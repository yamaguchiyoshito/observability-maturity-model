<script setup lang="ts">
import { onMounted, onBeforeUnmount, reactive, computed, ref } from 'vue'
import { withBase } from 'vitepress'

/** 個人評価: マトリクス上で軸ごとに 1 レベル（または対象外）を選ぶ。記録はこのブラウザの localStorage にだけ保存する。 */
const KEY = 'omm-self-assessment-v1'
type Axis = { key: string; name: string; slug: string; cells: HTMLTableCellElement[] }
const axes: Axis[] = []
const levelNames = ref<Record<string, string>>({})
const state = reactive<{ target: string; updated: string | null; levels: Record<string, number>; ready: boolean }>({ target: '', updated: null, levels: {}, ready: false })
const copied = ref(false)
const cleanups: (() => void)[] = []

function load() {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return
    const data = JSON.parse(raw)
    if (data && typeof data === 'object') {
      state.target = typeof data.target === 'string' ? data.target : ''
      state.updated = typeof data.updated === 'string' ? data.updated : null
      if (data.levels && typeof data.levels === 'object') {
        for (const [k, lv] of Object.entries(data.levels)) if (Number.isInteger(lv) && (lv as number) >= 0 && (lv as number) <= 5) state.levels[k] = lv as number
      }
    }
  } catch { /* プライベートモード等で localStorage が使えない場合も、保存なしで動作する */ }
}
function save() {
  state.updated = new Date().toISOString()
  try { localStorage.setItem(KEY, JSON.stringify({ version: 1, target: state.target, updated: state.updated, levels: state.levels })) } catch { /* ignore */ }
}
function paint(a: Axis) {
  const lv = state.levels[a.key]
  a.cells.forEach((td) => td.setAttribute('aria-checked', lv !== undefined && Number(td.dataset.level) === lv ? 'true' : 'false'))
}
function select(a: Axis, lv: number) {
  if (state.levels[a.key] === lv) delete state.levels[a.key]; else state.levels[a.key] = lv // 同じセルの再クリックで解除
  save(); paint(a)
}
function clearAll() {
  if (!confirm('選択内容と評価対象名をすべて消去します。よろしいですか？')) return
  for (const k of Object.keys(state.levels)) delete state.levels[k]
  state.target = ''; state.updated = null
  try { localStorage.removeItem(KEY) } catch { /* ignore */ }
  axes.forEach(paint)
}
function onTargetChange(e: Event) { state.target = (e.target as HTMLInputElement).value.trim(); save() }

onMounted(() => {
  load()
  const table = document.querySelector<HTMLTableElement>('.omm-sa-table')
  if (!table) return
  try { levelNames.value = JSON.parse(table.dataset.levelNames || '{}') } catch { levelNames.value = {} }
  for (const tr of Array.from(table.querySelectorAll<HTMLTableRowElement>('tbody tr[data-axis]'))) {
    const a: Axis = { key: tr.dataset.axis!, name: tr.dataset.axisName || tr.dataset.axis!, slug: tr.dataset.axisSlug || '', cells: Array.from(tr.querySelectorAll<HTMLTableCellElement>('td.omm-sa-cell')) }
    a.cells.forEach((td) => {
      const lv = Number(td.dataset.level)
      const onClick = (e: Event) => { if ((e.target as HTMLElement).closest('a, summary, details')) return; select(a, lv) }
      const onKey = (e: KeyboardEvent) => { if (e.target === td && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); select(a, lv) } }
      td.addEventListener('click', onClick); td.addEventListener('keydown', onKey)
      cleanups.push(() => { td.removeEventListener('click', onClick); td.removeEventListener('keydown', onKey) })
    })
    axes.push(a); paint(a)
  }
  state.ready = true
})
onBeforeUnmount(() => cleanups.forEach((f) => f()))

