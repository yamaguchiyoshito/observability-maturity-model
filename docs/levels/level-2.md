---
title: "レベル2: プロセス確立"
---
<!-- このファイルは tools/build_docs.py が csv/ から生成しています。直接編集せず CSV を編集してください。 -->

# レベル2: プロセス確立

> **CMMI 上の定義**: プロジェクトレベルで基本的な管理プロセスが確立され、計画・監視・制御によって再現可能な成果が得られている。

## A1. [データ収集と可視化](../model/data-collection-and-visualization.md#level-2)

<div class="omm-block omm-desc"><p class="omm-block-title">説明</p><p>主要システムに対して、基本的なメトリクスやログの収集・可視化に関する管理プロセスが導入されている。収集手順や品質確認も実施されているが、データの統合やリアルタイム性には課題が残り、プロジェクト単位での実施にとどまっている。</p></div>

<div class="omm-block omm-example"><p class="omm-block-title">具体例</p><p>メトリクス収集・可視化の手順書を整備し、担当と実施頻度を明確にしている。アプリケーションやネットワークのデータはツールごとに分断されており、更新頻度が低いため即応性に欠けている。データ品質の点検も実施しているが、ツールや手法はチームごとに異なっており、一貫性は限定的である。</p></div>

<div class="omm-block omm-required"><p class="omm-block-title">レベル3 へ進むための改善アクション<span>必須</span></p><p>インフラ、アプリケーション、ネットワーク、データベース層を含むすべての主要なコンポーネントに対してモニタリング対象を拡張します。また、収集間隔を1分以内に設定するなど、リアルタイム性を意識したモニタリング体制を整備します。さらに、収集設定の見直しや、想定通りのメトリクスが取得・可視化できているかを定期的に確認し、設定漏れやタグ不足などによるモニタリングの抜けを防ぎます。</p><p class="omm-block-more"><a href="../model/data-collection-and-visualization.html#transition-2-3">活用アクション・注意点メモ →</a></p></div>

## A2. [システムの信頼性管理](../model/system-reliability-management.md#level-2)

<div class="omm-block omm-desc"><p class="omm-block-title">説明</p><p>監視ツールや対応手順書を活用した基本的なインシデント管理プロセスが整備されており、プロジェクトレベルで計画的な対応が行われている。稼働状況や応答時間など、監視指標や性能指標をもとに改善を試みる仕組みも導入されている。</p></div>

<div class="omm-block omm-example"><p class="omm-block-title">具体例</p><p>インシデントの記録やエスカレーション手順を文書化し、チーム内で一定のルールに従って対応している。可用性や性能に関する基本的な観測指標（システム稼働率、応答時間など）を明示し、定期的に見直している。</p></div>

<div class="omm-block omm-required"><p class="omm-block-title">レベル3 へ進むための改善アクション<span>必須</span></p><p>インシデントの検知・記録・分析・再発防止を一貫して扱う対応プロセスを標準化し、各チームで運用可能なテンプレート（例：リアルタイムインシデントレポート、ポストモーテム）を整備します。可用性やエラーレートなどの信頼性指標に基準値を設定し、定期レビューを実施します。特にMTTR、MTBF、可用性などの信頼性指標の測定・共有体制を整備します。システムリスク要因の一覧と評価基準を整備し、リスク度に応じた優先順位付けを行います。</p><p class="omm-block-more"><a href="../model/system-reliability-management.html#transition-2-3">活用アクション・注意点メモ →</a></p></div>

## A3. [開発・運用プロセスの整備と最適化](../model/dev-ops-process-optimization.md#level-2)

<div class="omm-block omm-desc"><p class="omm-block-title">説明</p><p>静的解析やコードレビューを導入し、一部の品質管理が実施されている。リリースも一定のスケジュールで管理されているが、運用にはばらつきがある。</p></div>

<div class="omm-block omm-example"><p class="omm-block-title">具体例</p><p>静的解析ツールを活用して最低限の品質チェックを自動化している。コードレビューを実施してバグの抑制に取り組んでいるが、レビュープロセスには一貫性がない。リリースは定期的に行っているものの、品質保証体制が不十分でスケジュールの遅延が発生している。</p></div>

