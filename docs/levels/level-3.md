---
title: "レベル3: 組織標準化"
---
<!-- このファイルは tools/build_docs.py が csv/ から生成しています。直接編集せず CSV を編集してください。 -->

# レベル3: 組織標準化

> **CMMI 上の定義**: 組織全体で標準化されたプロセスが定義・文書化され、全プロジェクトで一貫して適用されている。

## A1. [データ収集と可視化](../model/data-collection-and-visualization.md#level-3)

<div class="omm-block omm-desc"><p class="omm-block-title">説明</p><p>組織標準として統一されたデータ収集・可視化プロセスが文書化され、インフラ・アプリ・ネットワーク・DB層に一貫して適用されている。可視化基準や品質管理も共通ルールとして定着している。</p></div>

<div class="omm-block omm-example"><p class="omm-block-title">具体例</p><p>DatadogやNew Relicなどを使い、全層のモニタリングを標準プロセスに沿って実施している。共通テンプレートで可視化しており、異常発生時の初動確認もルール化している。</p></div>

<div class="omm-block omm-required"><p class="omm-block-title">レベル4 へ進むための改善アクション<span>必須</span></p><p>主要な指標に対して動的ベースラインによる異常検知を導入し、通常状態と異常状態を比較可能なグラフやアラート機能を整備します。あわせて、ダッシュボード上で異常兆候を視覚的に把握できる表示項目を追加します。</p><p class="omm-block-more"><a href="../model/data-collection-and-visualization.html#transition-3-4">活用アクション・注意点メモ →</a></p></div>

## A2. [システムの信頼性管理](../model/system-reliability-management.md#level-3)

<div class="omm-block omm-desc"><p class="omm-block-title">説明</p><p>組織全体で標準化されたインシデント対応プロセスおよびシステムリスク要因管理プロセスが整備され、全プロジェクトで一貫して適用されている。信頼性の指標と達成基準が組織共通で整備され、継続的に評価されている。</p></div>

<div class="omm-block omm-example"><p class="omm-block-title">具体例</p><p>各チームのSRE担当者が、共通の組織標準プロセス（例：リアルタイムインシデントレポート、ポストモーテム）に基づき、インシデントの検知・対応・復旧・振り返りを実施している。可用性やエラーレートなどの観測指標に基準値を設定し、定期的にレビューしている。プレイブックによる対応標準化や、システムリスク要因の優先順位付け・改善計画も整備している。</p></div>

<div class="omm-block omm-required"><p class="omm-block-title">レベル4 へ進むための改善アクション<span>必須</span></p><p>稼働率・障害件数・復旧時間などの信頼性指標を統計的にモニタリングし、定量的な改善評価を可能にする仕組みを整えます。インシデントごとの再発防止策や対応時間の改善効果も定期的に分析します。障害発生時に収集する情報（例：メトリクス、ログ、トレース情報）を標準化し、障害発生直後に自動で必要なデータが集められる仕組みを構築します。</p><p class="omm-block-more"><a href="../model/system-reliability-management.html#transition-3-4">活用アクション・注意点メモ →</a></p></div>

## A3. [開発・運用プロセスの整備と最適化](../model/dev-ops-process-optimization.md#level-3)

<div class="omm-block omm-desc"><p class="omm-block-title">説明</p><p>CI/CDパイプラインが整備され、自動テストやステージング環境を活用して品質と本番環境の安定性を確保している。</p></div>

<div class="omm-block omm-example"><p class="omm-block-title">具体例</p><p>コードの変更がマージされると、単体テスト・統合テスト・リグレッションテストが自動で実行される仕組みを整備している。本番環境へのデプロイ前には影響評価も実施しており、リリースに伴う障害リスクを抑制している。</p></div>

