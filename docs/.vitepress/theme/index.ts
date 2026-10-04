import DefaultTheme from 'vitepress/theme'
import { h } from 'vue'
import Downloads from './Downloads.vue'
import MatrixAssessment from './MatrixAssessment.vue'
import SidebarToggle from './SidebarToggle.vue'
import './style.css'

export default {
  extends: DefaultTheme,
  Layout: () => h(DefaultTheme.Layout, null, {
    'sidebar-nav-before': () => h(SidebarToggle)
  }),
  enhanceApp({ app }) {
    app.component('Downloads', Downloads)
    app.component('MatrixAssessment', MatrixAssessment)
    // 全量マトリクス / 個人評価の「具体例をすべて開く／閉じる」ボタン（data-target 配下の details を一括開閉）
    if (typeof document !== 'undefined' && !(window as any).__ommExpandBound) {
      ;(window as any).__ommExpandBound = true
      document.addEventListener('click', (e) => {
        const button = (e.target as HTMLElement).closest<HTMLElement>('.omm-expand')
        if (!button) return
        const open = button.dataset.open === 'true'
        const scope = (button.dataset.target && document.querySelector(button.dataset.target)) || document
        scope.querySelectorAll('details').forEach((d) => { d.open = open })
      })
    }
  }
}
