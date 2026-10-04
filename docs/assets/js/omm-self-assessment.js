/* 個人評価ページ: セル選択・localStorage 保存・集計表示 */
(function () {
  'use strict';
  var root = document.getElementById('omm-sa');
  if (!root) return;

  var KEY = root.getAttribute('data-storage-key') || 'omm-self-assessment-v1';
  var table = root.querySelector('.omm-sa-table');
  var summaryEl = document.getElementById('omm-sa-summary');
  var targetInput = document.getElementById('omm-sa-target');
  var updatedEl = document.getElementById('omm-sa-updated');
  var levelNames = {};
  try { levelNames = JSON.parse(summaryEl.getAttribute('data-level-names') || '{}'); } catch (e) { levelNames = {}; }

  var rows = Array.prototype.slice.call(table.querySelectorAll('tbody tr[data-axis]'));
  var axes = rows.map(function (tr) {
    return { key: tr.getAttribute('data-axis'), name: tr.getAttribute('data-axis-name'), slug: tr.getAttribute('data-axis-slug'), tr: tr };
  });

  // ---------- 状態 ----------
  var state = { version: 1, target: '', updated: null, levels: {} };

  function load() {
    try {
      var raw = window.localStorage.getItem(KEY);
      if (!raw) return;
      var parsed = JSON.parse(raw);
      if (parsed && typeof parsed === 'object') {
        state.target = typeof parsed.target === 'string' ? parsed.target : '';
        state.updated = parsed.updated || null;
        state.levels = (parsed.levels && typeof parsed.levels === 'object') ? parsed.levels : {};
      }
    } catch (e) { /* private window などで localStorage が使えない場合は保存なしで動作 */ }
  }

  function save() {
    state.updated = new Date().toISOString();
    try { window.localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) { toast('この環境では保存できません（localStorage 無効）'); }
    render();
  }

  // ---------- 描画 ----------
  function levelLabel(lv) {
    if (lv === 0) return '対象外';
    return 'レベル' + lv + (levelNames[lv] ? '（' + levelNames[lv] + '）' : '');
  }

  function renderCells() {
    axes.forEach(function (a) {
      var selected = state.levels.hasOwnProperty(a.key) ? state.levels[a.key] : null;
      Array.prototype.forEach.call(a.tr.querySelectorAll('td.omm-sa-cell'), function (td) {
        var lv = parseInt(td.getAttribute('data-level'), 10);
        td.setAttribute('aria-checked', selected !== null && lv === selected ? 'true' : 'false');
      });
    });
  }

  function fmtDate(iso) {
    if (!iso) return '—';
    var d = new Date(iso);
    if (isNaN(d.getTime())) return '—';
    var p = function (n) { return (n < 10 ? '0' : '') + n; };
    return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate()) + ' ' + p(d.getHours()) + ':' + p(d.getMinutes());
  }

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; });
  }

  function renderSummary() {
    var assessed = axes.filter(function (a) { return state.levels.hasOwnProperty(a.key) && state.levels[a.key] > 0; });
    var excluded = axes.filter(function (a) { return state.levels[a.key] === 0; });
    var pending = axes.filter(function (a) { return !state.levels.hasOwnProperty(a.key); });

    if (assessed.length === 0 && excluded.length === 0) {
      summaryEl.innerHTML = '<p class="omm-muted">まだ選択がありません。上の表でセルをクリックしてください。</p>';
      return;
    }

    var html = '';
    html += '<p>評価済み <strong>' + assessed.length + '</strong> / ' + axes.length + ' 軸';
    if (excluded.length) html += '（対象外 ' + excluded.length + '）';
    if (pending.length) html += ' / 未選択: ' + pending.map(function (a) { return a.key; }).join(', ');
    html += '</p>';

    // 軸別
    html += '<table><thead><tr><th>評価軸</th><th>選択レベル</th><th>次のレベルへ</th></tr></thead><tbody>';
    axes.forEach(function (a) {
      var lv = state.levels.hasOwnProperty(a.key) ? state.levels[a.key] : null;
      var pill, next;
      if (lv === null) { pill = '<span class="omm-lv-pill omm-lv-none">未選択</span>'; next = '—'; }
      else if (lv === 0) { pill = '<span class="omm-lv-pill omm-lv-none">対象外</span>'; next = '—'; }
      else {
        pill = '<span class="omm-lv-pill">L' + lv + '</span> ' + esc(levelNames[lv] || '');
        next = lv < 5
          ? '<a href="model/' + a.slug + '.html#transition-' + lv + '-' + (lv + 1) + '">L' + lv + '→L' + (lv + 1) + ' の改善アクション</a>'
          : '最高レベル';
      }
      html += '<tr><td>' + a.key + '. <a href="model/' + a.slug + '.html">' + esc(a.name) + '</a></td><td>' + pill + '</td><td>' + next + '</td></tr>';
    });
    html += '</tbody></table>';

    // レベル分布
    html += '<h3>レベル分布</h3><table><tbody>';
    for (var lv = 1; lv <= 5; lv++) {
      var n = assessed.filter(function (a) { return state.levels[a.key] === lv; }).length;
      var pct = assessed.length ? Math.round(n / assessed.length * 100) : 0;
      html += '<tr><td style="white-space:nowrap">L' + lv + ' ' + esc(levelNames[lv] || '') + '</td>' +
        '<td><span class="omm-bar-track"><span class="omm-bar" style="width:' + pct + '%"></span></span>' + n + ' 軸</td></tr>';
    }
    html += '</tbody></table>';

    if (assessed.length) {
      var min = Math.min.apply(null, assessed.map(function (a) { return state.levels[a.key]; }));
      var lowest = assessed.filter(function (a) { return state.levels[a.key] === min; });
      html += '<p>最も低い軸: ' + lowest.map(function (a) { return a.key + '. ' + esc(a.name); }).join('、') + '（L' + min + '）。' +
        'レベルは軸ごとに独立で、平均値は成熟度の指標として用いません。着手順は <a href="assessment/">評価の進め方</a> を参照してください。</p>';
    }
    summaryEl.innerHTML = html;
  }

  function render() {
    renderCells();
    renderSummary();
    if (targetInput && targetInput.value !== state.target) targetInput.value = state.target;
    if (updatedEl) updatedEl.textContent = fmtDate(state.updated);
  }

  // ---------- 操作 ----------
  function select(axisKey, lv) {
    if (state.levels[axisKey] === lv) delete state.levels[axisKey]; // 同じセルの再クリックで解除
    else state.levels[axisKey] = lv;
    save();
  }

  table.addEventListener('click', function (e) {
    if (e.target.closest('summary, details, a')) return; // 具体例の開閉・リンクは選択にしない
    var td = e.target.closest('td.omm-sa-cell');
    if (!td) return;
    var tr = td.closest('tr[data-axis]');
    select(tr.getAttribute('data-axis'), parseInt(td.getAttribute('data-level'), 10));
  });
  table.addEventListener('keydown', function (e) {
    if (e.key !== 'Enter' && e.key !== ' ') return;
    var td = e.target.closest('td.omm-sa-cell');
    if (!td || e.target !== td) return;
    e.preventDefault();
    var tr = td.closest('tr[data-axis]');
    select(tr.getAttribute('data-axis'), parseInt(td.getAttribute('data-level'), 10));
  });

  if (targetInput) {
    targetInput.addEventListener('change', function () { state.target = targetInput.value.trim(); save(); });
  }

  var resetBtn = document.getElementById('omm-sa-reset');
  if (resetBtn) resetBtn.addEventListener('click', function () {
    if (!window.confirm('選択内容と評価対象名をすべて消去します。よろしいですか？')) return;
    state = { version: 1, target: '', updated: null, levels: {} };
    try { window.localStorage.removeItem(KEY); } catch (e) { /* noop */ }
    render();
  });

  function toMarkdown() {
    var lines = [];
    lines.push('# オブザーバビリティ成熟度 自己評価' + (state.target ? ': ' + state.target : ''));
    lines.push('');
    lines.push('- 評価日: ' + (state.updated ? state.updated.slice(0, 10) : new Date().toISOString().slice(0, 10)));
    lines.push('');
    lines.push('| 評価軸 | レベル | 名称 |');
    lines.push('|---|---|---|');
    axes.forEach(function (a) {
      var lv = state.levels.hasOwnProperty(a.key) ? state.levels[a.key] : null;
      var l = lv === null ? '未選択' : (lv === 0 ? '対象外' : 'レベル' + lv);
      var n = lv ? (levelNames[lv] || '') : '—';
      lines.push('| ' + a.key + '. ' + a.name + ' | ' + l + ' | ' + n + ' |');
    });
    lines.push('');
    lines.push('出典: DMM.com LLC オブザーバビリティ成熟度モデル（CC BY 4.0）');
    return lines.join('\n');
  }

  var copyBtn = document.getElementById('omm-sa-copy');
  if (copyBtn) copyBtn.addEventListener('click', function () {
    var md = toMarkdown();
    var done = function () { toast('集計を Markdown でコピーしました'); };
    var fail = function () { window.prompt('コピーできませんでした。以下を手動でコピーしてください。', md); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(md).then(done, fail);
    else fail();
  });

  var toastEl;
  function toast(msg) {
    if (!toastEl) { toastEl = document.createElement('div'); toastEl.className = 'omm-sa-toast'; document.body.appendChild(toastEl); }
    toastEl.textContent = msg;
    toastEl.classList.add('omm-show');
    clearTimeout(toastEl._t);
    toastEl._t = setTimeout(function () { toastEl.classList.remove('omm-show'); }, 2200);
  }

  load();
  render();
})();