<div class="omm-block omm-required"><p class="omm-block-title">レベル4 へ進むための改善アクション<span>必須</span></p><p>各プロセスフェーズでの成果物（例：設計書、テスト結果、リリースチェックリストなど）に対して、品質チェックポイント（例：レビュー項目、検証項目）を明確化し、ドキュメントや作業結果を客観的に評価できる基準を整備します。</p><p class="omm-block-more"><a href="../model/dev-ops-process-optimization.html#transition-3-4">活用アクション・注意点メモ →</a></p></div>

## A4. [アラート最適化と障害対応](../model/alert-optimization-and-incident-response.md#level-3)

<div class="omm-block omm-desc"><p class="omm-block-title">説明</p><p>動的しきい値や異常検知の仕組みを導入し、アラートの精度を向上させ、不要な通知を削減している。</p></div>

<div class="omm-block omm-example"><p class="omm-block-title">具体例</p><p>CPU・メモリ・ネットワークトラフィックなどの過去データを学習し、通常の変動範囲を自動で判断する異常検知アルゴリズムを導入している。これにより、しきい値の手動調整が不要になり、アラートノイズの大幅な削減を実現している。</p></div>

<div class="omm-block omm-required"><p class="omm-block-title">レベル4 へ進むための改善アクション<span>必須</span></p><p>重大な障害発生に備え、深刻度分類（SEVレベル）に応じた対応フローとエスカレーションパスを明文化します。特にSEV-1（致命的障害）に該当する事象については、即時エスカレーション・対応できる体制を確立します。</p><p class="omm-block-more"><a href="../model/alert-optimization-and-incident-response.html#transition-3-4">活用アクション・注意点メモ →</a></p></div>

## A5. [ユーザー行動の理解と最適化](../model/user-behavior-understanding.md#level-3)

<div class="omm-block omm-desc"><p class="omm-block-title">説明</p><p>ユーザー行動データをKPIとして活用し、継続的な機能改善やUX最適化を実施する仕組みが確立されている。</p></div>

<div class="omm-block omm-example"><p class="omm-block-title">具体例</p><p>コンバージョン率・リテンション率・セッション継続時間・アクティブユーザー数（DAU・WAU・MAU）・ユーザーフローなどをKPIとして設定し、定期的に分析している。これらのデータに基づき、機能改善やUI調整を継続的に実施している。</p></div>

<div class="omm-block omm-required"><p class="omm-block-title">レベル4 へ進むための改善アクション<span>必須</span></p><p>主要なユーザー行動パターン（例：ログイン頻度、動画視聴数など）ごとにKPI（例：継続率、エンゲージメント率など）を設定し、ダッシュボードで定期的にモニタリングできるようにします。さらに、行動データの傾向や異常をAI分析によって自動検出する仕組みを導入します。KPI変動の原因分析を効率化します。</p><p class="omm-block-more"><a href="../model/user-behavior-understanding.html#transition-3-4">活用アクション・注意点メモ →</a></p></div>

## A6. [継続的な改善と最適化](../model/continuous-improvement.md#level-3)

<div class="omm-block omm-desc"><p class="omm-block-title">説明</p><p>チーム全体で改善プロセスが明文化・体系化されており、継続的改善がプロジェクトの一部として定着している。</p></div>

<div class="omm-block omm-example"><p class="omm-block-title">具体例</p><p>開発速度、バグ修正率、デプロイ頻度などのKPIを設定し、その成果を定量的に測定している。これらの仕組みが組織として整備されており、継続的なプロセス改善を推進する体制を構築している。</p></div>

<div class="omm-block omm-required"><p class="omm-block-title">レベル4 へ進むための改善アクション<span>必須</span></p><p>定量データだけでなく、障害発生時の対応記録やリリース作業時のトラブル事例など、定性的な情報も収集・共有できる仕組みを整備します。改善事例をナレッジとして蓄積し、チーム内で学び合う文化を醸成します。</p><p class="omm-block-more"><a href="../model/continuous-improvement.html#transition-3-4">活用アクション・注意点メモ →</a></p></div>

