---
title: ダウンロード
nav_order: 7
---

# ダウンロード

## PDF（閲覧用）

読みやすいレイアウトで提供しています。まずはこちらをご覧ください。

- [成熟度モデル (PDF)]({{ site.github.repository_url }}/blob/main/pdf/observability-maturity-model.pdf) — 6 つの評価軸について、レベル1〜5 の状態と具体例
- [改善アクションプラン (PDF)]({{ site.github.repository_url }}/blob/main/pdf/improvement-action-plan.pdf) — 各レベルから次のレベルへ進むための改善アクション（必須）・活用アクション（推奨）・注意点メモ

## CSV（編集用データソース）

PDF と本サイトの元データです。自社向けにカスタマイズする際はこちらを編集してください（唯一の正）。

- [成熟度モデル (CSV)]({{ site.github.repository_url }}/blob/main/csv/observability-maturity-model.csv)
- [改善アクションプラン (CSV)]({{ site.github.repository_url }}/blob/main/csv/improvement-action-plan.csv)

編集手順と注意点（2 つの CSV の整合性、セル内改行のエスケープ）は [CONTRIBUTING.md]({{ site.github.repository_url }}/blob/main/CONTRIBUTING.md) を参照してください。

## 機械可読データ

CSV を JSON に変換するには、リポジトリで次を実行します（標準ライブラリのみ）。

```bash
python3 .claude/skills/observability-maturity-assessment/scripts/omm_model.py > model.json
```

## ライセンス

[Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/)。利用・改変・再配布の際は著作者 **DMM.com LLC** のクレジットを表示してください。