<div class="omm-block omm-required"><p class="omm-block-title">レベル3 へ進むための改善アクション<span>必須</span></p><p>プロセスごとに標準的なテンプレートや手順書（例：設計書テンプレート、リリース手順書など）を整備し、誰が作業しても一定品質が保たれる基盤を作ります。また、手順の自動化と一貫性を確保するため、CI/CDパイプラインの整備または改善にも取り組みます。特に、リリースに関わる作業手順の標準化と自動化を優先します。</p><p class="omm-block-more"><a href="../model/dev-ops-process-optimization.html#transition-2-3">活用アクション・注意点メモ →</a></p></div>

## A4. [アラート最適化と障害対応](../model/alert-optimization-and-incident-response.md#level-2)

<div class="omm-block omm-desc"><p class="omm-block-title">説明</p><p>アラートの重要度や対象を整理し、しきい値調整などによるノイズ削減に取り組んでいるが、改善効果は限定的である。</p></div>

<div class="omm-block omm-example"><p class="omm-block-title">具体例</p><p>アラートの優先度を定義し、しきい値を調整することで通知量を削減しているが、負荷の急変には対応できず、ピーク時には誤検知や遅延が発生している。その結果、重要な異常の見逃しや対応の遅れが残っている。</p></div>

<div class="omm-block omm-required"><p class="omm-block-title">レベル3 へ進むための改善アクション<span>必須</span></p><p>システム全体に対してアラート対象を体系的に見直し、サービス、インフラ、ネットワーク層ごとに重要な監視指標を整理します。アラート発生時に確認すべきダッシュボードやログなど、初動対応に必要な情報セットも標準化します。さらに、動的しきい値や異常検知の仕組みを導入し、アラート精度の向上と不要通知の削減に取り組みます。</p><p class="omm-block-more"><a href="../model/alert-optimization-and-incident-response.html#transition-2-3">活用アクション・注意点メモ →</a></p></div>

## A5. [ユーザー行動の理解と最適化](../model/user-behavior-understanding.md#level-2)

<div class="omm-block omm-desc"><p class="omm-block-title">説明</p><p>ページビューやクリックなどの基本的な行動データを収集・可視化し、定量的な指標に基づく意思決定を開始している。</p></div>

<div class="omm-block omm-example"><p class="omm-block-title">具体例</p><p>Google Analyticsやアプリ内の簡易トラッキングを活用し、PV・UU・滞在時間などの基本的な行動指標を分析している。ただし、スクロール深度・クリック率・遷移パターンなどの詳細データは収集しておらず、具体的な改善に十分活かしきれていない。</p></div>

<div class="omm-block omm-required"><p class="omm-block-title">レベル3 へ進むための改善アクション<span>必須</span></p><p>ユーザー行動ログの収集範囲を拡大し、クリティカルユーザージャーニー（＝サービス提供側が特に重視する一連の操作）ごとにユーザーの遷移状況を可視化します。特に離脱ポイントを特定しやすいダッシュボードを整備し、ユーザー行動のボトルネックを把握することで、継続率や定着率の改善に役立てます。</p><p class="omm-block-more"><a href="../model/user-behavior-understanding.html#transition-2-3">活用アクション・注意点メモ →</a></p></div>

## A6. [継続的な改善と最適化](../model/continuous-improvement.md#level-2)

<div class="omm-block omm-desc"><p class="omm-block-title">説明</p><p>レビューやふりかえりを定期的に実施し、課題や改善点をチームで共有する文化が形成されつつある。</p></div>

<div class="omm-block omm-example"><p class="omm-block-title">具体例</p><p>開発チームが定期的に振り返りミーティングを実施し、プロセス上の課題を共有している。しかし、改善施策の優先順位が明確でなく、具体的なアクションに落とし込めておらず、同じ課題が繰り返し議論されている。</p></div>

<div class="omm-block omm-required"><p class="omm-block-title">レベル3 へ進むための改善アクション<span>必須</span></p><p>障害対応やリリース結果を定量的に振り返るため、基本的な運用指標（例：障害検知時間、復旧時間、リリース成功率など）を可視化し、チームで共有できるようにします。</p><p class="omm-block-more"><a href="../model/continuous-improvement.html#transition-2-3">活用アクション・注意点メモ →</a></p></div>

