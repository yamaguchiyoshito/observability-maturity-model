/* サイト共通: 左ペインの標準/コンパクト切替、details の一括開閉 */
(function () {
  'use strict';
  var NAV_KEY = 'omm-nav-compact';
  var html = document.documentElement;

  function isCompact() { return html.classList.contains('omm-nav-compact'); }
  function setCompact(on) {
    html.classList.toggle('omm-nav-compact', on);
    try { window.localStorage.setItem(NAV_KEY, on ? '1' : '0'); } catch (e) { /* noop */ }
    updateButtons();
  }
  var buttons = [];
  function updateButtons() {
    buttons.forEach(function (b) {
      b.setAttribute('aria-pressed', isCompact() ? 'true' : 'false');
      b.title = isCompact() ? '左ペインの目次を表示する' : '左ペインの目次を畳んで本文を全幅にする';
      b.innerHTML = '<span class="omm-nav-toggle-icon" aria-hidden="true">' + (isCompact() ? '▸' : '◂') + '</span>' +
        '目次: ' + (isCompact() ? 'コンパクト' : '標準');
    });
  }
  function makeButton() {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'omm-nav-toggle';
    b.addEventListener('click', function () { setCompact(!isCompact()); });
    buttons.push(b);
    return b;
  }

  function init() {
    // just-the-docs のヘッダ（検索 + aux links）の先頭に置く。無ければ本文の先頭。
    var header = document.querySelector('.main-header');
    var btn = makeButton();
    if (header) header.insertBefore(btn, header.firstChild);
    else {
      var main = document.querySelector('.main-content');
      if (main) main.insertBefore(btn, main.firstChild);
    }
    updateButtons();

    // details の一括開閉（全量マトリクス / 個人評価）
    document.addEventListener('click', function (e) {
      var b = e.target.closest('.omm-expand');
      if (!b) return;
      var open = b.getAttribute('data-open') === 'true';
      var scope = document.querySelector(b.getAttribute('data-target')) || document;
      Array.prototype.forEach.call(scope.querySelectorAll('details'), function (d) { d.open = open; });
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
