#!/usr/bin/env python3
"""CSV（唯一の正）から閲覧用 Markdown（docs/）を生成し、スキル同梱の CSV コピーを同期する。

生成物:
  docs/model/index.md                 名称定義・CMMI レベル・6 軸 × 5 レベルの一覧表
  docs/model/<axis-slug>.md           軸別ページ: 定義 → レベル1〜5（説明・具体例）→ 各レベル間の改善アクション
  docs/levels/level-<n>.md            レベル別ページ: 全軸のそのレベルの状態を横断で読む
  .claude/skills/observability-maturity-assessment/references/csv/*.csv   スキル同梱コピー

使い方:
  python3 tools/build_docs.py          # 生成・同期
  python3 tools/build_docs.py --check  # 生成結果と差分があれば exit 1（CI 用）
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / ".claude" / "skills" / "observability-maturity-assessment"
sys.path.insert(0, str(SKILL / "scripts"))
from omm_model import ACTION_CSV, MODEL_CSV, Axis, Model, load_model  # noqa: E402

DOCS = REPO / "docs"
GENERATED_NOTE = (
    "<!-- このファイルは tools/build_docs.py が csv/ から生成しています。直接編集せず CSV を編集してください。 -->"
)


def front_matter(**kv: object) -> str:
    lines = ["---"]
    for k, v in kv.items():
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
            "**説明**",
            "",
            lv.description,
            "",
            "**具体例**",
            "",
            lv.example,
            "",
        ]
        if n < 5:
            t = a.transitions.get((n, n + 1))
            out += [anchor(f"transition-{n}-{n + 1}"), f"### レベル{n}→レベル{n + 1} に進むには", ""]
            if t:
                out += [
                    f"**改善アクション（必須）**: {t.improvement}",
                    "",
                    f"**活用アクション（推奨）**: {t.leverage}",
                    "",
                    f"> **注意点メモ**: {t.notes}",
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
        front_matter(title="レベル別ビュー", nav_order=3, has_children=True, permalink="/levels/"),
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
            lv.description,
            "",
            f"**具体例**: {lv.example}",
            "",
        ]
        if n < 5:
            t = a.transitions.get((n, n + 1))
            if t:
                out += [f"**レベル{n + 1} へ進むための改善アクション（必須）**: {t.improvement} （[活用アクション・注意点](../model/{a.slug}.md#transition-{n}-{n + 1})）", ""]
    nav = []
    if n > 1:
        nav.append(f"← [レベル{n - 1}](level-{n - 1}.md)")
    nav.append("[レベル別ビュー](index.md)")
    if n < 5:
        nav.append(f"[レベル{n + 1}](level-{n + 1}.md) →")
    out += ["---", "", " | ".join(nav), ""]
    return "\n".join(out) + "\n"


def planned_outputs(model: Model) -> Dict[Path, str]:
    files: Dict[Path, str] = {DOCS / "model" / "index.md": gen_model_index(model)}
    for a in model.axes:
        files[DOCS / "model" / f"{a.slug}.md"] = gen_axis_page(model, a)
    files[DOCS / "levels" / "index.md"] = gen_levels_index(model)
    for n in range(1, 6):
        files[DOCS / "levels" / f"level-{n}.md"] = gen_level_page(model, n)
    return files


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="差分があれば exit 1（書き込みはしない）")
    args = ap.parse_args()

    model = load_model(str(REPO / "csv"))
    outputs = planned_outputs(model)
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
    print(f"生成: {len(outputs)} ファイル（docs/model, docs/levels）, 同期: {len(csv_sync)} CSV → {SKILL.relative_to(REPO)}/references/csv/")
    if stale:
        print("更新されたファイル:")
        for p in stale:
            print(f"  - {p.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
