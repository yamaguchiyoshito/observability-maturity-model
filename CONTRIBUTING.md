# コントリビューションガイド

このリポジトリのオブザーバビリティ成熟度モデルは、Creative Commons Attribution 4.0（CC BY 4.0）の下で公開しています。自社向けにカスタマイズして利用する場合は、以下のガイドを参考にしてください。

## 📁 データソースについて

このリポジトリのコンテンツは、以下の2種類のファイルで構成されています。

- **CSVファイル（`csv/`）**: 成熟度モデルの定義本体です。編集・カスタマイズの起点となるデータソースです。
  - `observability-maturity-model.csv`: 6つの評価項目についてレベル1〜5の状態と具体例を定義したマスタデータ
  - `improvement-action-plan.csv`: 各レベルから次段階へ進むための改善アクション・活用アクション・注意点を定義したデータ
- **PDFファイル（`pdf/`）**: 上記CSVを読みやすいレイアウトにまとめた閲覧用の成果物です。

## ✏️ CSVを編集する際の手順

成熟度モデルの定義を変更する場合は、次の順序で編集するとスムーズです。

1. **`observability-maturity-model.csv`（基本定義）を先に更新する**
    - 成熟度モデルの評価項目やレベル定義（レベル1〜5）は、こちらが基準になります。
2. **`improvement-action-plan.csv`（改善アクションプラン）を後から更新する**
    - 基本定義の変更に合わせて、レベルアップ対象やアクション内容に乖離が生じないよう調整すると、両者の対応を保てます。

### 編集時の注意点

このリポジトリのデータ構造ならではの、編集時に注意したい点です。いずれも「編集したデータが壊れて成熟度モデルやPDFが意図どおりに扱えなくなる」ことを避けるための観点です。

- **データの整合性**: 2つのCSVは相互に対応する構造になっています（`improvement-action-plan.csv` は「レベル1→レベル2」のようなレベル遷移を単位に改善アクションを定義し、`observability-maturity-model.csv` で定義したレベル1〜5と対応します）。片方だけを変更すると、成熟度モデルとアクションプランの対応がずれ、モデルを利用する際やPDFを再生成する際に意図しない内容になります。これを防ぐため、両ファイルの評価項目名とレベル定義を揃えて編集することをおすすめします。
- **エスケープ処理**: 評価項目のセルは、説明文を含む複数行のテキストがダブルクォートで囲まれています。Excelなどの表計算ソフトで編集すると、セル内の改行やカンマによってCSVの区切りが崩れ、ファイルが正しく読み込めなくなることがあります。編集後は、クォート・エスケープが崩れていないか確認することをおすすめします。

## 🔄 PDFの更新について

PDFはCSVから生成される閲覧用の成果物で、CSVが唯一の正となります。CSVを更新した場合は、対応するPDF（`pdf/`）も再生成しておくと、閲覧時にCSVとPDFの内容が食い違わずに済みます。

## 🧩 Markdown（docs/）とスキル同梱データの再生成

`docs/model/`・`docs/levels/`・`docs/matrix.md`・`docs/self-assessment.md`、`build/model.json`、および評価スキルが同梱する CSV コピー（`.claude/skills/observability-maturity-assessment/references/csv/`）は、CSV から自動生成しています。**直接編集せず**、CSV を編集したあとに次を実行してください（Python 3.9 以降、標準ライブラリのみ）。

```bash
python3 tools/build_docs.py
```

サイトのビルド（`npm run docs:build`）と PR 検証（`.github/workflows/docs.yml`）は次を行います。いずれかが失敗した場合は上記コマンドを実行して差分をコミットしてください。

1. `omm_model.py --validate-only` — 2 つの CSV の対応（6 軸 × レベル1〜5 の定義と、レベル1→2 〜 4→5 の改善アクションが揃っているか）
2. `build_docs.py --check` — 生成物が CSV と同期しているか
3. `build_docs.py --downloads` — ダウンロード用の PDF・CSV・JSON と manifest を `docs/public/downloads/` に生成（gitignore 対象）
4. VitePress ビルドと `scripts/check_site.mjs` による Playwright 検証（主要ページ、個人評価の保存、目次切替、日本語検索、ダウンロード、モバイル表示）
5. 評価スキルのスクリプトがこのリポジトリを走査できるか（スモークテスト）

サイトをローカルで確認するには `npm ci` のあと `npm run docs:dev` を実行します（Node.js は `.nvmrc` の版）。

### 評価軸を追加・改名する場合

- 軸名は 2 つの CSV で完全に一致させてください（`omm_model.py` は軸名で対応付けます）。
- 軸ページのファイル名（英語スラッグ）は `.claude/skills/observability-maturity-assessment/scripts/omm_model.py` の `AXIS_SLUGS` で定義しています。新しい軸を追加した場合はここにスラッグを追加してください（未定義なら `axis-N` になります）。
- 証跡シグナル（`scripts/signals.json`）の `axis` キー（`A1`〜`A6`）は軸の出現順に対応します。軸の順序を変えた場合は見直してください。

### 手書きページ

`docs/index.md`・`docs/assessment/`・`docs/downloads.md`・`docs/.vitepress/` は手書きです。モデル本文を引用する場合はリンクで参照し、文章をコピーしないでください（CSV 更新時に食い違います）。ナビゲーションとサイドバーの並びは `docs/.vitepress/config.ts` で定義しています（評価軸とレベルの項目は `build/model.json` から自動生成）。

## 📄 ライセンス

このリポジトリを利用・カスタマイズする際は、[Creative Commons Attribution 4.0 International License](LICENSE) の条件（著作者のクレジット表示）に従ってください。
