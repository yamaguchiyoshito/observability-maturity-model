// サイトのビルド: CSV の整合性 → 生成物が CSV と同期しているか → ダウンロード用ファイル生成 → VitePress ビルド。
// GitHub Actions（.github/workflows/pages.yml, docs.yml）とローカル（npm run docs:build）で同じ手順を使う。
import { spawnSync } from 'node:child_process';
for (const [command, args] of [
  ['python3', ['.claude/skills/observability-maturity-assessment/scripts/omm_model.py', '--validate-only']],
  ['python3', ['tools/build_docs.py', '--check']],
  ['python3', ['tools/build_docs.py', '--downloads']],
  ['node', ['node_modules/vitepress/bin/vitepress.js', 'build', 'docs']]
]) {
  const result = spawnSync(command, args, { stdio: 'inherit', env: process.env });
  if (result.status !== 0) process.exit(result.status ?? 1);
}
