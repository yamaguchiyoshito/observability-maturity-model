---
name: observability-maturity-assessment
description: 指定したリポジトリ（ローカルパスまたは GitHub URL）を走査し、DMM.com のオブザーバビリティ成熟度モデル（6 評価軸 × 5 レベル）に基づく成熟度評価レポートの下書きを生成する。証跡（ファイル:行）付きの暫定レベル・確信度・次レベルとのギャップ・リポジトリから確認できない事項のヒアリング質問・改善アクションプランを含む Markdown を出力する。「オブザーバビリティ成熟度を評価して」「このリポジトリの observability maturity を測って」「成熟度モデルで診断して」「監視・SRE 体制のレベルを判定して」「改善アクションプランを作って」といった依頼で使う。
---

# オブザーバビリティ成熟度評価（下書き生成）

対象リポジトリの成果物を証跡として、成熟度モデルの 6 軸それぞれに**暫定レベル**を置き、確定に必要な**ヒアリング質問**を添えた評価レポートの下書きを作る。

**前提として必ず伝えること**: 成熟度モデルの要件の多くは組織・運用の実態（「組織全体で標準化」「定期的にレビュー」）であり、リポジトリだけでは確定できない。このスキルの出力は**下書き**で、ヒアリング回答を得てから最終評価になる。

## 役割分担

| 担当 | 内容 |
|---|---|
| `scripts/scan_repo.py` | リポジトリを走査し、証跡シグナル（設定・コード・依存・文書）を `file:line` 付きで収集。**判定はしない** |
| Claude（評価者） | 証跡をレベル定義と照合して暫定レベル・確信度・ギャップ・未検証事項を決め、`assessment.json` に書く |
| `scripts/build_report.py` | `assessment.json` と CSV（モデルの正）からレポートを生成。レベル定義・改善アクションは CSV から引用 |

モデル本文は言い換えず CSV から引用する。評価者が書くのは判定と根拠だけ。

## 手順

### 1. 対象を決めて作業ディレクトリを用意する

- 引数がローカルパスならそのまま使う。GitHub URL なら作業用ディレクトリに shallow clone する:
  ```bash
  git clone --depth 1 <url> <workdir>/target
  ```
  shallow clone では履歴（更新頻度・継続性）が見えないので、継続性を要する判断は確信度を下げる。
- モノレポ・組織横断リポジトリ（platform/infra）なら、どの範囲を評価するかを決め、レポートの `scope` に書く。
- 出力先は `<workdir>/omm-assessment/`（対象リポジトリ内には書かない）。

### 2. 走査して証跡を集める

```bash
python3 <skill>/scripts/scan_repo.py <target> \
  --out <workdir>/omm-assessment/evidence.json \
  --md  <workdir>/omm-assessment/evidence-summary.md
```

`evidence-summary.md` を読む。各軸について:
- ✅（設定・コード・依存・配置の証跡）と 📝（文書への言及のみ）を区別する。📝 だけのシグナルは弱い証跡。
- 代表的な証跡を `Read`/`grep` で実際に開き、**本番構成か、サンプル・デモ・テスト用か**、**導入済みか、予定・言及か**を確認する。`examples/` `samples/` `test/` 配下は弱い証跡。
- シグナルに無い証跡も探す（対象特有のツール、独自の運用ドキュメント、CI の実際のジョブ内容）。README・`docs/`・`.github/workflows` は必ず目を通す。

### 3. 軸ごとに暫定レベルを決める

`references/evidence-rubric.md` を開き、軸ごとに次を行う:

1. L1 から順に「このレベルの主要要件が証跡で直接確認できるか」を見て、**確認できる最高のレベル**を暫定レベルにする。上位レベルの成果物が 1 つあるだけでは上げない。
2. 確信度を付ける（高／中／低）。レベル3以上は組織横断性が未確認なので原則「中」以下。レベル5はリポジトリだけでは「低」。
3. 次レベルの定義と比べたギャップ、リポジトリから確認できない事項、ヒアリング質問（`references/interview-questions.md` から選び、対象に合わせて具体化）を書く。
4. 判定できない・対象外（例: バックエンド専用リポジトリの A5）なら `level: null` にして理由を書く。無理に L1 にしない。

### 4. assessment.json を書く

`references/assessment-schema.md` の形式で `<workdir>/omm-assessment/assessment.json` を書く。

- `evidence.ref` は `evidence.json` の `file:line` をそのまま使う（読者が検証できること）。
- `rationale` には「満たした要件」と「次レベルに達しない理由」の両方を書く。
- `target` の `commit`/`branch`/`url` は `evidence.json` の `meta` から転記する。
- 全体を見て `summary`（総評）と `priorities`（最初に取り組むべきテーマ 2〜3 件、軸間の依存を考慮: 例 A4 の重要度分類は A2 のインシデント対応の前提）を書く。

### 5. レポートを生成して確認する

```bash
python3 <skill>/scripts/build_report.py <workdir>/omm-assessment/assessment.json \
  --evidence <workdir>/omm-assessment/evidence.json \
  --out <workdir>/omm-assessment/observability-maturity-assessment.md --strict
```

警告（証跡なし・確信度未設定など）が出たら `assessment.json` を直して再実行する。生成された Markdown を読み、サマリ表・各軸の判定理由・ヒアリング質問が読者にとって筋が通っているか確認する。

### 6. 報告する

ユーザーには次を伝える:
- レポートのパスと、サマリ表（軸・暫定レベル・確信度）
- 「下書きであり、各軸のヒアリング質問への回答で確定する」こと
- 優先テーマとその理由
- 走査で打ち切り・スキップがあればその旨（`evidence.json` の `notes`）

## CSV（モデル本文）の所在

`build_report.py` は次の順で CSV を探す: `--csv-dir` → 環境変数 `OMM_CSV_DIR` → リポジトリ配置（`<repo>/csv/`）→ スキル同梱コピー（`references/csv/`）。このスキルを他リポジトリや `~/.claude/skills/` にコピーした場合は同梱コピーが使われる。同梱コピーは `tools/build_docs.py` で `csv/` から同期される。

## 参照

- `references/evidence-rubric.md` — 軸 × レベルごとの「リポジトリで確認できる要件／できない要件」と判定原則、よくある誤判定
- `references/interview-questions.md` — 軸ごとの既定ヒアリング質問（レベル境界ごと）
- `references/assessment-schema.md` — `assessment.json` の形式と記入例
- `scripts/signals.json` — 証跡シグナルのカタログ。対象組織固有のツールがあれば追記してよい
