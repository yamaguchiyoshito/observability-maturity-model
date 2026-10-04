import { defineConfig } from 'vitepress'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

const root = new URL('../../', import.meta.url)
// tools/build_docs.py が CSV から生成する。評価軸とレベルの一覧をサイドバーに使う。
const model = JSON.parse(readFileSync(new URL('build/model.json', root), 'utf8'))
const { version } = JSON.parse(readFileSync(new URL('package.json', root), 'utf8'))

// base: GitHub Actions では configure-pages が SITE_BASE_PATH を渡す。ローカルはリポジトリ名から決める。
const repository = process.env.GITHUB_REPOSITORY || ''
const [owner, repo] = repository.split('/')
const defaultBase = repo ? (repo.toLowerCase() === `${owner}.github.io`.toLowerCase() ? '/' : `/${repo}/`) : '/observability-maturity-model/'
const requestedBase = process.env.SITE_BASE_PATH ?? defaultBase
const base = '/' + requestedBase.replace(/^\/+|\/+$/g, '') + (requestedBase.replace(/\//g, '') ? '/' : '')
const origin = (process.env.SITE_ORIGIN || '').replace(/\/$/, '')
const upstream = 'https://github.com/dmm-com/observability-maturity-model'

const axes = model.axes.map((a: any) => ({ text: `${a.key}. ${a.name}`, link: `/model/${a.slug}` }))
const levels = model.cmmi_levels.map((l: any) => ({ text: `レベル${l.level}: ${l.name}`, link: `/levels/level-${l.level}` }))
const sidebar = [
  { text: 'はじめに', link: '/' },
  { text: '成熟度モデル', link: '/model/', items: axes },
  { text: '全量マトリクス', link: '/matrix' },
  { text: 'レベル別ビュー', link: '/levels/', collapsed: true, items: levels },
  { text: '個人評価', link: '/self-assessment' },
  { text: '評価の進め方', link: '/assessment/', items: [{ text: '評価レポートテンプレート', link: '/assessment/report-template' }] },
  { text: 'ダウンロード', link: '/downloads' }
]

export default defineConfig({
  lang: 'ja-JP',
  title: 'オブザーバビリティ成熟度モデル',
  titleTemplate: ':title | オブザーバビリティ成熟度モデル',
  description: '組織のオブザーバビリティ能力を 6 つの評価軸・5 段階のレベルで評価し、段階的な改善を支援する成熟度モデル（DMM.com 策定, CC BY 4.0）。',
  base,
  cleanUrls: false,
  appearance: true,
  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: `${base}favicon.svg` }],
    // 目次の標準/コンパクトを描画前に反映する（ダークモードと同じ方式）
    ['script', {}, "(()=>{try{document.documentElement.dataset.sidebar=localStorage.getItem('omm.sidebar')==='compact'?'compact':'full'}catch(e){}})()"]
  ],
  ...(origin ? { sitemap: { hostname: origin + base } } : {}),
  vite: { server: { fs: { allow: [fileURLToPath(root)] } } },
  themeConfig: {
    siteTitle: 'オブザーバビリティ成熟度モデル',
    nav: [
      { text: '成熟度モデル', link: '/model/', activeMatch: '/(model|levels)/' },
      { text: '全量マトリクス', link: '/matrix' },
      { text: '個人評価', link: '/self-assessment' },
      { text: '評価の進め方', link: '/assessment/', activeMatch: '/assessment/' },
      { text: 'ダウンロード', link: '/downloads' }
    ],
    sidebar,
    ...(repository
      ? { socialLinks: [{ icon: 'github', link: `https://github.com/${repository}` }], editLink: { pattern: `https://github.com/${repository}/edit/main/docs/:path`, text: 'GitHubで編集を提案' } }
      : { socialLinks: [{ icon: 'github', link: upstream }] }),
    outline: { level: [2, 3], label: 'このページの内容' },
    docFooter: { prev: '前のページ', next: '次のページ' },
    sidebarMenuLabel: '目次', returnToTopLabel: 'ページの先頭へ',
    darkModeSwitchLabel: '表示モード', lightModeSwitchTitle: 'ライトモード', darkModeSwitchTitle: 'ダークモード',
    skipToContentLabel: '本文へ移動',
    footer: {
      message: `成熟度モデル本文：DMM.com LLC「<a href="${upstream}" target="_blank" rel="noopener">オブザーバビリティ成熟度モデル</a>」（<a href="https://creativecommons.org/licenses/by/4.0/deed.ja" target="_blank" rel="noopener">CC BY 4.0</a>）。生成ページと評価ページは同ライセンス。`,
      copyright: `&copy; 2025 DMM.com LLC · サイト版 ${version}`
    },
    search: {
      provider: 'local',
      options: {
        locales: { root: { translations: {
          button: { buttonText: '検索', buttonAriaLabel: '文書を検索' },
          modal: { displayDetails: '詳細を表示', resetButtonTitle: '検索をクリア', backButtonTitle: '検索を閉じる', noResultsText: '結果が見つかりません', footer: { selectText: '選択', selectKeyAriaLabel: 'Enter', navigateText: '移動', navigateUpKeyAriaLabel: '上矢印', navigateDownKeyAriaLabel: '下矢印', closeText: '閉じる', closeKeyAriaLabel: 'Escape' } }
        } } },
        miniSearch: {
          options: {
            // VitePress はこの関数をブラウザ用に直列化する。外部参照を持たない自己完結の実装にすること。
            // 日本語は 1 文字と 2 文字（bigram）に分割し、英数字は単語単位で索引する。
            tokenize: (text: string) => {
              const input = text.normalize('NFKC').toLowerCase()
              const terms = new Set<string>()
              for (const match of input.matchAll(/[a-z0-9]+(?:[.\-][a-z0-9]+)*/g)) {
                terms.add(match[0])
                for (const part of match[0].split(/[.\-]/)) terms.add(part)
              }
              for (const match of input.matchAll(/[\p{Script=Han}\p{Script=Hiragana}\p{Script=Katakana}ー]+/gu)) {
                const chars = Array.from(match[0])
                for (let i = 0; i < chars.length; i++) {
                  terms.add(chars[i])
                  if (i + 1 < chars.length) terms.add(chars[i] + chars[i + 1])
                }
              }
              return [...terms]
            },
            processTerm: (term: string) => term.toLowerCase()
          },
          searchOptions: { prefix: true, fuzzy: false, combineWith: 'AND' }
        }
      }
    }
  }
})
