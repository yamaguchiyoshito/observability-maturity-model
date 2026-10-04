---
title: はじめに
nav_order: 1
permalink: /
---

# オブザーバビリティ成熟度モデル

DMM.com で策定・運用されている、組織のオブザーバビリティ能力を **6 つの評価軸** × **5 段階のレベル** で評価し、段階的な改善を支援するための成熟度モデルです。CMMI（能力成熟度モデル統合）の考え方をオブザーバビリティ領域に適用しています。

## このサイトの読み方

| 目的 | 読むページ |
|---|---|
| モデル全体を把握する（用語・レベル定義・6 軸の一覧） | [成熟度モデル](model/) |
| 特定の軸を深く読む（レベルごとの状態・具体例・次のレベルへの改善アクション） | [成熟度モデル](model/) → 各軸ページ |
| 「レベル N とは全体としてどんな状態か」を軸横断で読む | [レベル別ビュー](levels/) |
| 自組織・自リポジトリを評価する | [評価の進め方](assessment/) |
| PDF / CSV をダウンロードする | [ダウンロード](downloads.md) |

## 6 つの評価軸

1. [データ収集と可視化](model/data-collection-and-visualization.md) — あらゆる領域のデータを網羅的に収集し、リアルタイムで可視化・分析できる能力
2. [システムの信頼性管理](model/system-reliability-management.md) — 障害対応・復旧プロセスを整備し、観測指標に基づく信頼性評価とリスク改善を継続する能力
3. [開発・運用プロセスの整備と最適化](model/dev-ops-process-optimization.md) — コード品質を維持したまま予測可能で安定したデリバリーを実現する能力
4. [アラート最適化と障害対応](model/alert-optimization-and-incident-response.md) — 異常を適切に検知し、ノイズを抑えながら迅速に対応する能力
5. [ユーザー行動の理解と最適化](model/user-behavior-understanding.md) — ユーザーの利用状況やニーズを把握し、改善に反映する能力
6. [継続的な改善と最適化](model/continuous-improvement.md) — モニタリングや開発プロセスのデータを活用し、チーム全体で継続的な改善を推進する能力

## 5 段階のレベル

| レベル | 名称 | ひとことで |
|---|---|---|
| [1](levels/level-1.md) | 属人的 | 個人の能力と努力に依存している |
| [2](levels/level-2.md) | プロセス確立 | プロジェクト単位で基本的な管理プロセスがある |
| [3](levels/level-3.md) | 組織標準化 | 組織全体の標準が文書化され、一貫して適用されている |
| [4](levels/level-4.md) | 定量管理 | KPI と統計的手法で測定・制御されている |
| [5](levels/level-5.md) | 継続的最適化 | 改善と最適化が自動化され、組織文化として定着している |

> **レベルは軸ごとに独立**です。6 軸の平均値を「組織の成熟度」として扱うことは想定していません。各軸で「いまどこにいて、次に何をするか」を見るために使ってください。

## 文書の構成とデータの正

- `csv/` の 2 つの CSV が唯一の正（SSoT）です。本サイトの [成熟度モデル](model/) と [レベル別ビュー](levels/) のページは CSV から自動生成されています。
- PDF は CSV を読みやすいレイアウトにした閲覧用成果物です。
- カスタマイズ方法は [コントリビューションガイド](https://github.com/dmm-com/observability-maturity-model/blob/main/CONTRIBUTING.md) を参照してください。

## ライセンス

このモデルは [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/) の下で公開されています。著作者: **DMM.com LLC**。
