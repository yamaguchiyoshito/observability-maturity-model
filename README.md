# オブザーバビリティ成熟度モデル

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-brightgreen.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Publish GitHub Pages](https://github.com/yamaguchiyoshito/observability-maturity-model/actions/workflows/pages.yml/badge.svg)](https://github.com/yamaguchiyoshito/observability-maturity-model/actions/workflows/pages.yml)

DMM.comで策定・運用されている、組織のオブザーバビリティ能力を6つの評価軸で測定し、段階的な改善を支援するための成熟度モデルです。

> このリポジトリは [dmm-com/observability-maturity-model](https://github.com/dmm-com/observability-maturity-model) のフォークです。元のモデル（CSV / PDF）はそのままに、次を追加しています。
>
> - **閲覧用サイト（GitHub Pages）** — 軸別・レベル別ページ、全量マトリクス、ブラウザ上で行う個人評価、日本語対応の全文検索
> - **評価を下書きする Claude Code スキル** — 指定リポジトリを走査し、証跡付きの暫定レベルとヒアリング質問を含むレポートを生成

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

レベル: 1 属人的 → 2 プロセス確立 → 3 組織標準化 → 4 定量管理 → 5 継続的最適化（[レベル別ビュー](docs/levels/index.md)）

レベルは軸ごとに独立です。6 軸の平均を「組織の成熟度」として扱うことは想定していません。

## 📁 ドキュメント

### Web で読む（GitHub Pages）

`docs/` 配下を [VitePress](https://vitepress.dev/) でビルドし、GitHub Actions から GitHub Pages に公開する構成です（サイドバー、日本語対応の全文検索、ダークモード付き）。GitHub 上でも Markdown としてそのまま読めます。

| ページ | 内容 |
|---|---|
| [はじめに](docs/index.md) | モデルの読み方、6 軸・5 レベルの早見表 |
| [成熟度モデル](docs/model/index.md) | 名称定義、CMMI レベル定義、6 軸 × 5 レベルの一覧表。各軸ページではレベルごとの説明・具体例と、次のレベルへ進むための改善アクション（必須）・活用アクション（推奨）・注意点メモを続けて読めます |
| [全量マトリクス](docs/matrix.md) | 縦軸に評価軸、横軸に Lv1〜5 を取り、全セルの説明を 1 枚で確認。具体例と改善アクションプランはセル内で展開 |
| [レベル別ビュー](docs/levels/index.md) | 「レベル N とは全体としてどんな状態か」を 6 軸横断で読む |
| [個人評価](docs/self-assessment.md) | マトリクス上でセルをクリックしてレベルを選択し、軸別レベル・レベル分布・次のアクションへのリンクをページ内に集計。選択はブラウザの localStorage に保存され、Markdown でコピーできます（Pages 上でのみ動作） |
| [評価の進め方](docs/assessment/index.md) | 評価手順、判定で迷いやすい点、[評価レポートテンプレート](docs/assessment/report-template.md)、スキルの使い方 |
| [ダウンロード](docs/downloads.md) | PDF / CSV / JSON 変換 |

サイトの操作:

- **目次の切替** — 左の目次の上にある「目次をコンパクト表示」で目次を畳み、横長の表を広く読めます。設定はブラウザに保存され、描画前に適用されます。
- **全文検索** — 日本語で検索できます（ローカル検索の tokenizer を 1 文字と 2 文字単位に設定。`docs/.vitepress/config.ts`）。

### 公開の仕組み

| 項目 | 内容 |
|---|---|
| ビルド | `npm run docs:build`（[scripts/build_docs.mjs](scripts/build_docs.mjs)）: CSV の整合性 → 生成物の同期チェック → ダウンロード用ファイル生成 → VitePress ビルド |
| 検証 | `npm run test:site`（[scripts/check_site.mjs](scripts/check_site.mjs)）: ビルド済みサイトを配信し、Playwright でトップ・深いリンク・全量マトリクス・個人評価の保存・目次切替・日本語検索・ダウンロード・モバイル表示を確認 |
| 公開 | [.github/workflows/pages.yml](.github/workflows/pages.yml): `main` への push でビルドと検証を実行し、`actions/upload-pages-artifact` → `actions/deploy-pages` で公開 |
| PR 検証 | [.github/workflows/docs.yml](.github/workflows/docs.yml): base パス `/` と `/preview-repository/` の 2 通りでビルドと検証を行い、スクリーンショットをアーティファクトに保存。評価スキルのスモークテストも実行 |
| base パス | `actions/configure-pages` が渡す `SITE_BASE_PATH` を使用。ローカルではリポジトリ名から `/observability-maturity-model/` を既定にする |

初回だけ、リポジトリの **Settings → Pages → Build and deployment → Source: GitHub Actions** を選んでください。フォーク先ごとの URL 書き換えは不要です（`GITHUB_REPOSITORY` から決まります）。

### ローカルでプレビューする

Node.js（`.nvmrc` の版）と Python 3 が必要です。

```bash
npm ci
npm run docs:dev
```

`http://localhost:5173/observability-maturity-model/` で確認できます。公開と同じ手順で検証するには、Playwright のブラウザを入れてから `npm test` を実行します。

```bash
npx playwright install chromium
npm test
```

### PDFファイル（閲覧用）

- **[成熟度モデル (PDF)](pdf/observability-maturity-model.pdf)** — 6つの評価項目について、レベル1（属人的）からレベル5（継続的最適化）までの状態と具体例
- **[改善アクションプラン (PDF)](pdf/improvement-action-plan.pdf)** — 現在のレベルから次のレベルへ進むための「改善アクション（必須）」と「活用アクション（推奨）」

### CSVファイル（編集用データソース・唯一の正）

PDF と `docs/` の元データです。自社向けにカスタマイズする際はこちらを編集してください。

- **[成熟度モデル (CSV)](csv/observability-maturity-model.csv)**
- **[改善アクションプラン (CSV)](csv/improvement-action-plan.csv)**

CSV を編集したら次を実行して、`docs/` の生成ページとスキル同梱の CSV コピーを再生成します。CI の `docs-check` が同期を検証します。

```bash
python3 tools/build_docs.py
```

## 🤖 評価を下書きする Claude Code スキル

[`.claude/skills/observability-maturity-assessment/`](.claude/skills/observability-maturity-assessment/SKILL.md) は、指定したリポジトリ（ローカルパスまたは GitHub URL）を走査し、設定・コード・文書を証跡として 6 軸の **暫定レベル・確信度・次レベルとのギャップ・ヒアリング質問・改善アクションプラン** を含む評価レポートの下書きを生成する Agent Skill です。

```text
Claude Code をこのリポジトリで起動し:
  /observability-maturity-assessment https://github.com/org/your-service を評価して
```

役割分担:

| 担当 | 内容 |
|---|---|
| `scripts/scan_repo.py` | 54 種の証跡シグナル（OpenTelemetry、SLO 定義、ランブック、アラートルール、CI/CD、解析 SDK、ふりかえり記録など）を `file:line` 付きで収集。設定・コード・依存の証跡と、文書への言及だけの弱い証跡を区別する。判定はしない |
| Claude | `references/evidence-rubric.md` に沿って軸ごとに暫定レベルと確信度を決め、`assessment.json` に書く。レベル3以上は組織横断性が要件なので原則「中」以下、レベル5はリポジトリだけでは「低」 |
| `scripts/build_report.py` | モデル本文（レベル定義・改善アクション）を CSV から引用し、ヒアリング質問を添えたレポートを生成 |

スクリプトは Python 標準ライブラリのみで動き、対象リポジトリを変更しません。他リポジトリで使う場合はスキルディレクトリを対象の `.claude/skills/` または `~/.claude/skills/` にコピーします。モデル本文は同梱の CSV コピーから引用されます。

> 生成物は**下書き**です。「組織全体で標準化」「定期的にレビュー」といった要件はリポジトリだけでは確定できないため、レポート中のヒアリング質問への回答を得てから最終評価としてください。

## 🗂 リポジトリ構成

```text
csv/                      成熟度モデル・改善アクションプラン（唯一の正）
pdf/                      閲覧用 PDF
build/model.json          [生成] CSV の JSON 表現。.vitepress/config.ts がサイドバー生成に読む
docs/                     サイト（VitePress）
├── .vitepress/config.ts  サイト設定（ナビ・サイドバー・日本語検索・base パス）
├── .vitepress/theme/     テーマ拡張: SidebarToggle.vue（目次切替）, MatrixAssessment.vue（個人評価）, Downloads.vue, style.css
├── public/               favicon。downloads/ はビルド時に csv/ pdf/ から生成（gitignore）
├── index.md, downloads.md, assessment/   手書きページ
├── model/, levels/, matrix.md, self-assessment.md   [生成] tools/build_docs.py が CSV から生成
tools/build_docs.py       CSV → docs/ と build/model.json の生成、スキル同梱 CSV の同期、--check で同期検証、--downloads で配布物生成
scripts/build_docs.mjs    サイトのビルド手順（CI とローカルで共通）
scripts/check_site.mjs    ビルド済みサイトの Playwright 検証
.claude/skills/observability-maturity-assessment/   評価下書き生成スキル（SKILL.md, scripts/, references/）
.github/workflows/        pages.yml（公開）, docs.yml（PR 検証）
```

生成ページは直接編集せず、CSV を編集して `tools/build_docs.py` を実行してください。詳細は [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。

## 🤝 カスタマイズ・コントリビューション

自社向けにCSVをカスタマイズする際の編集手順や注意点は、[コントリビューションガイド（CONTRIBUTING.md）](CONTRIBUTING.md)を参照してください。

## 📄 ライセンス

このプロジェクトは[Creative Commons Attribution 4.0 International License](LICENSE)の下でライセンスされています。

## ✍️ 著作者

**DMM.com LLC**（成熟度モデル本体）

フォークで追加した `docs/` のサイト構成・`tools/`・`.claude/skills/` は同ライセンスで提供します。
