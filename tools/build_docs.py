#!/usr/bin/env python3
"""CSV（唯一の正）から閲覧用 Markdown（docs/）を生成し、スキル同梱の CSV コピーを同期する。

生成物:
  docs/model/index.md                 名称定義・CMMI レベル・6 軸 × 5 レベルの一覧表
  docs/model/<axis-slug>.md           軸別ページ: 定義 → レベル1〜5（説明・具体例）→ 各レベル間の改善アクション
  docs/levels/level-<n>.md            レベル別ページ: 全軸のそのレベルの状態を横断で読む
  docs/matrix.md                      全量マトリクス: 6 軸 × 5 レベルの説明・具体例と改善アクションを 1 枚で
  docs/self-assessment.md             個人評価: セルを選択して自己評価（状態は localStorage、集計をページ内表示）
  .claude/skills/observability-maturity-assessment/references/csv/*.csv   スキル同梱コピー

使い方:
  python3 tools/build_docs.py          # 生成・同期
  python3 tools/build_docs.py --check  # 生成結果と差分があれば exit 1（CI 用）
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / ".claude" / "skills" / "observability-maturity-assessment"
sys.path.insert(0, str(SKILL / "scripts"))
from omm_model import ACTION_CSV, MODEL_CSV, Axis, Model, load_model, to_dict  # noqa: E402

DOCS = REPO / "docs"
GENERATED_NOTE = (
    "<!-- このファイルは tools/build_docs.py が csv/ から生成しています。直接編集せず CSV を編集してください。 -->"
)


FRONT_MATTER_KEYS = ("title", "description", "titleTemplate", "aside", "outline")  # VitePress が解釈するキーだけを出力


def front_matter(**kv: object) -> str:
    lines = ["---"]
    for k, v in kv.items():
        if k not in FRONT_MATTER_KEYS:
            continue  # nav_order / parent / permalink などサイトジェネレータ固有のキーは出力しない（並び順は .vitepress/config.ts）
        if isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, int):
            lines.append(f"{k}: {v}")
        else:
            s = str(v).replace('"', '\\"')
            lines.append(f'{k}: "{s}"')
    lines.append("---")
    return "\n".join(lines)


def anchor(id_: str) -> str:
    # GitHub と Jekyll(kramdown) の両方で機能する明示アンカー
    return f'<a id="{id_}"></a>'


def level_label(model: Model, n: int) -> str:
    return f"レベル{n}: {model.level_name(n)}"


def block(kind: str, title: str, body: str, caption: str = "", extra_html: str = "") -> str:
    """説明 / 具体例 / 改善アクション / 活用アクション / 注意点メモ を視覚的に区別するブロック（スタイルは .vitepress/theme/style.css）。

    kind: desc | example | required | recommended | note。1 行の HTML にして markdown-it の HTML ブロックとして扱わせる。
    """
    cap = f"<span>{html.escape(caption)}</span>" if caption else ""
    tail = f'<p class="omm-block-more">{extra_html}</p>' if extra_html else ""
    return (
        f'<div class="omm-block omm-{kind}"><p class="omm-block-title">{html.escape(title)}{cap}</p>'
        f"<p>{html.escape(body)}</p>{tail}</div>"
    )


def gen_model_index(model: Model) -> str:
    out: List[str] = [
        front_matter(title="成熟度モデル", nav_order=2, has_children=True, permalink="/model/"),
        GENERATED_NOTE,
        "",
        f"# {model.title}",
        "",
        "組織のオブザーバビリティ能力を 6 つの評価軸で測定するための評価基準です。各軸はレベル1（属人的）からレベル5（継続的最適化）までの状態を定義しています。",
        "",
        "## 名称定義",
        "",
    ]
    for t in model.terms:
        out.append(f"- **{t.name}**: {t.definition}")
    out += ["", "## 成熟度レベル（CMMI に基づく 5 段階）", "", "| レベル | 名称 | 説明 |", "|---|---|---|"]
    for l in model.cmmi_levels:
        out.append(f"| [レベル{l.level}](../levels/level-{l.level}.md) | {l.name} | {l.description} |")
    out += [
        "",
        "## 評価軸",
        "",
        "各軸のページでは、レベルごとの「説明」「具体例」と、次のレベルへ進むための「改善アクション（必須）」「活用アクション（推奨）」「注意点メモ」を続けて読めます。",
        "",
    ]
    for a in model.axes:
        out.append(f"### {a.key}. [{a.name}]({a.slug}.md)")
        out.append("")
        out.append(a.definition)
        if a.note:
            out.append("")
            out.append(a.note)
        out.append("")
    out += ["## レベル一覧（6 軸 × 5 レベル）", "", "セルをクリックすると各軸ページの該当レベルに移動します。", ""]
    header = "| 評価軸 | " + " | ".join(f"L{n} {model.level_name(n)}" for n in range(1, 6)) + " |"
    out.append(header)
    out.append("|---|" + "---|" * 5)
    for a in model.axes:
        cells = []
        for n in range(1, 6):
            desc = a.levels[n].description
            short = desc[:28] + ("…" if len(desc) > 28 else "")
            cells.append(f"[{short}]({a.slug}.md#level-{n})")
        out.append(f"| [{a.name}]({a.slug}.md) | " + " | ".join(cells) + " |")
    out += [
        "",
        "## 横断ビュー",
        "",
        "「いま組織全体がレベル2なら、レベル3とはどんな状態か」を軸をまたいで読みたいときは [レベル別ページ](../levels/) を使ってください。",
        "",
    ]
    return "\n".join(out) + "\n"


def gen_axis_page(model: Model, a: Axis) -> str:
    out: List[str] = [
        front_matter(title=a.name, parent="成熟度モデル", nav_order=a.index),
        GENERATED_NOTE,
        "",
        f"# {a.key}. {a.name}",
        "",
        f"**能力の定義**: {a.definition}",
    ]
    if a.note:
        out += ["", a.note]
    out += ["", "## レベル一覧", "", "| レベル | 名称 | 説明 |", "|---|---|---|"]
    for n in range(1, 6):
        out.append(f"| [レベル{n}](#level-{n}) | {model.level_name(n)} | {a.levels[n].description} |")
    out.append("")
    for n in range(1, 6):
        lv = a.levels[n]
        out += [
            anchor(f"level-{n}"),
            f"## {level_label(model, n)}",
            "",
            block("desc", "説明", lv.description, "このレベルにある組織・チームの状態"),
            "",
            block("example", "具体例", lv.example, "状態を具体化した例。自組織の実態と照らし合わせる"),
            "",
        ]
        if n < 5:
            t = a.transitions.get((n, n + 1))
            out += [anchor(f"transition-{n}-{n + 1}"), f"### レベル{n}→レベル{n + 1} に進むには", ""]
            if t:
                out += [
                    block("required", "改善アクション", t.improvement, "必須 — 次のレベルに進むための最小限の実施事項"),
                    "",
                    block("recommended", "活用アクション", t.leverage, "推奨 — 改善アクションの実効性を高め、次のレベルでの成功確率を上げる施策"),
                    "",
                    block("note", "注意点メモ", t.notes, "実施時に注意すべき点、誤解しやすい点"),
                    "",
                ]
            else:
                out += ["（改善アクションプラン未定義）", ""]
    nav = []
    if a.index > 1:
        prev = model.axes[a.index - 2]
        nav.append(f"← [{prev.key}. {prev.name}]({prev.slug}.md)")
    nav.append("[成熟度モデルの一覧](index.md)")
    if a.index < len(model.axes):
        nxt = model.axes[a.index]
        nav.append(f"[{nxt.key}. {nxt.name}]({nxt.slug}.md) →")
    out += ["---", "", " | ".join(nav), ""]
    return "\n".join(out) + "\n"


def gen_levels_index(model: Model) -> str:
    out = [
        front_matter(title="レベル別ビュー", nav_order=4, has_children=True, permalink="/levels/"),
        GENERATED_NOTE,
        "",
        "# レベル別ビュー",
        "",
        "各レベルについて、6 つの評価軸がどのような状態にあるかを横断で読むためのページです。「次のレベルの全体像」を掴むときに使います。軸ごとの詳細と改善アクションは[成熟度モデル](../model/)の各軸ページを参照してください。",
        "",
        "| レベル | 名称 | 説明 |",
        "|---|---|---|",
    ]
    for l in model.cmmi_levels:
        out.append(f"| [レベル{l.level}](level-{l.level}.md) | {l.name} | {l.description} |")
    out.append("")
    return "\n".join(out) + "\n"


def gen_level_page(model: Model, n: int) -> str:
    cm = next(l for l in model.cmmi_levels if l.level == n)
    out = [
        front_matter(title=f"レベル{n}: {cm.name}", parent="レベル別ビュー", nav_order=n),
        GENERATED_NOTE,
        "",
        f"# レベル{n}: {cm.name}",
        "",
        f"> **CMMI 上の定義**: {cm.description}",
        "",
    ]
    for a in model.axes:
        lv = a.levels[n]
        out += [
            f"## {a.key}. [{a.name}](../model/{a.slug}.md#level-{n})",
            "",
            block("desc", "説明", lv.description),
            "",
            block("example", "具体例", lv.example),
            "",
        ]
        if n < 5:
            t = a.transitions.get((n, n + 1))
            if t:
                more = f'<a href="../model/{a.slug}.html#transition-{n}-{n + 1}">活用アクション・注意点メモ →</a>'
                out += [block("required", f"レベル{n + 1} へ進むための改善アクション", t.improvement, "必須", more), ""]
    nav = []
    if n > 1:
        nav.append(f"← [レベル{n - 1}](level-{n - 1}.md)")
    nav.append("[レベル別ビュー](index.md)")
    if n < 5:
        nav.append(f"[レベル{n + 1}](level-{n + 1}.md) →")
    out += ["---", "", " | ".join(nav), ""]
    return "\n".join(out) + "\n"


def _h(s: str) -> str:
    return html.escape(s or "", quote=True)


def _axis_head_cell(a: Axis) -> str:
    note = f'<div class="omm-note">{_h(a.note)}</div>' if a.note else ""
    return (
        f'<th scope="row" class="omm-axis"><a href="model/{a.slug}.html">{a.key}. {_h(a.name)}</a>'
        f'<div class="omm-def">{_h(a.definition)}</div>{note}</th>'
    )


def gen_matrix_page(model: Model) -> str:
    """6 軸 × 5 レベルの全量を 1 枚で確認するマトリクス（説明 + 折りたたみの具体例）と、改善アクションのマトリクス。"""
    out: List[str] = [
        front_matter(
            title="全量マトリクス",
            description="6 つの評価軸を縦軸、成熟度レベル1〜5 を横軸に、全セルの説明と具体例、レベル間の改善アクションを 1 枚の表で見渡します。",
            aside=False,
            outline=False,
        ),
        GENERATED_NOTE,
        "",
        "# 全量マトリクス",
        "",
        "縦軸に評価軸、横軸に成熟度レベルを取り、全セルの「説明」を 1 枚で確認できる表です。「具体例」はセル内で展開します。表は縦横にスクロールでき、見出し行と評価軸の列は固定されます。表が広いときは、左の目次の上にあるボタンで目次をコンパクト表示にできます。",
        "",
        '<p class="omm-toolbar"><button type="button" class="omm-button omm-expand" data-target=".omm-matrix-levels" data-open="true">具体例をすべて開く</button> <button type="button" class="omm-button omm-expand" data-target=".omm-matrix-levels" data-open="false">すべて閉じる</button></p>',
        "",
        "## 成熟度レベル定義",
        "",
        '<div class="omm-matrix-wrap"><table class="omm-matrix omm-matrix-levels">',
        "<thead><tr><th>評価軸</th>"
        + "".join(f'<th>L{n}<br><span class="omm-lv-name">{_h(model.level_name(n))}</span></th>' for n in range(1, 6))
        + "</tr></thead>",
        "<tbody>",
    ]
    for a in model.axes:
        cells = []
        for n in range(1, 6):
            lv = a.levels[n]
            cells.append(
                f'<td><p class="omm-desc">{_h(lv.description)}</p>'
                f'<details><summary>具体例</summary><p>{_h(lv.example)}</p></details>'
                f'<a class="omm-more" href="model/{a.slug}.html#level-{n}">詳細 →</a></td>'
            )
        out.append(f"<tr>{_axis_head_cell(a)}{''.join(cells)}</tr>")
    out += [
        "</tbody></table></div>",
        "",
        "## 改善アクションプラン",
        "",
        "各セルは「改善アクション（必須）」を表示し、「活用アクション（推奨）」「注意点メモ」はセル内で展開します。",
        "",
        '<p class="omm-toolbar"><button type="button" class="omm-button omm-expand" data-target=".omm-matrix-actions" data-open="true">活用アクション・注意点をすべて開く</button> <button type="button" class="omm-button omm-expand" data-target=".omm-matrix-actions" data-open="false">すべて閉じる</button></p>',
        "",
        '<div class="omm-matrix-wrap"><table class="omm-matrix omm-matrix-actions">',
        "<thead><tr><th>評価軸</th>"
        + "".join(f"<th>L{n}→L{n + 1}</th>" for n in range(1, 5))
        + "</tr></thead>",
        "<tbody>",
    ]
    for a in model.axes:
        cells = []
        for n in range(1, 5):
            t = a.transitions.get((n, n + 1))
            if not t:
                cells.append("<td>—</td>")
                continue
            cells.append(
                f'<td><p class="omm-desc"><strong>改善（必須）</strong> {_h(t.improvement)}</p>'
                f'<details><summary>活用アクション（推奨）</summary><p>{_h(t.leverage)}</p></details>'
                f'<details><summary>注意点メモ</summary><p>{_h(t.notes)}</p></details>'
                f'<a class="omm-more" href="model/{a.slug}.html#transition-{n}-{n + 1}">詳細 →</a></td>'
            )
        out.append(f"<tr>{_axis_head_cell(a)}{''.join(cells)}</tr>")
    out += [
        "</tbody></table></div>",
        "",
        "関連: [個人評価](self-assessment.md)（このマトリクス上でレベルを選択して集計） / [成熟度モデル](model/index.md) / [レベル別ビュー](levels/index.md)",
        "",
    ]
    return "\n".join(out) + "\n"


def gen_self_assessment_page(model: Model) -> str:
    """セルを選択して自己評価を行うページ。状態は localStorage に保存し、集計をページ内に表示する（assets/js/omm-self-assessment.js）。"""
    level_names = ",".join(f'"{n}":"{_h(model.level_name(n))}"' for n in range(1, 6))
    out: List[str] = [
        front_matter(
            title="個人評価",
            description="6 つの評価軸について、マトリクス上でレベルを選択して自己評価を記録し、集計をページ内で確認します。記録はブラウザの localStorage にだけ保存されます。",
            aside=False,
            outline=False,
        ),
        GENERATED_NOTE,
        "",
        "# 個人評価",
        "",
        "各評価軸について、現状に最も近いレベルのセルをクリックして選択してください。選択内容はこのブラウザの localStorage に保存され、ページを閉じても保持されます（サーバには送信されません）。集計は選択のたびに上の「自己評価の記録と集計」に反映されます。",
        "",
        "判定の目安は [評価の進め方](assessment/index.md) を参照してください。レベルは「そのレベルの定義を証跡で示せる最高のレベル」とし、上位の取り組みが一部あるだけでは上げないのが原則です。",
        "",
        "<ClientOnly><MatrixAssessment /></ClientOnly>",
        "",
        '<p class="omm-toolbar"><button type="button" class="omm-button omm-expand" data-target=".omm-sa-table" data-open="true">具体例をすべて開く</button> <button type="button" class="omm-button omm-expand" data-target=".omm-sa-table" data-open="false">すべて閉じる</button></p>',
        "",
        '<div class="omm-matrix-wrap"><table class="omm-matrix omm-sa-table" data-level-names=\'{' + level_names + "}'>",
        "<thead><tr><th>評価軸</th>"
        + "".join(f'<th>L{n}<br><span class="omm-lv-name">{_h(model.level_name(n))}</span></th>' for n in range(1, 6))
        + "<th>対象外</th></tr></thead>",
        "<tbody>",
    ]
    for a in model.axes:
        cells = []
        for n in range(1, 6):
            lv = a.levels[n]
            cells.append(
                f'<td class="omm-sa-cell" data-level="{n}" role="radio" aria-checked="false" tabindex="0" '
                f'aria-label="{_h(a.name)} レベル{n}">'
                f'<span class="omm-sa-badge">L{n}</span>'
                f'<p class="omm-desc">{_h(lv.description)}</p>'
                f'<details><summary>具体例</summary><p>{_h(lv.example)}</p></details></td>'
            )
        cells.append(
            f'<td class="omm-sa-cell omm-sa-na" data-level="0" role="radio" aria-checked="false" tabindex="0" '
            f'aria-label="{_h(a.name)} 対象外"><span class="omm-sa-badge">—</span><p class="omm-desc">対象外 / 未評価</p></td>'
        )
        out.append(
            f'<tr data-axis="{a.key}" data-axis-name="{_h(a.name)}" data-axis-slug="{a.slug}">'
            f"{_axis_head_cell(a)}{''.join(cells)}</tr>"
        )
    out += [
        "</tbody></table></div>",
        "",
        "## 使い方の補足",
        "",
        "- 選択はセルのクリックまたはキーボード（Enter / Space）で行えます。同じセルをもう一度クリックすると選択を解除します。",
        "- 「集計を Markdown でコピー」は、[評価レポートテンプレート](assessment/report-template.md) のサマリ表に貼り付けられる形式です。",
        "- 別の端末・ブラウザには引き継がれません。チームで共有する場合はコピーした Markdown を使ってください。",
        "",
    ]
    return "\n".join(out) + "\n"


def planned_outputs(model: Model) -> Dict[Path, str]:
    files: Dict[Path, str] = {DOCS / "model" / "index.md": gen_model_index(model)}
    for a in model.axes:
        files[DOCS / "model" / f"{a.slug}.md"] = gen_axis_page(model, a)
    files[DOCS / "levels" / "index.md"] = gen_levels_index(model)
    for n in range(1, 6):
        files[DOCS / "levels" / f"level-{n}.md"] = gen_level_page(model, n)
    files[DOCS / "matrix.md"] = gen_matrix_page(model)
    files[DOCS / "self-assessment.md"] = gen_self_assessment_page(model)
    return files


DOWNLOADS = DOCS / "public" / "downloads"
DOWNLOAD_FILES = [
    # (配布名, 元ファイル, 表示名, 説明)
    ("observability-maturity-model.pdf", REPO / "pdf" / "observability-maturity-model.pdf", "成熟度モデル（PDF）", "6 つの評価軸について、レベル1〜5 の状態と具体例"),
    ("improvement-action-plan.pdf", REPO / "pdf" / "improvement-action-plan.pdf", "改善アクションプラン（PDF）", "各レベルから次のレベルへ進むための改善・活用アクションと注意点"),
    ("observability-maturity-model.csv", REPO / "csv" / MODEL_CSV, "成熟度モデル（CSV）", "編集・カスタマイズ用の元データ（唯一の正）"),
    ("improvement-action-plan.csv", REPO / "csv" / ACTION_CSV, "改善アクションプラン（CSV）", "編集・カスタマイズ用の元データ（唯一の正）"),
]


def model_json(model: Model) -> str:
    return json.dumps(to_dict(model), ensure_ascii=False, indent=2) + "\n"


def build_downloads(model: Model) -> int:
    """csv/ と pdf/ を docs/public/downloads/ に複製し、JSON と manifest.json を書く（gitignore 対象のビルド成果物）。"""
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    files = []
    for name, src, title, desc in DOWNLOAD_FILES:
        data = src.read_bytes()
        (DOWNLOADS / name).write_bytes(data)
        files.append({"name": name, "title": title, "description": desc, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    data = model_json(model).encode("utf-8")
    (DOWNLOADS / "observability-maturity-model.json").write_bytes(data)
    files.append({"name": "observability-maturity-model.json", "title": "成熟度モデル + 改善アクションプラン（JSON）", "description": "評価軸・レベル定義・具体例・改善アクションを 1 ファイルにまとめた機械可読形式", "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    try:
        commit = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True, check=False).stdout.strip() or "unknown"
    except OSError:
        commit = "unknown"
    manifest = {"generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "commit": commit, "files": files}
    (DOWNLOADS / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(files)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="差分があれば exit 1（書き込みはしない）")
    ap.add_argument("--downloads", action="store_true", help="docs/public/downloads/ だけを生成する（ビルド成果物。差分チェック対象外）")
    args = ap.parse_args()

    model = load_model(str(REPO / "csv"))
    if args.downloads:
        n = build_downloads(model)
        print(f"ダウンロード用ファイル {n} 件 + manifest.json → {DOWNLOADS.relative_to(REPO)}/")
        return 0

    outputs = planned_outputs(model)
    outputs[REPO / "build" / "model.json"] = model_json(model)  # .vitepress/config.ts がサイドバー生成に読む
    csv_sync = {
        SKILL / "references" / "csv" / name: (REPO / "csv" / name).read_bytes() for name in (MODEL_CSV, ACTION_CSV)
    }

    stale: List[Path] = []
    for path, content in outputs.items():
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            stale.append(path)
    for path, data in csv_sync.items():
        if not path.exists() or path.read_bytes() != data:
            stale.append(path)

    if args.check:
        if stale:
            print("生成物が CSV と同期していません。`python3 tools/build_docs.py` を実行してください:")
            for p in stale:
                print(f"  - {p.relative_to(REPO)}")
            return 1
        print(f"OK: 生成物 {len(outputs) + len(csv_sync)} 件は CSV と同期しています")
        return 0

    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    for path, data in csv_sync.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    n_dl = build_downloads(model)
    print(f"生成: {len(outputs)} ファイル（docs/model, docs/levels, docs/matrix.md, docs/self-assessment.md, build/model.json）, "
          f"同期: {len(csv_sync)} CSV → {SKILL.relative_to(REPO)}/references/csv/, ダウンロード {n_dl} 件 → docs/public/downloads/")
    if stale:
        print("更新されたファイル:")
        for p in stale:
            print(f"  - {p.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
