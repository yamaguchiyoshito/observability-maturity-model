#!/usr/bin/env python3
"""オブザーバビリティ成熟度モデル CSV の共通パーサ。

リポジトリの `csv/` にある 2 本の CSV（成熟度モデル / 改善アクションプラン）を
構造化データに変換する。標準ライブラリのみ依存。

- docs 生成 (`tools/build_docs.py`) と評価レポート生成 (`scripts/build_report.py`) の両方が
  このモジュールを使う。CSV が唯一の正（SSoT）であり、ここでは内容を一切書き換えない。
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

MODEL_CSV = "observability-maturity-model.csv"
ACTION_CSV = "improvement-action-plan.csv"

# 評価軸名 → URL/ファイル名に使う英語スラッグ。未知の軸は axis-N にフォールバックする。
AXIS_SLUGS: Dict[str, str] = {
    "データ収集と可視化": "data-collection-and-visualization",
    "システムの信頼性管理": "system-reliability-management",
    "開発・運用プロセスの整備と最適化": "dev-ops-process-optimization",
    "アラート最適化と障害対応": "alert-optimization-and-incident-response",
    "ユーザー行動の理解と最適化": "user-behavior-understanding",
    "継続的な改善と最適化": "continuous-improvement",
}

LEVEL_RE = re.compile(r"レベル\s*(\d)")
TRANSITION_RE = re.compile(r"レベル\s*(\d)\s*→\s*レベル\s*(\d)")


@dataclass
class Term:
    name: str
    definition: str


@dataclass
class CmmiLevel:
    level: int
    name: str
    description: str


@dataclass
class LevelDef:
    level: int
    description: str
    example: str


@dataclass
class Transition:
    from_level: int
    to_level: int
    improvement: str  # 改善アクション（必須）
    leverage: str  # 活用アクション（推奨）
    notes: str  # 注意点メモ


@dataclass
class Axis:
    index: int  # 1 始まり
    name: str
    definition: str
    note: str = ""  # 「※」で始まる補足
    slug: str = ""
    levels: Dict[int, LevelDef] = field(default_factory=dict)
    transitions: Dict[Tuple[int, int], Transition] = field(default_factory=dict)

    @property
    def key(self) -> str:
        return f"A{self.index}"


@dataclass
class Model:
    title: str
    terms: List[Term]
    cmmi_levels: List[CmmiLevel]
    axes: List[Axis]
    action_title: str = ""
    action_terms: List[Term] = field(default_factory=list)

    def axis_by_name(self, name: str) -> Optional[Axis]:
        for a in self.axes:
            if a.name == name:
                return a
        return None

    def axis_by_key(self, key: str) -> Optional[Axis]:
        for a in self.axes:
            if a.key == key or a.slug == key:
                return a
        return None

    def level_name(self, level: int) -> str:
        for l in self.cmmi_levels:
            if l.level == level:
                return l.name
        return ""


def _read_csv(path: Path) -> List[List[str]]:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return [row for row in csv.reader(fh)]


def _split_lines(cell: str) -> List[str]:
    return [s.strip() for s in re.split(r"\r\n|\r|\n", cell) if s.strip()]


def _parse_terms(rows: List[List[str]], start: int, header_marker: str) -> Tuple[List[Term], int]:
    """『【名称定義】』以降、ヘッダ行までの「　・名前：定義」行を Term にする。ヘッダ行の index を返す。"""
    terms: List[Term] = []
    i = start
    while i < len(rows):
        first = rows[i][0].strip() if rows[i] else ""
        if first == header_marker:
            return terms, i
        m = re.match(r"^[・･]\s*([^：:]+)[：:](.*)$", first.lstrip("　 ").strip())
        if m:
            terms.append(Term(name=m.group(1).strip(), definition=m.group(2).strip()))
        i += 1
    raise ValueError(f"ヘッダ行 '{header_marker}' が見つかりません")


def parse_model_csv(path: Path) -> Model:
    rows = _read_csv(path)
    title = rows[0][0].strip()
    terms, header_idx = _parse_terms(rows, 1, "評価項目")

    cmmi: List[CmmiLevel] = []
    axes: List[Axis] = []
    current: Optional[Axis] = None
    in_cmmi = False

    for row in rows[header_idx + 1 :]:
        row = (row + [""] * 4)[:4]
        axis_cell, level_cell, desc, example = (c.strip() for c in row)
        if axis_cell:
            if "CMMI" in axis_cell or "能力成熟度" in axis_cell:
                in_cmmi = True
                current = None
            else:
                in_cmmi = False
                lines = _split_lines(axis_cell)
                name = lines[0]
                note_lines = [l for l in lines[1:] if l.startswith("※")]
                def_lines = [l for l in lines[1:] if not l.startswith("※")]
                current = Axis(
                    index=len(axes) + 1,
                    name=name,
                    definition=" ".join(def_lines),
                    note=" ".join(note_lines),
                    slug=AXIS_SLUGS.get(name, f"axis-{len(axes) + 1}"),
                )
                axes.append(current)
        m = LEVEL_RE.search(level_cell)
        if not m:
            continue
        level = int(m.group(1))
        if in_cmmi:
            name = level_cell.split(":", 1)[1].strip() if ":" in level_cell else level_cell
            name = name.split("：", 1)[-1].strip()
            cmmi.append(CmmiLevel(level=level, name=name, description=desc))
        elif current is not None:
            current.levels[level] = LevelDef(level=level, description=desc, example=example)

    return Model(title=title, terms=terms, cmmi_levels=cmmi, axes=axes)


def parse_action_csv(path: Path, model: Model) -> None:
    rows = _read_csv(path)
    model.action_title = rows[0][0].strip()
    terms, header_idx = _parse_terms(rows, 1, "評価項目")
    model.action_terms = terms

    current: Optional[Axis] = None
    for row in rows[header_idx + 1 :]:
        row = (row + [""] * 5)[:5]
        axis_cell, target, improvement, leverage, notes = (c.strip() for c in row)
        if axis_cell:
            current = model.axis_by_name(_split_lines(axis_cell)[0])
            if current is None:
                print(f"[warn] アクションプランの評価項目 '{axis_cell}' が成熟度モデルに存在しません", file=sys.stderr)
        m = TRANSITION_RE.search(target)
        if not m or current is None:
            continue
        frm, to = int(m.group(1)), int(m.group(2))
        current.transitions[(frm, to)] = Transition(frm, to, improvement, leverage, notes)


def find_csv_dir(explicit: Optional[str] = None) -> Path:
    """CSV ディレクトリを解決する。優先順: 引数 > 環境変数 OMM_CSV_DIR > リポジトリ配置 > スキル同梱コピー。"""
    here = Path(__file__).resolve().parent
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    if os.environ.get("OMM_CSV_DIR"):
        candidates.append(Path(os.environ["OMM_CSV_DIR"]))
    candidates.append(here.parents[3] / "csv")  # <repo>/.claude/skills/<skill>/scripts → <repo>/csv
    candidates.append(here.parent / "references" / "csv")  # スキル同梱コピー
    for c in candidates:
        if (c / MODEL_CSV).is_file() and (c / ACTION_CSV).is_file():
            return c.resolve()
    raise FileNotFoundError(
        "成熟度モデル CSV が見つかりません。--csv-dir または OMM_CSV_DIR で "
        f"{MODEL_CSV} と {ACTION_CSV} を含むディレクトリを指定してください。試行: "
        + ", ".join(str(c) for c in candidates)
    )


def load_model(csv_dir: Optional[str] = None) -> Model:
    d = find_csv_dir(csv_dir)
    model = parse_model_csv(d / MODEL_CSV)
    parse_action_csv(d / ACTION_CSV, model)
    validate(model)
    return model


def validate(model: Model) -> List[str]:
    """CONTRIBUTING の「データの整合性」観点を機械的に確認する。問題を文字列リストで返す（空なら整合）。"""
    problems: List[str] = []
    if len(model.cmmi_levels) != 5:
        problems.append(f"CMMI レベル定義が {len(model.cmmi_levels)} 件（期待 5）")
    for a in model.axes:
        missing = [l for l in range(1, 6) if l not in a.levels]
        if missing:
            problems.append(f"{a.name}: レベル定義が欠落 {missing}")
        missing_t = [(l, l + 1) for l in range(1, 5) if (l, l + 1) not in a.transitions]
        if missing_t:
            problems.append(f"{a.name}: 改善アクションが欠落 {missing_t}")
    for p in problems:
        print(f"[warn] {p}", file=sys.stderr)
    return problems


def to_dict(model: Model) -> dict:
    """JSON 化しやすい dict。タプルキーは 'from-to' 文字列に変換する。"""
    d = asdict(model)
    for a in d["axes"]:
        a["key"] = f"A{a['index']}"
        a["levels"] = {str(k): v for k, v in sorted(a["levels"].items())}
        a["transitions"] = {f"{k[0]}-{k[1]}": v for k, v in sorted(a["transitions"].items())}
    return d


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="成熟度モデル CSV を JSON に変換して標準出力へ出す")
    ap.add_argument("--csv-dir", help="CSV ディレクトリ（省略時は自動解決）")
    ap.add_argument("--validate-only", action="store_true", help="整合性チェックのみ行い、問題があれば exit 1")
    args = ap.parse_args()
    m = load_model(args.csv_dir)
    if args.validate_only:
        sys.exit(1 if validate(m) else 0)
    json.dump(to_dict(m), sys.stdout, ensure_ascii=False, indent=2)
    print()
