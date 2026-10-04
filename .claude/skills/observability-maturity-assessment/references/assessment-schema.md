# assessment.json スキーマ

`build_report.py` の入力。評価者（Claude / 人間）が書く唯一のファイル。モデル本文（レベル定義・改善アクション）はここに書かない（CSV から自動引用される）。

```json
{
  "target": {
    "name": "my-service",
    "url": "https://github.com/org/my-service",
    "path": "/path/to/clone",
    "commit": "abc1234",
    "branch": "main"
  },
  "assessed_at": "2026-10-04",
  "assessor": "Claude Code（observability-maturity-assessment スキル）— 下書き",
  "scope": "単一リポジトリ（Web バックエンド + Terraform）。組織横断の標準適用状況は未確認。",
  "axes": {
    "A1": {
      "level": 2,
      "confidence": "medium",
      "rationale": "Prometheus クライアントと構造化ログ（zap）が全サービスに導入され、Grafana ダッシュボードが dashboards/ にコード管理されているためレベル2の要件（基本的な収集・可視化の管理プロセス）は満たす。一方、DB 層とネットワーク層の収集設定が無く、ダッシュボードは単一チーム向けのため、レベル3（全層・組織標準）には達していないと判断した。",
      "evidence": [
        {"ref": "go.mod:14", "note": "github.com/prometheus/client_golang — メトリクス公開"},
        {"ref": "internal/log/logger.go:9", "note": "go.uber.org/zap による構造化ログ"},
        {"ref": "deploy/grafana/dashboards/api.json", "note": "ダッシュボードのコード管理（1 枚のみ）"}
      ],
      "gaps": [
        "DB・ネットワーク層の収集設定が無い",
        "ダッシュボードの共通テンプレート化・他チームとの共有が確認できない",
        "分散トレーシングが未導入"
      ],
      "unverified": [
        "収集手順書の有無と、担当・実施頻度の取り決め",
        "データ品質の点検を行っているか"
      ],
      "questions": [
        "メトリクス・ログ収集の担当者と点検頻度は決まっていますか",
        "DB・ネットワーク層のメトリクスは別の仕組みで収集していますか"
      ]
    },
    "A5": {
      "level": null,
      "confidence": "low",
      "rationale": "内部向け API サービスでエンドユーザー向け UI を持たないため、この軸は評価対象外とした。"
    }
  },
  "summary": "総評（任意）。全体傾向、強み、最初に取り組むべき軸。",
  "priorities": [
    {"axis": "A4", "theme": "アラートの棚卸しと重要度分類の導入", "reason": "固定しきい値アラートのみで severity が無く、A2 のインシデント対応整備の前提になるため"}
  ]
}
```

## フィールド

| パス | 必須 | 説明 |
|---|---|---|
| `target.name` | ✓ | 対象の表示名（リポジトリ名） |
| `target.url` / `path` / `commit` / `branch` | | 再現性のための識別情報。`scan_repo.py` の `evidence.json` → `meta` から転記する |
| `assessed_at` | | ISO 日付。省略時は生成日 |
| `assessor` | | 評価者。下書きであることを明記する |
| `scope` | 推奨 | 対象範囲と前提（モノレポの一部か、組織横断性は未確認か等） |
| `axes.<A1..A6>` | ✓（6 軸） | 軸ごとの評価。欠けた軸は「未評価」として出力される |
| `axes.*.level` | ✓ | `1`〜`5` の整数、または `null`（未評価／対象外） |
| `axes.*.confidence` | ✓ | `"high"` / `"medium"` / `"low"`。基準は `evidence-rubric.md` |
| `axes.*.rationale` | ✓ | 判定理由。**満たした要件**と**次レベルに達しない理由**の両方を書く（2〜5 文） |
| `axes.*.evidence[]` | ✓（level が数値のとき） | `{"ref": "path:line", "note": "何を示すか"}`。文字列でも可。証跡が無い判定は `confidence: "low"` |
| `axes.*.gaps[]` | 推奨 | 次のレベル定義と比べて不足している点 |
| `axes.*.unverified[]` | 推奨 | リポジトリから確認できない要件（運用実態・組織横断性） |
| `axes.*.questions[]` | | ヒアリング質問。省略時は `references/interview-questions.md` の既定質問が入る |
| `summary` | | 総評 |
| `priorities[]` | | 優先テーマ。`{"axis","theme","reason"}` または文字列 |

## 書き方の注意

- `rationale` にはモデル本文をコピーしない（レポートが CSV から引用する）。
- `evidence.ref` は `scan_repo.py` が出した `file:line` をそのまま使う。読者が検証できることが目的。
- 「〜と思われる」「〜の可能性が高い」で終わる判定は `confidence: "low"` にし、`questions` で確定手段を示す。
- レベル3以上を付けるときは `unverified` に必ず組織横断性（他チーム・他プロジェクトでの適用状況）を含める。