const rows = computed(() => axes.map((a) => ({ ...a, level: state.levels[a.key] ?? null })))
const assessed = computed(() => rows.value.filter((r) => r.level !== null && r.level > 0))
const excluded = computed(() => rows.value.filter((r) => r.level === 0))
const pending = computed(() => rows.value.filter((r) => r.level === null))
const byLevel = computed(() => [1, 2, 3, 4, 5].map((lv) => ({ lv, name: levelNames.value[lv] || '', n: assessed.value.filter((r) => r.level === lv).length })))
const lowest = computed(() => {
  if (!assessed.value.length) return null
  const min = Math.min(...assessed.value.map((r) => r.level as number))
  return { min, axes: assessed.value.filter((r) => r.level === min) }
})
const updatedLabel = computed(() => {
  if (!state.updated) return '—'
  const d = new Date(state.updated); if (isNaN(d.getTime())) return '—'
  const p = (n: number) => (n < 10 ? '0' : '') + n
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
})
const markdown = computed(() => {
  const lines = [`# オブザーバビリティ成熟度 自己評価${state.target ? ': ' + state.target : ''}`, '', `- 評価日: ${(state.updated ?? new Date().toISOString()).slice(0, 10)}`, '', '| 評価軸 | レベル | 名称 |', '|---|---|---|']
  for (const r of rows.value) {
    const l = r.level === null ? '未選択' : r.level === 0 ? '対象外' : `レベル${r.level}`
    const n = r.level ? (levelNames.value[r.level] || '') : '—'
    lines.push(`| ${r.key}. ${r.name} | ${l} | ${n} |`)
  }
  lines.push('', '出典: DMM.com LLC オブザーバビリティ成熟度モデル（CC BY 4.0）')
  return lines.join('\n') + '\n'
})
async function copy() {
  try { await navigator.clipboard.writeText(markdown.value); copied.value = true; setTimeout(() => (copied.value = false), 2000) } catch { copied.value = false }
}
function axisLink(r: { slug: string }, hash = '') { return withBase(`/model/${r.slug}.html${hash}`) }
</script>

<template>
  <section class="omm-sa-summary" aria-labelledby="omm-sa-title">
    <h2 id="omm-sa-title" class="omm-sa-title">自己評価の記録と集計<span>この端末のブラウザにだけ保存されます</span></h2>
    <p class="omm-sa-help">下の表で、各評価軸の現状に最も近いレベルのセルを選んでください。同じセルをもう一度選ぶと解除されます。記録はサーバーに送られず、別の端末やブラウザには引き継がれません。確定した評価は<a :href="withBase('/assessment/report-template.html')">評価レポートテンプレート</a>に転記してください。</p>
    <div v-if="state.ready" class="omm-sa-body">
      <div class="omm-sa-meta">
        <label>評価対象 <input id="omm-sa-target" type="text" :value="state.target" placeholder="チーム名 / サービス名" maxlength="80" @change="onTargetChange"></label>
        <span class="omm-sa-updated">最終更新：{{ updatedLabel }}</span>
      </div>
      <div class="omm-sa-stats" role="group" aria-label="集計">
        <span class="stat stat-primary"><strong>{{ assessed.length }}<small>/{{ rows.length }}</small></strong>評価済み</span>
        <span class="stat"><strong>{{ excluded.length }}</strong>対象外</span>
        <span class="stat"><strong>{{ pending.length }}</strong>未選択</span>
        <span v-for="b in byLevel" :key="b.lv" class="stat"><strong>{{ b.n }}</strong>L{{ b.lv }} {{ b.name }}</span>
      </div>
      <table class="omm-sa-axes">
        <thead><tr><th>評価軸</th><th>選択レベル</th><th>次のレベルへ</th></tr></thead>
        <tbody>
          <tr v-for="r in rows" :key="r.key">
            <td>{{ r.key }}. <a :href="axisLink(r)">{{ r.name }}</a></td>
            <td>
              <span v-if="r.level === null" class="omm-lv-pill omm-lv-none">未選択</span>
              <span v-else-if="r.level === 0" class="omm-lv-pill omm-lv-none">対象外</span>
              <template v-else><span class="omm-lv-pill">L{{ r.level }}</span> {{ levelNames[r.level] }}</template>
            </td>
            <td>
              <a v-if="r.level && r.level < 5" :href="axisLink(r, `#transition-${r.level}-${r.level + 1}`)">L{{ r.level }}→L{{ r.level + 1 }} の改善アクション</a>
              <span v-else-if="r.level === 5">最高レベル</span>
              <span v-else>—</span>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="lowest" class="omm-sa-note">最も低い軸: {{ lowest.axes.map(a => `${a.key}. ${a.name}`).join('、') }}（L{{ lowest.min }}）。レベルは軸ごとに独立で、平均値は成熟度の指標として用いません。着手順は<a :href="withBase('/assessment/')">評価の進め方</a>を参照してください。</p>
      <div class="omm-sa-actions">
        <button type="button" class="omm-button" @click="copy">{{ copied ? 'コピーしました' : '集計を Markdown でコピー' }}</button>
        <button type="button" class="omm-button omm-button-danger" :disabled="assessed.length === 0 && excluded.length === 0 && !state.target" @click="clearAll">リセット</button>
      </div>
      <details class="omm-sa-markdown"><summary>Markdown で表示</summary><pre>{{ markdown }}</pre></details>
    </div>
  </section>
</template>
