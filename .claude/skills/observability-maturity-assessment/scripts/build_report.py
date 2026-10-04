#!/usr/bin/env python3
"""評価者が作成した assessment.json から、成熟度評価レポート（Markdown 下書き）を生成する。

- レベル定義・具体例・改善アクションの本文は CSV（成熟度モデルの唯一の正）から引用する。
  評価者（Claude / 人間）が書くのは「判定・根拠・ギャップ・未検証事項」だけで、
  モデル本文を言い換えることはしない。
- 入力スキーマは references/assessment-schema.md を参照。

使い方:
  python3 build_report.py assessment.json --out report.md [--evidence evidence.json] [--csv-dir ../../../csv]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from omm_model import Axis, Model, load_model  # noqa: E402

CONFIDENCE_JA = {"high": "高", "medium": "中", "low": "低"}
CONFIDENCE_DESC = {
    "high": "設定・コード・運用記録など複数種類の一次証跡が揃い、レベル定義の主要要件を直接確認できた",
    "medium": "一次証跡はあるが一部要件は文書への言及のみ、または運用実態の確認が必要",
    "low": "証跡が乏しく、主に推定。ヒアリングで確定が必要",
}


def bar(level: Optional[int]) -> str:
    if not level:
        return "○○○○○"
    return "●" * level + "○" * (5 - level)


def esc(s: str) -> str:
    return (s or "").replace("|", "\\|").replace("\n", " ")


def q(text: str) -> str:
    """引用ブロック化。"""
    return "\n".join("> " + line for line in (text or "").splitlines()) or "> —"


def validate(assessment: dict, model: Model) -> List[str]:
    problems: List[str] = []
    axes = assessment.get("axes", {})
    for a in model.axes:
        if a.key not in axes:
            problems.append(f"{a.key} {a.name}: 評価がありません（未評価として出力します）")
            continue
        ax = axes[a.key]
        lv = ax.get("level")
        if lv is not None and (not isinstance(lv, int) or not 1 <= lv <= 5):
            problems.append(f"{a.key}: level は 1〜5 の整数、または null（未評価）である必要があります: {lv!r}")
        conf = ax.get("confidence")
        if lv is not None and conf not in CONFIDENCE_JA:
            problems.append(f"{a.key}: confidence は high/medium/low のいずれか: {conf!r}")
        if lv is not None and not ax.get("rationale"):
            problems.append(f"{a.key}: rationale（判定理由）が空です")
        if lv is not None and not ax.get("evidence"):
            problems.append(f"{a.key}: evidence（証跡）が空です。証跡なしの判定は confidence=low にしてください")
    unknown = [k for k in axes if model.axis_by_key(k) is None]
    if unknown:
        problems.append(f"モデルに存在しない軸キー: {unknown}")
    return problems


def render_evidence(items: List) -> List[str]:
    out = []
    for e in items or []:
        if isinstance(e, str):
            out.append(f"- {e}")
        else:
            ref = e.get("ref") or e.get("file") or ""
            if e.get("line") and ":" not in str(ref):
                ref = f"{ref}:{e['line']}"
            note = e.get("note", "")
            out.append(f"- `{ref}` — {note}" if ref else f"- {note}")
    return out or ["- （証跡なし）"]


def render_list(items: List[str], empty: str = "- （なし）") -> List[str]:
    return [f"- {i}" for i in items] if items else [empty]


def render_axis(a: Axis, ax: Optional[dict], model: Model, default_questions: Dict[str, List[str]]) -> List[str]:
    out: List[str] = []
    out.append(f"### {a.key}. {a.name}")
    out.append("")
    out.append(f"**能力の定義**: {a.definition}")
    if a.note:
        out.append("")
        out.append(f"{a.note}")
    out.append("")
    if not ax or ax.get("level") is None:
        out.append("**暫定レベル**: 未評価")
        out.append("")
        if ax and ax.get("rationale"):
            out.append(ax["rationale"])
            out.append("")
        out.append("#### ヒアリングで確認すべき事項")
        out.extend(render_list(default_questions.get(a.key, [])))
        out.append("")
        return out

    lv = int(ax["level"])
    conf = ax.get("confidence", "low")
    out.append(f"**暫定レベル**: レベル{lv}（{model.level_name(lv)}） {bar(lv)}  **確信度**: {CONFIDENCE_JA.get(conf, conf)}")
    out.append("")
    out.append(f"#### モデル上のレベル{lv}の状態")
    out.append(q(a.levels[lv].description))
    out.append("")
    out.append("#### 判定理由")
    out.append(ax.get("rationale", ""))
    out.append("")
    out.append("#### 証跡")
    out.extend(render_evidence(ax.get("evidence", [])))
    out.append("")
    if lv < 5:
        nxt = a.levels[lv + 1]
        out.append(f"#### 次のレベル{lv + 1}（{model.level_name(lv + 1)}）の状態")
        out.append(q(nxt.description))
        out.append("")
        out.append("#### 次のレベルとのギャップ")
        out.extend(render_list(ax.get("gaps", []), "- （評価者による記載なし）"))
        out.append("")
    out.append("#### リポジトリからは確認できない事項（ヒアリングで確定）")
    out.extend(render_list(ax.get("unverified", []), "- （記載なし）"))
    out.append("")
    out.append("#### ヒアリング質問")
    questions = ax.get("questions") or default_questions.get(a.key, [])
    out.extend(render_list(questions))
    out.append("")
    if lv < 5:
        t = a.transitions.get((lv, lv + 1))
        if t:
            out.append(f"#### レベル{lv}→レベル{lv + 1} の改善アクションプラン（モデルより）")
            out.append("")
            out.append(f"- **改善アクション（必須）**: {t.improvement}")
            out.append(f"- **活用アクション（推奨）**: {t.leverage}")
            out.append(f"- **注意点メモ**: {t.notes}")
            out.append("")
    return out


def render_report(assessment: dict, model: Model, evidence: Optional[dict], default_questions: Dict[str, List[str]]) -> str:
    tgt = assessment.get("target", {})
    name = tgt.get("name") or tgt.get("url") or tgt.get("path") or "（対象未記載）"
    date = assessment.get("assessed_at") or dt.date.today().isoformat()
    out: List[str] = []
    out.append(f"# オブザーバビリティ成熟度評価（下書き）: {name}")
    out.append("")
    out.append("> **この文書は下書きです。** リポジトリ内の成果物（設定・コード・文書）を証跡として暫定レベルを置いています。"
               "成熟度モデルの多くの要件は組織・プロセスの運用実態に関するもので、リポジトリだけでは確認できません。"
               "各軸の「ヒアリング質問」への回答を得てから最終評価としてください。")
    out.append("")
    out.append("## 評価対象")
    out.append("")
    out.append("| 項目 | 内容 |")
    out.append("|---|---|")
    out.append(f"| 対象 | {esc(name)} |")
    if tgt.get("url"):
        out.append(f"| URL | {esc(tgt['url'])} |")
    if tgt.get("commit"):
        out.append(f"| コミット | `{tgt['commit']}`" + (f" ({tgt.get('branch')})" if tgt.get("branch") else "") + " |")
    out.append(f"| 評価日 | {date} |")
    out.append(f"| 評価者 | {esc(assessment.get('assessor', 'Claude Code（observability-maturity-assessment スキル）'))} |")
    if assessment.get("scope"):
        out.append(f"| 範囲・前提 | {esc(assessment['scope'])} |")
    out.append("")

    out.append("## サマリ")
    out.append("")
    out.append("| 評価軸 | 暫定レベル | | 確信度 | 次のレベル |")
    out.append("|---|---|---|---|---|")
    levels: List[int] = []
    for a in model.axes:
        ax = assessment.get("axes", {}).get(a.key)
        if not ax or ax.get("level") is None:
            out.append(f"| {a.key}. {a.name} | 未評価 | {bar(None)} | — | — |")
            continue
        lv = int(ax["level"])
        levels.append(lv)
        nxt = f"レベル{lv + 1}（{model.level_name(lv + 1)}）" if lv < 5 else "—（最高レベル）"
        out.append(f"| {a.key}. {a.name} | レベル{lv}（{model.level_name(lv)}） | {bar(lv)} | {CONFIDENCE_JA.get(ax.get('confidence'), '—')} | {nxt} |")
    out.append("")
    if levels:
        out.append(f"- 評価済み {len(levels)}/{len(model.axes)} 軸 / 最低レベル {min(levels)} / 最高レベル {max(levels)}（レベルは軸ごとに独立で、平均値は成熟度の指標として用いません）")
        out.append("")
    if assessment.get("summary"):
        out.append("### 総評")
        out.append("")
        out.append(assessment["summary"])
        out.append("")
    if assessment.get("priorities"):
        out.append("### 優先して取り組むテーマ（提案）")
        out.append("")
        for i, p in enumerate(assessment["priorities"], 1):
            if isinstance(p, str):
                out.append(f"{i}. {p}")
            else:
                ax_name = ""
                a = model.axis_by_key(p.get("axis", "")) if p.get("axis") else None
                if a:
                    ax_name = f"[{a.key} {a.name}] "
                out.append(f"{i}. {ax_name}**{p.get('theme', '')}** — {p.get('reason', '')}")
        out.append("")

    out.append("## 軸別の評価")
    out.append("")
    for a in model.axes:
        out.extend(render_axis(a, assessment.get("axes", {}).get(a.key), model, default_questions))

    out.append("## 付録A. 評価方法と限界")
    out.append("")
    out.append("1. 対象リポジトリを `scan_repo.py` で走査し、6 評価軸に関する成果物（設定・コード・依存・文書）の有無と所在を収集した。")
    out.append("2. 収集した証跡を成熟度モデルの各レベル定義と照合し、**レベル定義の主要要件が証跡で直接確認できる最高のレベル**を暫定レベルとした。上位レベルの成果物が一部あるだけでは、そのレベルとは判定していない。")
    out.append("3. 文書への言及のみの証跡は弱い証跡として扱い、設定・コード・運用記録による裏付けがない場合は確信度を下げた。")
    out.append("4. 組織標準化（レベル3）以上の判定には「全プロジェクトで一貫して適用されている」ことの確認が必要で、単一リポジトリからは原則確認できない。該当する判定は確信度『中』以下とし、ヒアリング質問を付した。")
    out.append("")
    out.append("| 確信度 | 意味 |")
    out.append("|---|---|")
    for k in ("high", "medium", "low"):
        out.append(f"| {CONFIDENCE_JA[k]} | {CONFIDENCE_DESC[k]} |")
    out.append("")

    if evidence:
        out.append("## 付録B. 走査サマリ")
        out.append("")
        m = evidence.get("meta", {})
        out.append(f"- 走査日時: {evidence.get('scanned_at', '')} / ファイル数 {m.get('file_count', '?')}（本文走査 {m.get('text_files_scanned', '?')}）")
        if m.get("languages_top"):
            out.append("- 主要言語: " + ", ".join(f"{l} ({n})" for l, n in m["languages_top"]))
        for n in evidence.get("notes", []):
            out.append(f"- ⚠️ {n}")
        out.append("")
        out.append("| 評価軸 | ヒット（シグナル数） | 証跡のある hint レベル | 文書以外の証跡があるレベル |")
        out.append("|---|---|---|---|")
        for k, ax in evidence.get("axes", {}).items():
            out.append(f"| {k}. {ax['name']} | {len(ax['signals_hit'])}/{ax['signals_total']} | {ax.get('hint_levels_with_evidence') or '—'} | {ax.get('strong_hint_levels') or '—'} |")
        out.append("")
        out.append("詳細は同時に生成した `evidence-summary.md` / `evidence.json` を参照。")
        out.append("")

    out.append("## 出典・ライセンス")
    out.append("")
    out.append("本評価の成熟度レベル定義・具体例・改善アクションプランの本文は、DMM.com LLC が "
               "[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) で公開する"
               "[オブザーバビリティ成熟度モデル](https://github.com/dmm-com/observability-maturity-model) から引用しています。"
               "評価・判定部分は評価者の見解であり、モデル著作者の見解ではありません。")
    out.append("")
    return "\n".join(out)


def load_default_questions(model: Model) -> Dict[str, List[str]]:
    """references/interview-questions.md から軸ごとの既定質問を読む（見出し `## A1.` 配下の `- ` 行）。"""
    path = Path(__file__).resolve().parent.parent / "references" / "interview-questions.md"
    result: Dict[str, List[str]] = {a.key: [] for a in model.axes}
    if not path.is_file():
        return result
    current = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            key = line[3:].split(".", 1)[0].strip()
            current = key if key in result else None
        elif current and line.startswith("- "):
            result[current].append(line[2:].strip())
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("assessment", help="評価者が作成した assessment.json")
    ap.add_argument("--out", default="observability-maturity-assessment.md")
    ap.add_argument("--evidence", help="scan_repo.py が出力した evidence.json（付録に走査サマリを載せる）")
    ap.add_argument("--csv-dir", help="成熟度モデル CSV のディレクトリ（省略時は自動解決）")
    ap.add_argument("--strict", action="store_true", help="入力の問題を警告ではなくエラー（exit 1）にする")
    args = ap.parse_args()

    model = load_model(args.csv_dir)
    assessment = json.loads(Path(args.assessment).read_text(encoding="utf-8"))
    problems = validate(assessment, model)
    for p in problems:
        print(f"[warn] {p}", file=sys.stderr)
    if problems and args.strict:
        return 1
    evidence = json.loads(Path(args.evidence).read_text(encoding="utf-8")) if args.evidence else None
    report = render_report(assessment, model, evidence, load_default_questions(model))
    Path(args.out).write_text(report, encoding="utf-8")
    print(f"レポートを生成しました: {args.out}" + (f"（警告 {len(problems)} 件）" if problems else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
