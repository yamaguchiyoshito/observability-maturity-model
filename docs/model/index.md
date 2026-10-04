---
title: "成熟度モデル"
nav_order: 2
has_children: true
permalink: "/model/"
---
<!-- このファイルは tools/build_docs.py が csv/ から生成しています。直接編集せず CSV を編集してください。 -->

# オブザーバビリティ成熟度モデル

組織のオブザーバビリティ能力を 6 つの評価軸で測定するための評価基準です。各軸はレベル1（属人的）からレベル5（継続的最適化）までの状態を定義しています。

## 名称定義

- **組織**: 複数のチームやプロジェクトを包含し、それらの活動を統括・管理する組織単位。事業部、グループ、部門などの組織階層を指します。
- **チーム**: 共通の目標に向かって協働する機能的または役割的に編成されたメンバーグループ。開発チーム、運用チーム、SREチームなどを含み、1つまたは複数のプロジェクトに所属することがあります。
- **プロジェクト**: 特定の目標を達成するために、期間やスコープが明確に定められた活動単位。システム開発、サービス改善、インフラ構築など、特定の成果物を目的とした個別の取り組みを指します。
- **サービス**: エンドユーザーまたは他のシステムに対して特定の価値や機能を提供するシステムまたはアプリケーションを指します。

## 成熟度レベル（CMMI に基づく 5 段階）

| レベル | 名称 | 説明 |
|---|---|---|
| [レベル1](../levels/level-1.md) | 属人的 | プロセスは未定義で場当たり的に運用されており、成功は主に個々の能力や努力に依存している。 |
| [レベル2](../levels/level-2.md) | プロセス確立 | プロジェクトレベルで基本的な管理プロセスが確立され、計画・監視・制御によって再現可能な成果が得られている。 |
| [レベル3](../levels/level-3.md) | 組織標準化 | 組織全体で標準化されたプロセスが定義・文書化され、全プロジェクトで一貫して適用されている。 |
| [レベル4](../levels/level-4.md) | 定量管理 | プロセスのパフォーマンスが統計的手法により定量的に測定・制御されており、予測可能かつ安定した成果が得られている。 |
| [レベル5](../levels/level-5.md) | 継続的最適化 | 継続的な改善と技術革新が組織文化として確立され、プロセスの有効性と適応力が継続的に向上している。 |

## 評価軸

各軸のページでは、レベルごとの「説明」「具体例」と、次のレベルへ進むための「改善アクション（必須）」「活用アクション（推奨）」「注意点メモ」を続けて読めます。

### A1. [データ収集と可視化](data-collection-and-visualization.md)

システムのあらゆる領域に関するデータを網羅的に収集し、リアルタイムで可視化・分析できる能力。

### A2. [システムの信頼性管理](system-reliability-management.md)

システムの可用性や性能を維持・向上するために、障害対応・復旧プロセスを整備し、観測指標に基づく信頼性評価とリスク要因の改善を継続的に実施する能力。

### A3. [開発・運用プロセスの整備と最適化](dev-ops-process-optimization.md)

コードの品質を維持したまま、予測可能で安定したデリバリーを実現する能力。

### A4. [アラート最適化と障害対応](alert-optimization-and-incident-response.md)

システムの異常を適切に検知し、ノイズを抑えながら迅速な対応を実現する能力。

### A5. [ユーザー行動の理解と最適化](user-behavior-understanding.md)

ユーザーの利用状況やニーズを把握し、システムの改善に反映する能力。

※ここでの「ユーザー」とは、サービスを実際に利用する人間を指しますが、APIクライアントなども人の行動を代理する場合や分析対象として妥当な場合には含まれることがあります。

### A6. [継続的な改善と最適化](continuous-improvement.md)

モニタリングや開発プロセスのデータを活用し、チーム全体で継続的な改善を推進する能力。

## レベル一覧（6 軸 × 5 レベル）

セルをクリックすると各軸ページの該当レベルに移動します。

