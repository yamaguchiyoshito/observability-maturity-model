<script setup lang="ts">
import { withBase } from 'vitepress'
// tools/build_docs.py --downloads が csv/ と pdf/ から docs/public/downloads/ に複製し、manifest.json を書く。
import manifest from '../../public/downloads/manifest.json'
</script>
<template>
  <p class="download-version">生成元コミット {{ manifest.commit.slice(0, 12) }} · 生成日時（UTC）{{ manifest.generatedAt }}</p>
  <ul class="downloads-list">
    <li v-for="file in manifest.files" :key="file.name">
      <a :href="withBase('/downloads/' + file.name)" :download="file.name">
        <strong>{{ file.title }}</strong>
        <span>{{ file.description }} · {{ Math.ceil(file.bytes / 1024) }} KB</span>
      </a>
    </li>
  </ul>
  <details class="download-provenance">
    <summary>ファイルの検証</summary>
    <p><a :href="withBase('/downloads/manifest.json')" download="manifest.json">生成元コミット・SHA-256 を記録した manifest.json</a></p>
  </details>
</template>
