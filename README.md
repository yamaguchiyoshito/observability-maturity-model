# オブザーバビリティ成熟度モデル

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-brightgreen.svg)](https://creativecommons.org/licenses/by/4.0/)
[![docs-check](https://github.com/yamaguchiyoshito/observability-maturity-model/actions/workflows/docs-check.yml/badge.svg)](https://github.com/yamaguchiyoshito/observability-maturity-model/actions/workflows/docs-check.yml)

DMM.comで策定・運用されている、組織のオブザーバビリティ能力を6つの評価軸で測定し、段階的な改善を支援するための成熟度モデルです。

> このリポジトリは [dmm-com/observability-maturity-model](https://github.com/dmm-com/observability-maturity-model) のフォークです。元のモデル（CSV / PDF）に加えて、**閲覧用 Markdown サイト（GitHub Pages）** と、**対象リポジトリの成熟度評価を下書きする Claude Code スキル** を追加しています。

## 📋 概要

このモデルは、組織のオブザーバビリティ実践を体系的に評価し、継続的な改善を推進するためのフレームワークです。CMMI（能力成熟度モデル統合）の考え方を基に、オブザーバビリティ領域に特化した5段階の成熟度レベルと、6つの評価軸を定義しています。

| 評価軸 | 能力 |
|---|---|
| A1. [データ収集と可視化](docs/model/data-collection-and-visualization.md) | あらゆる領域のデータを網羅的に収集し、リアルタイムで可視化・分析できる |
| A2. [システムの信頼性管理](docs/model/system-reliability-management.md) | 障害対応・復旧プロセスを整備し、観測指標に基づく信頼性評価とリスク改善を継続する |
| A3. [開発・運用プロセスの整備と最適化](docs/model/dev-ops-process-optimization.md) | コード品質を維持したまま予測可能で安定したデリバリーを実現する |
| A4. [アラート最適化と障害対応](docs/model/alert-optimization-and-incident-response.md) | 異常を適切に検知し、ノイズを抑えながら迅速に対応する |
| A5. [ユーザー行動の理解と最適化](docs/model/user-behavior-understanding.md) | ユーザーの利用状況やニーズを把握し、改善に反映する |
| A6. [継続的な改善と最適化](docs/model/continuous-improvement.md) | モニタリングや開発プロセスのデータを活用し、チーム全体で継続的な改善を推進する |

レベル: 1 属人的 → 2 プロセス確立 → 3 組織標準化 → 4 定量管理 → 5 継続的最適化（[レベル別ビュー](docs/levels/)）

## 📁 ドキュメント

### Web で読む（GitHub Pages）

`docs/` 配下を [GitHub Pages](docs/index.md) として公開する構成になっています（Jekyll + just-the-docs、サイドバー・全文検索付き）。

- [はじめに](docs/index.md) — モデルの読み方
- [成熟度モデル](docs/model/index.md) — 名称定義・レベル定義・6軸×5レベル一覧。各軸ページでレベルごとの説明・具体例と、次のレベルへの改善アクションを続けて読めます
- [全量マトリクス](docs/matrix.md) — 6 軸 × 5 レベルの説明・具体例と改善アクションを 1 枚の表で
- [レベル別ビュー](docs/levels/index.md) — 「レベル N とは全体としてどんな状態か」を軸横断で読む
- [個人評価](docs/self-assessment.md) — 表上でレベルを選択して自己評価。選択はブラウザの localStorage に保存され、集計をページ内に表示（Pages 上でのみ動作）
- [評価の進め方](docs/assessment/index.md) — 評価手順、判定で迷いやすい点、[レポートテンプレート](docs/assessment/report-template.md)

左ペインの目次はヘッダの「目次: 標準 / コンパクト」で畳めます（横長の表を読むとき用。設定はブラウザに保存）。
- [ダウンロード](docs/downloads.md)

公開手順: リポジトリの **Settings → Pages → Source: Deploy from a branch → Branch: `main` / Folder: `/docs`**。`docs/_config.yml` の `url` / `baseurl` / `aux_links` をフォーク先に合わせて書き換えてください。

### PDFファイル（閲覧用）

- **[成熟度モデル (PDF)](pdf/observability-maturity-model.pdf)** — 6つの評価項目について、レベル1（属人的）からレベル5（継続的最適化）までの状態と具体例
- **[改善アクションプラン (PDF)](pdf/improvement-action-plan.pdf)** — 現在のレベルから次のレベルへ進むための「改善アクション（必須）」と「活用アクション（推奨）」

### CSVファイル（編集用データソース・唯一の正）

PDF と `docs/` の元データです。自社向けにカスタマイズする際はこちらを編集してください。

- **[成熟度モデル (CSV)](csv/observability-maturity-model.csv)**
- **[改善アクションプラン (CSV)](csv/improvement-action-plan.csv)**

CSV を編集したら `python3 tools/build_docs.py` で `docs/` とスキル同梱コピーを再生成します（CI の `docs-check` が同期を検証します）。

## 🤖 評価を下書きする Claude Code スキル

[`.claude/skills/observability-maturity-assessment/`](.claude/skills/observability-maturity-assessment/SKILL.md) は、指定したリポジトリ（ローカルパスまたは GitHub URL）を走査し、設定・コード・文書を証跡として 6 軸の **暫定レベル・確信度・次レベルとのギャップ・ヒアリング質問・改善アクションプラン** を含む評価レポートの下書きを生成する Agent Skill です。

```text
Claude Code をこのリポジトリで起動し:
  /observability-maturity-assessment https://github.com/org/your-service を評価して
```

- `scripts/scan_repo.py` — 54 種の証跡シグナル（OpenTelemetry、SLO 定義、ランブック、アラートルール、CI/CD、解析 SDK、ふりかえり記録…）を `file:line` 付きで収集。判定はしない
- Claude が `references/evidence-rubric.md` に沿って軸ごとに暫定レベルと確信度を決め、`assessment.json` に書く
- `scripts/build_report.py` — モデル本文（レベル定義・改善アクション）を CSV から引用してレポートを生成

スクリプトは Python 標準ライブラリのみで動き、対象リポジトリを変更しません。他リポジトリで使う場合はスキルディレクトリを `.claude/skills/` または `~/.claude/skills/` にコピーします。

> 生成物は**下書き**です。「組織全体で標準化」「定期的にレビュー」といった要件はリポジトリだけでは確定できないため、レポート中のヒアリング質問への回答を得てから最終評価としてください。

## 🗂 リポジトリ構成

```text
csv/        成熟度モデル・改善アクションプラン（唯一の正）
pdf/        閲覧用 PDF
docs/       GitHub Pages（Jekyll）。model/ と levels/ は tools/build_docs.py が CSV から生成
tools/      build_docs.py — CSV → docs/ 生成、スキル同梱 CSV の同期、--check で CI 検証
.claude/skills/observability-maturity-assessment/   評価下書き生成スキル
.github/workflows/docs-check.yml   CSV 整合性・生成物同期・スキルのスモークテスト
```

## 🤝 カスタマイズ・コントリビューション

自社向けにCSVをカスタマイズする際の編集手順や注意点は、[コントリビューションガイド（CONTRIBUTING.md）](CONTRIBUTING.md)を参照してください。

## 📄 ライセンス

このプロジェクトは[Creative Commons Attribution 4.0 International License](LICENSE)の下でライセンスされています。

## ✍️ 著作者

**DMM.com LLC**（成熟度モデル本体）

フォークで追加した `docs/` のサイト構成・`tools/`・`.claude/skills/` は同ライセンスで提供します。
