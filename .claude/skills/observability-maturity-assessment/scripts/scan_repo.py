#!/usr/bin/env python3
"""対象リポジトリを走査し、オブザーバビリティ成熟度モデルの 6 評価軸に関する『証跡シグナル』を収集する。

- 判定はしない。signals.json のカタログに基づき「何が・どこに・どう書かれているか」を
  ファイルパス + 行番号 + 抜粋として機械的に集める。レベルの判断は SKILL.md の手順に従い
  評価者（Claude / 人間）が行う。
- 標準ライブラリのみ。ネットワークアクセスなし。対象リポジトリは一切変更しない。

使い方:
  python3 scan_repo.py /path/to/repo --out evidence.json --md evidence-summary.md
"""
from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional

HERE = Path(__file__).resolve().parent
SIGNALS_PATH = HERE / "signals.json"

SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "vendor", "bower_components", "dist", "build", "out", "target",
    ".venv", "venv", "env", "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".tox", ".nox",
    ".next", ".nuxt", ".svelte-kit", ".turbo", ".parcel-cache", ".cache", ".terraform", ".serverless",
    "coverage", "htmlcov", ".gradle", ".idea", ".vscode", "Pods", "DerivedData", ".dart_tool", "bin", "obj",
    "site-packages", ".bundle", "tmp", "temp", "logs", ".claude",  # .claude: スキル定義は運用の証跡ではない
}
LOCKFILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "go.sum", "Cargo.lock", "poetry.lock", "Pipfile.lock",
    "Gemfile.lock", "composer.lock", "mix.lock", "pubspec.lock", "Package.resolved", "flake.lock", "uv.lock",
    "bun.lockb", "shrinkwrap.yaml", "npm-shrinkwrap.json",
}
BINARY_EXT = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".svg", ".pdf", ".zip", ".gz", ".tgz", ".bz2", ".xz", ".7z",
    ".jar", ".war", ".class", ".so", ".dylib", ".dll", ".exe", ".bin", ".o", ".a", ".wasm", ".pyc", ".woff",
    ".woff2", ".ttf", ".otf", ".eot", ".mp3", ".mp4", ".mov", ".avi", ".webm", ".ogg", ".wav", ".sqlite", ".db",
    ".parquet", ".avro", ".pb", ".lock", ".min.js", ".min.css", ".map", ".ipynb", ".psd", ".ai", ".sketch", ".fig",
}
LANG_BY_EXT = {
    ".py": "Python", ".go": "Go", ".js": "JavaScript", ".jsx": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
    ".java": "Java", ".kt": "Kotlin", ".rb": "Ruby", ".rs": "Rust", ".cs": "C#", ".php": "PHP", ".swift": "Swift",
    ".dart": "Dart", ".scala": "Scala", ".ex": "Elixir", ".exs": "Elixir", ".c": "C", ".cc": "C++", ".cpp": "C++",
    ".h": "C/C++", ".hpp": "C++", ".m": "Objective-C", ".sh": "Shell", ".bash": "Shell", ".tf": "Terraform",
    ".yaml": "YAML", ".yml": "YAML", ".json": "JSON", ".md": "Markdown", ".sql": "SQL", ".html": "HTML", ".vue": "Vue",
    ".svelte": "Svelte", ".css": "CSS", ".scss": "SCSS", ".hcl": "HCL", ".proto": "Protobuf", ".graphql": "GraphQL",
}
SECRET_RE = re.compile(
    r"((?:api[_-]?key|apikey|token|secret|password|passwd|pwd|license[_-]?key|private[_-]?key|credential)s?\s*[:=]\s*[\"']?)([^\s\"',;]{4,})",
    re.I,
)
EXCERPT_MAX = 160
DOC_EXT = {".md", ".rst", ".adoc", ".txt", ".csv", ".html"}
CONFIG_EXT = {".yaml", ".yml", ".tf", ".json", ".json5", ".toml", ".ini", ".cfg", ".conf", ".properties", ".rules",
              ".hcl", ".xml", ".env", ".jsonnet", ".libsonnet", ".neon"}
DEP_BASENAMES = {"package.json", "go.mod", "pyproject.toml", "Pipfile", "pom.xml", "build.gradle", "build.gradle.kts",
                 "Gemfile", "Cargo.toml", "composer.json", "mix.exs", "Package.swift", "pubspec.yaml", "setup.py", "setup.cfg"}


def hit_kind(rel: str) -> str:
    """証跡の種別。docs は『概念に言及している』だけの可能性があり、config/code/deps より弱い証跡として扱う。"""
    base = rel.rsplit("/", 1)[-1]
    ext = os.path.splitext(base)[1].lower()
    if base in DEP_BASENAMES or base.startswith("requirements") or base.endswith(".csproj") or base.endswith(".gemspec"):
        return "deps"
    if ext in DOC_EXT:
        return "docs"
    if ext in CONFIG_EXT or base.startswith("Dockerfile") or base in ("Makefile", "Jenkinsfile", "Procfile", "CODEOWNERS"):
        return "config"
    return "code"