| 評価軸 | L1 属人的 | L2 プロセス確立 | L3 組織標準化 | L4 定量管理 | L5 継続的最適化 |
|---|---|---|---|---|---|
| [データ収集と可視化](data-collection-and-visualization.md) | [データ収集と可視化は個人の裁量に依存しており、対象範囲や…](data-collection-and-visualization.md#level-1) | [主要システムに対して、基本的なメトリクスやログの収集・可…](data-collection-and-visualization.md#level-2) | [組織標準として統一されたデータ収集・可視化プロセスが文書…](data-collection-and-visualization.md#level-3) | [データ収集・可視化のパフォーマンスがKPIや統計的手法に…](data-collection-and-visualization.md#level-4) | [AI・機械学習による予測分析と最適化の仕組みが確立されて…](data-collection-and-visualization.md#level-5) |
| [システムの信頼性管理](system-reliability-management.md) | [障害対応は個人の経験と判断に依存しており、対応手順や評価…](system-reliability-management.md#level-1) | [監視ツールや対応手順書を活用した基本的なインシデント管理…](system-reliability-management.md#level-2) | [組織全体で標準化されたインシデント対応プロセスおよびシス…](system-reliability-management.md#level-3) | [観測された信頼性指標（例：稼働率、障害件数、対応時間など…](system-reliability-management.md#level-4) | [観測データのAI・機械学習による高度な分析が自律的に実行…](system-reliability-management.md#level-5) |
| [開発・運用プロセスの整備と最適化](dev-ops-process-optimization.md) | [コード品質の基準やレビュー体制が整備されておらず、開発お…](dev-ops-process-optimization.md#level-1) | [静的解析やコードレビューを導入し、一部の品質管理が実施さ…](dev-ops-process-optimization.md#level-2) | [CI/CDパイプラインが整備され、自動テストやステージン…](dev-ops-process-optimization.md#level-3) | [コード品質やリリースの結果をKPIとして定量的に測定し、…](dev-ops-process-optimization.md#level-4) | [AIによるコード解析と変更影響分析により、リスクやバグを…](dev-ops-process-optimization.md#level-5) |
| [アラート最適化と障害対応](alert-optimization-and-incident-response.md) | [固定しきい値のアラートのみで運用されており、誤検知・見逃…](alert-optimization-and-incident-response.md#level-1) | [アラートの重要度や対象を整理し、しきい値調整などによるノ…](alert-optimization-and-incident-response.md#level-2) | [動的しきい値や異常検知の仕組みを導入し、アラートの精度を…](alert-optimization-and-incident-response.md#level-3) | [アラート履歴や影響度をもとに、AIによる優先度付けや自動…](alert-optimization-and-incident-response.md#level-4) | [異常検知から原因推定、対処アクションの実行までを自動化し…](alert-optimization-and-incident-response.md#level-5) |
| [ユーザー行動の理解と最適化](user-behavior-understanding.md) | [ユーザーの行動ログをほとんど収集しておらず、分析も実施さ…](user-behavior-understanding.md#level-1) | [ページビューやクリックなどの基本的な行動データを収集・可…](user-behavior-understanding.md#level-2) | [ユーザー行動データをKPIとして活用し、継続的な機能改善…](user-behavior-understanding.md#level-3) | [機械学習を活用してユーザー属性や行動パターンを分類・予測…](user-behavior-understanding.md#level-4) | [行動分析から改善提案・施策適用までのフィードバックループ…](user-behavior-understanding.md#level-5) |
| [継続的な改善と最適化](continuous-improvement.md) | [改善活動は担当者の裁量に任されており、仕組み化されていな…](continuous-improvement.md#level-1) | [レビューやふりかえりを定期的に実施し、課題や改善点をチー…](continuous-improvement.md#level-2) | [チーム全体で改善プロセスが明文化・体系化されており、継続…](continuous-improvement.md#level-3) | [改善指標（KPI）やログデータを活用し、改善サイクル（P…](continuous-improvement.md#level-4) | [AIが改善対象やアクションを自動で特定・提案・実行し、最…](continuous-improvement.md#level-5) |

## 横断ビュー

「いま組織全体がレベル2なら、レベル3とはどんな状態か」を軸をまたいで読みたいときは [レベル別ページ](../levels/) を使ってください。