def redact(text: str) -> str:
    return SECRET_RE.sub(lambda m: m.group(1) + "***", text)


def path_matches(rel: str, pattern: str) -> bool:
    base = rel.rsplit("/", 1)[-1]
    if "/" not in pattern:
        return fnmatch.fnmatch(base, pattern)
    if pattern.startswith("**/"):
        return fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(rel, pattern[3:])
    return fnmatch.fnmatch(rel, pattern)


def any_match(rel: str, patterns: Iterable[str]) -> bool:
    return any(path_matches(rel, p) for p in patterns)


def is_probably_binary(data: bytes) -> bool:
    return b"\x00" in data[:4096]


def git_meta(repo: Path) -> dict:
    meta: dict = {}
    if not (repo / ".git").exists():
        return meta

    def run(*args: str) -> Optional[str]:
        try:
            return subprocess.run(
                ["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=30, check=False
            ).stdout.strip()
        except Exception:  # noqa: BLE001
            return None

    meta["commit"] = run("rev-parse", "--short", "HEAD")
    meta["branch"] = run("rev-parse", "--abbrev-ref", "HEAD")
    meta["last_commit_date"] = run("log", "-1", "--format=%cs")
    meta["first_commit_date"] = (run("log", "--reverse", "--format=%cs") or "").split("\n")[0] or None
    count = run("rev-list", "--count", "HEAD")
    meta["commit_count"] = int(count) if count and count.isdigit() else None
    authors = run("shortlog", "-sn", "--no-merges", "HEAD")
    meta["author_count"] = len([l for l in (authors or "").splitlines() if l.strip()]) or None
    remote = run("remote", "get-url", "origin")
    meta["origin"] = remote or None
    shallow = (repo / ".git" / "shallow").exists()
    meta["shallow_clone"] = shallow
    return meta


def walk_files(repo: Path, max_files: int, notes: List[str]) -> List[str]:
    rels: List[str] = []
    for root, dirs, files in os.walk(repo):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for f in sorted(files):
            rel = os.path.relpath(os.path.join(root, f), repo).replace(os.sep, "/")
            rels.append(rel)
            if len(rels) >= max_files:
                notes.append(f"ファイル数が上限 {max_files} に達したため走査を打ち切りました（結果は部分的です）")
                return rels
    return rels


def load_signals() -> dict:
    with SIGNALS_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def compile_signals(catalog: dict) -> List[dict]:
    deps = catalog.get("dependency_files", [])
    compiled = []
    for s in catalog["signals"]:
        c = dict(s)
        c["_paths"] = s.get("paths", [])
        cps = s.get("content_paths")
        if cps:
            expanded: List[str] = []
            for p in cps:
                expanded.extend(deps if p == "$DEPS" else [p])
            c["_content_paths"] = expanded
        else:
            c["_content_paths"] = None  # None = 全テキストファイル
        c["_regexes"] = [re.compile(p, re.I | re.M) for p in s.get("content", [])]
        compiled.append(c)
    return compiled


def scan(repo: Path, max_file_bytes: int, max_hits: int, max_files: int) -> dict:
    notes: List[str] = []
    catalog = load_signals()
    signals = compile_signals(catalog)
    rels = walk_files(repo, max_files, notes)

    # 1) パス一致
    path_hits: Dict[str, List[str]] = defaultdict(list)
    for rel in rels:
        base = rel.rsplit("/", 1)[-1]
        for s in signals:
            if s["_paths"] and any_match(rel, s["_paths"]):
                if base in LOCKFILES:
                    continue
                path_hits[s["id"]].append(rel)

    # 2) 本文一致（ファイルは 1 回だけ読む）
    content_hits: Dict[str, List[dict]] = defaultdict(list)
    scanned_text_files = 0
    skipped_large = 0
    ext_counter: Counter = Counter()
    for rel in rels:
        base = rel.rsplit("/", 1)[-1]
        ext = os.path.splitext(base)[1].lower()
        if base.endswith(".min.js") or base.endswith(".min.css"):
            continue
        ext_counter[ext] += 1
        if ext in BINARY_EXT or base in LOCKFILES:
            continue
        candidates = [
            s for s in signals
            if s["_regexes"] and (s["_content_paths"] is None or any_match(rel, s["_content_paths"]))
            and len(content_hits[s["id"]]) < max_hits
        ]
        if not candidates:
            continue
        full = repo / rel
        try:
            size = full.stat().st_size
        except OSError:
            continue
        if size > max_file_bytes:
            skipped_large += 1
            continue
        try:
            data = full.read_bytes()
        except OSError:
            continue
        if is_probably_binary(data):
            continue
        text = data.decode("utf-8", errors="replace")
        scanned_text_files += 1
        line_starts: Optional[List[int]] = None
        for s in candidates:
            for rx in s["_regexes"]:
                for m in rx.finditer(text):
                    if len(content_hits[s["id"]]) >= max_hits:
                        break
                    if line_starts is None:
                        line_starts = [0]
                        for i, ch in enumerate(text):
                            if ch == "\n":
                                line_starts.append(i + 1)
                    # 行番号を二分探索で求める
                    lo, hi = 0, len(line_starts) - 1
                    while lo < hi:
                        mid = (lo + hi + 1) // 2
                        if line_starts[mid] <= m.start():
                            lo = mid
                        else:
                            hi = mid - 1
                    line_no = lo + 1
                    line_end = text.find("\n", line_starts[lo])
                    line = text[line_starts[lo] : line_end if line_end != -1 else None].strip()
                    excerpt = redact(line)[:EXCERPT_MAX]
                    # 同一ファイル・同一行の重複は 1 回だけ
                    if any(h["file"] == rel and h["line"] == line_no for h in content_hits[s["id"]]):
                        continue
                    content_hits[s["id"]].append(
                        {"file": rel, "line": line_no, "kind": hit_kind(rel), "pattern": rx.pattern, "excerpt": excerpt}
                    )
                    break  # 同じ正規表現で同じファイルから多数拾わない（1 ファイル 1 行）
    if skipped_large:
        notes.append(f"{skipped_large} ファイルがサイズ上限 {max_file_bytes} バイト超のため本文走査をスキップしました")

    # 3) 集計
    signal_results = []
    axis_summary: Dict[str, dict] = {
        k: {"name": v, "signals_hit": [], "hint_levels_with_evidence": [], "strong_hint_levels": [],
            "max_hint_level": 0, "signals_total": 0}
        for k, v in catalog["axes"].items()
    }
    for s in signals:
        ax = axis_summary[s["axis"]]
        ax["signals_total"] += 1
        p = sorted(set(path_hits.get(s["id"], [])))
        c = content_hits.get(s["id"], [])
        hit = bool(p or c)
        kinds = Counter(h["kind"] for h in c)
        if p:
            kinds["path"] = len(p)
        strong = bool(p) or any(h["kind"] != "docs" for h in c)
        signal_results.append(
            {
                "id": s["id"],
                "axis": s["axis"],
                "hint_level": s["hint_level"],
                "title": s["title"],
                "why": s.get("why", ""),
                "hit": hit,
                "strong": strong,
                "kinds": dict(kinds),
                "path_matches": p[:max_hits * 3],
                "path_match_count": len(p),
                "content_hits": c,
            }
        )
        if hit:
            ax["signals_hit"].append(s["id"])
            ax["hint_levels_with_evidence"].append(s["hint_level"])
            ax["max_hint_level"] = max(ax["max_hint_level"], s["hint_level"])
            if strong:
                ax["strong_hint_levels"].append(s["hint_level"])
    for ax in axis_summary.values():
        ax["hint_levels_with_evidence"] = sorted(set(ax["hint_levels_with_evidence"]))
        ax["strong_hint_levels"] = sorted(set(ax["strong_hint_levels"]))

    languages = Counter()
    for ext, n in ext_counter.items():
        if ext in LANG_BY_EXT:
            languages[LANG_BY_EXT[ext]] += n
    meta = {
        "file_count": len(rels),
        "text_files_scanned": scanned_text_files,
        "languages_top": languages.most_common(8),
        "has_readme": any(r.lower().startswith("readme") for r in rels),
        "has_docs_dir": any(r.startswith(("docs/", "doc/")) for r in rels),
        "has_dockerfile": any(r.rsplit("/", 1)[-1].startswith("Dockerfile") for r in rels),
        "has_k8s_manifests": any(
            r.endswith((".yaml", ".yml")) and ("/k8s/" in f"/{r}" or "/kubernetes/" in f"/{r}" or "/manifests/" in f"/{r}" or "/helm/" in f"/{r}")
            for r in rels
        ),
        "has_terraform": any(r.endswith(".tf") for r in rels),
        "top_level_entries": sorted({r.split("/", 1)[0] for r in rels})[:60],
    }
    meta.update(git_meta(repo))

    return {
        "target": {"path": str(repo), "name": repo.name},
        "scanned_at": dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds"),
        "scanner": {"signals_catalog": str(SIGNALS_PATH.name), "signal_count": len(signals)},
        "notes": notes,
        "meta": meta,
        "axes": axis_summary,
        "signals": signal_results,
    }


def render_markdown(result: dict) -> str:
    out: List[str] = []
    m = result["meta"]
    out.append(f"# 証跡サマリ: {result['target']['name']}")
    out.append("")
    out.append(f"- 走査日時: {result['scanned_at']}")
    out.append(f"- パス: `{result['target']['path']}`")
    if m.get("origin"):
        out.append(f"- origin: {m['origin']}")
    if m.get("commit"):
        out.append(
            f"- コミット: `{m['commit']}` ({m.get('branch')}) / 最終コミット {m.get('last_commit_date')} / "
            f"コミット数 {m.get('commit_count')} / 著者数 {m.get('author_count')}"
            + (" / shallow clone" if m.get("shallow_clone") else "")
        )
    out.append(f"- ファイル数 {m['file_count']}（本文走査 {m['text_files_scanned']}）")
    if m.get("languages_top"):
        out.append("- 主要言語: " + ", ".join(f"{l} ({n})" for l, n in m["languages_top"]))
    flags = [k for k in ("has_readme", "has_docs_dir", "has_dockerfile", "has_k8s_manifests", "has_terraform") if m.get(k)]
    out.append("- 構成: " + (", ".join(flags) if flags else "特記なし"))
    for n in result["notes"]:
        out.append(f"- ⚠️ {n}")
    out.append("")
    out.append("> この表はシグナルの有無を示すだけで、成熟度レベルの判定ではありません。`hint` は『その成果物を持つ組織が通常到達しているレベルの目安』です。")
    out.append("> ✅ = 設定・コード・依存・ファイル配置に証跡あり / 📝 = 文書への言及のみ（弱い証跡） / ・ = 証跡なし")
    out.append("")

    by_axis: Dict[str, List[dict]] = defaultdict(list)
    for s in result["signals"]:
        by_axis[s["axis"]].append(s)
    for key, ax in result["axes"].items():
        out.append(f"## {key}. {ax['name']}")
        out.append("")
        out.append(
            f"ヒットしたシグナル: {len(ax['signals_hit'])}/{ax['signals_total']} / "
            f"証跡のある hint レベル: {ax['hint_levels_with_evidence'] or 'なし'} / "
            f"文書以外（設定・コード・依存）の証跡があるレベル: {ax['strong_hint_levels'] or 'なし'}"
        )
        out.append("")
        out.append("| hint | シグナル | 件数（種別） | 代表的な証跡 |")
        out.append("|---|---|---|---|")
        for s in sorted(by_axis[key], key=lambda x: (x["hint_level"], x["id"])):
            n = s["path_match_count"] + len(s["content_hits"])
            if s["content_hits"]:
                h = s["content_hits"][0]
                ev = f"`{h['file']}:{h['line']}` — {h['excerpt'][:80]}"
            elif s["path_matches"]:
                ev = "`" + "`, `".join(s["path_matches"][:3]) + "`"
            else:
                ev = "—"
            mark = "✅" if s["strong"] else ("📝" if s["hit"] else "・")
            kinds = ", ".join(f"{k} {v}" for k, v in sorted(s["kinds"].items()))
            cell = f"{n}" + (f"（{kinds}）" if kinds else "")
            out.append(f"| L{s['hint_level']} | {mark} {s['title']} (`{s['id']}`) | {cell} | {ev.replace('|', '\\|')} |")
        out.append("")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", help="走査対象リポジトリのローカルパス")
    ap.add_argument("--out", default="evidence.json", help="証跡 JSON の出力先")
    ap.add_argument("--md", default=None, help="人間向け Markdown サマリの出力先（省略時は出力しない）")
    ap.add_argument("--max-file-bytes", type=int, default=1_000_000)
    ap.add_argument("--max-hits-per-signal", type=int, default=12)
    ap.add_argument("--max-files", type=int, default=60_000)
    args = ap.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    if not repo.is_dir():
        print(f"エラー: ディレクトリがありません: {repo}", file=sys.stderr)
        return 2
    result = scan(repo, args.max_file_bytes, args.max_hits_per_signal, args.max_files)
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.md:
        Path(args.md).write_text(render_markdown(result), encoding="utf-8")
    hit_total = sum(1 for s in result["signals"] if s["hit"])
    print(f"走査完了: {repo.name} — ファイル {result['meta']['file_count']} / シグナル {hit_total}/{len(result['signals'])} ヒット")
    for k, ax in result["axes"].items():
        print(f"  {k} {ax['name']}: {len(ax['signals_hit'])}/{ax['signals_total']} 証跡レベル {ax['hint_levels_with_evidence'] or '-'} (文書以外: {ax['strong_hint_levels'] or '-'})")
    print(f"→ {args.out}" + (f", {args.md}" if args.md else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
