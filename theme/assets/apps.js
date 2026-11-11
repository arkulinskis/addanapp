/* apps.js: drawing engine for the Apps area (#apps). Python passes plain data + callbacks; everything is built with
   createElement + textContent (no HTML strings), so app names and texts can't inject markup.
   apps.segs(el, [[state, color]])        the step strip on a card (state: done | na | todo)
   apps.chips(el, [{text, cls, title}])   tags;  apps.links(el, [{label, href, title}]) outside links
   apps.grid(host, model, cb)             the checklist grid (1,000+ tick squares, too many for Forms)
   apps.gridRow(host, row)                redraw one grid row in place
   apps.chart(el, pts, kind, color, h)    area or bar chart with a hover tooltip; apps.spark(el, values, color)
   apps.tip(text, evt) / apps.tipHide()   the shared tooltip */
(function () {
  'use strict';
  var NS = 'http://www.w3.org/2000/svg';
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = String(text);
    return e;
  }
  function svg(tag, attrs) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    return e;
  }
  function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); }
  function arr(x) { return x ? Array.prototype.slice.call(x) : []; }

  function segs(host, list) {
    clear(host);
    arr(list).forEach(function (s) {
      var sp = el('span', s[0] === 'todo' ? '' : s[0]);
      sp.style.setProperty('--c', s[1]);
      if (s[2]) sp.title = s[2];
      host.appendChild(sp);
    });
  }
  function chips(host, list) {
    clear(host);
    arr(list).forEach(function (c) {
      var sp = el('span', 'ap-tag ' + (c.cls || ''), c.text);
      if (c.title) sp.title = c.title;
      host.appendChild(sp);
    });
  }
  function links(host, list) {
    clear(host);
    arr(list).forEach(function (l) {
      var a = el('a', '', l.label);
      a.href = l.href;
      if (/^https?:/.test(l.href)) { a.target = '_blank'; a.rel = 'noopener'; }
      if (l.title) a.title = l.title;
      host.appendChild(a);
    });
  }

  // ---------- the grid ----------
  var MARK = {done: '✓', na: '–', todo: ''};
  function cell(row, col) {
    var v = (row.cells || {})[col.id] || 'todo', auto = !!(row.auto || {})[col.id];
    var b = el('button', 'ap-cell ' + (v === 'todo' ? '' : v) + (auto ? ' auto' : ''), MARK[v]);
    b.type = 'button';
    b.style.setProperty('--c', col.color);
    b.dataset.key = row.key; b.dataset.item = col.id;
    var what = v === 'na' ? 'not needed' : v === 'done' ? 'done' : 'to do';
    b.title = row.name + ' — ' + col.label + ': ' + what + (auto ? ' (found automatically)' : '') + '. Click to change.';
    b.setAttribute('aria-label', b.title);
    return b;
  }
  function baseCell(row, id) {
    var td = el('td');
    if (id === 'stage') {
      var s = el('span', 'ap-stage', row.stage_name);
      s.style.setProperty('--c', row.stage_color);
      td.className = 'stage';
      td.appendChild(s);
    } else if (id === 'live') {
      var d = el('span', 'ap-dot ' + (row.live === 'ok' ? 'ok' : row.live === 'bad' ? 'bad' : ''));
      d.title = row.live_title || '';
      d.setAttribute('role', 'img');
      d.setAttribute('aria-label', row.live_title || 'no live address');
      if (row.url) { var a = el('a'); a.href = row.url; a.target = '_blank'; a.rel = 'noopener'; a.appendChild(d); td.appendChild(a); }
      else td.appendChild(d);
    } else if (id === 'merge' && row.merge) {
      var m = el('button', 'ap-merge-pill', '⑂ ' + row.merge);
      m.type = 'button'; m.dataset.open = row.key; m.title = 'Branches to merge: ' + (row.merge_names || '');
      td.appendChild(m);
    }
    return td;
  }
  function rowEl(model, row) {
    var tr = el('tr');
    tr.dataset.row = row.key;
    var name = el('td', 'name'), a = el('a', '', row.name);
    a.href = '#app/' + encodeURIComponent(row.key);
    name.appendChild(a);
    tr.appendChild(name);
    arr(model.base).forEach(function (b) { tr.appendChild(baseCell(row, b.id)); });
    arr(model.cols).forEach(function (c) { var td = el('td'); td.appendChild(cell(row, c)); tr.appendChild(td); });
    return tr;
  }
  function th(model, id, label, extra) {
    var t = el('th', extra || '', label);
    t.dataset.sort = id;
    t.title = 'Sort by ' + label;
    t.setAttribute('scope', 'col');
    if (model.sort === id) {
      t.appendChild(el('span', 'arrow', model.dir > 0 ? '▲' : '▼'));
      t.setAttribute('aria-sort', model.dir > 0 ? 'ascending' : 'descending');
    }
    return t;
  }
  function grid(host, model, cb) {
    var wrap = host.querySelector('.ap-grid-wrap'), top = wrap ? wrap.scrollTop : 0, left = wrap ? wrap.scrollLeft : 0;
    clear(host);
    wrap = el('div', 'ap-grid-wrap');
    var table = el('table', 'ap-grid'), thead = el('thead'), r1 = el('tr'), r2 = el('tr'), tbody = el('tbody');
    var nm = th(model, 'name', 'App', 'name'); nm.rowSpan = 2; r1.appendChild(nm);
    arr(model.base).forEach(function (b) { var x = th(model, b.id, b.label); x.rowSpan = 2; r1.appendChild(x); });
    arr(model.phases).forEach(function (p) {
      var x = el('th', 'ph', p.name); x.colSpan = p.n; x.style.setProperty('--c', p.color); r1.appendChild(x);
    });
    arr(model.cols).forEach(function (c) { r2.appendChild(th(model, c.id, c.short || c.label)); });
    thead.appendChild(r1); thead.appendChild(r2);
    arr(model.rows).forEach(function (row) { tbody.appendChild(rowEl(model, row)); });
    if (!model.rows || !model.rows.length) {
      var tr = el('tr'), td = el('td', 'name', 'No apps match these filters.');
      td.colSpan = 1 + arr(model.base).length + arr(model.cols).length; tr.appendChild(td); tbody.appendChild(tr);
    }
    table.appendChild(thead); table.appendChild(tbody); wrap.appendChild(table); host.appendChild(wrap);
    wrap.scrollTop = top; wrap.scrollLeft = left;
    host._model = model;
    host.onclick = function (e) {
      var c = e.target.closest('.ap-cell');
      if (c) { cb.cell(c.dataset.key, c.dataset.item); return; }
      var s = e.target.closest('th[data-sort]');
      if (s) { cb.sort(s.dataset.sort); return; }
      var o = e.target.closest('[data-open]');
      if (o) { cb.open(o.dataset.open); }
    };
  }
  function gridRow(host, row) {
    var model = host._model, tr = host.querySelector('tr[data-row="' + CSS.escape(row.key) + '"]');
    if (!model || !tr) return false;
    var focused = document.activeElement && document.activeElement.dataset ? document.activeElement.dataset.item : null;
    var fresh = rowEl(model, row);
    tr.replaceWith(fresh);
    if (focused) { var f = fresh.querySelector('[data-item="' + CSS.escape(focused) + '"]'); if (f) f.focus(); }
    return true;
  }

  // ---------- tooltip + charts ----------
  var tipEl = null;
  function tip(text, e) {
    if (!tipEl) { tipEl = el('div', 'ap-tip'); tipEl.setAttribute('role', 'tooltip'); document.body.appendChild(tipEl); }
    if (!text) { tipEl.style.display = 'none'; return; }
    tipEl.textContent = text; tipEl.style.display = 'block';
    var w = tipEl.offsetWidth, x = e.clientX + 14 + w > innerWidth ? e.clientX - w - 14 : e.clientX + 14;
    tipEl.style.left = x + 'px'; tipEl.style.top = (e.clientY + 14) + 'px';
  }
  function tipHide() { if (tipEl) tipEl.style.display = 'none'; }
  function short(n) {
    return n >= 1e6 ? (n / 1e6).toFixed(n >= 1e7 ? 0 : 1) + 'M' : n >= 1e4 ? Math.round(n / 1e3) + 'k' : n >= 1e3 ? (n / 1e3).toFixed(1) + 'k' : String(Math.round(n));
  }
  function ticks(max) {
    if (max <= 0) return [0, 1];
    var raw = max / 3, mag = Math.pow(10, Math.floor(Math.log10(raw)));
    var step = [1, 2, 5, 10].map(function (m) { return m * mag; }).find(function (s) { return s >= raw; });
    var t = []; for (var v = 0; v <= max + step * .001; v += step) t.push(v);
    if (t[t.length - 1] < max) t.push(t[t.length - 1] + step);
    return t;
  }
  function chart(host, ptsIn, kind, color, H) {
    var pts = arr(ptsIn);
    H = H || 190; clear(host);
    if (!pts.length) { host.appendChild(el('p', 'ap-hint', 'No days to show yet.')); return; }
    var W = Math.max(280, host.clientWidth || 360), L = 40, R = 8, T = 8, B = 22, iw = W - L - R, ih = H - T - B;
    var tk = ticks(Math.max.apply(null, pts.map(function (p) { return p.y; }))), max = tk[tk.length - 1] || 1, n = pts.length;
    var X = function (i) { return kind === 'bars' ? L + (i + .5) * iw / n : L + (n === 1 ? iw / 2 : i * iw / (n - 1)); };
    var Y = function (v) { return T + ih - v / max * ih; };
    var s = svg('svg', {viewBox: '0 0 ' + W + ' ' + H, height: H, role: 'img'});
    s.setAttribute('aria-label', kind === 'bars' ? 'Bar chart' : 'Line chart');
    tk.forEach(function (t) {
      s.appendChild(svg('line', {x1: L, x2: W - R, y1: Y(t), y2: Y(t), stroke: 'var(--line)', 'stroke-width': 1}));
      var tx = svg('text', {x: L - 6, y: Y(t) + 4, 'text-anchor': 'end'}); tx.textContent = short(t); s.appendChild(tx);
    });
    var every = Math.max(1, Math.ceil(n / Math.max(2, Math.floor(iw / 70))));
    pts.forEach(function (p, i) {
      if (i % every) return;
      var tx = svg('text', {x: X(i), y: H - 6, 'text-anchor': 'middle'}); tx.textContent = p.x; s.appendChild(tx);
    });
    if (kind === 'bars') {
      var bw = Math.max(1, Math.min(22, iw / n - 2));
      pts.forEach(function (p, i) {
        var h = Math.max(p.y > 0 ? 1 : 0, ih - (Y(p.y) - T));
        s.appendChild(svg('rect', {x: X(i) - bw / 2, y: T + ih - h, width: bw, height: h, rx: Math.min(4, bw / 2), fill: color}));
      });
    } else {
      var d = pts.map(function (p, i) { return (i ? 'L' : 'M') + X(i).toFixed(1) + ',' + Y(p.y).toFixed(1); }).join('');
      s.appendChild(svg('path', {d: d + 'L' + X(n - 1) + ',' + (T + ih) + 'L' + X(0) + ',' + (T + ih) + 'Z', fill: color, opacity: .12}));
      s.appendChild(svg('path', {d: d, fill: 'none', stroke: color, 'stroke-width': 2, 'stroke-linejoin': 'round', 'stroke-linecap': 'round'}));
    }
    var xh = svg('line', {x1: 0, x2: 0, y1: T, y2: T + ih, stroke: 'var(--line-2)', 'stroke-width': 1, visibility: 'hidden'});
    s.appendChild(xh);
    s.appendChild(svg('rect', {x: L, y: 0, width: iw, height: H, fill: 'transparent'}));
    s.addEventListener('mousemove', function (e) {
      var r = s.getBoundingClientRect(), mx = (e.clientX - r.left) * W / r.width;
      var i = Math.max(0, Math.min(n - 1, kind === 'bars' ? Math.floor((mx - L) / (iw / n)) : Math.round((mx - L) / (iw / Math.max(1, n - 1)))));
      xh.setAttribute('x1', X(i)); xh.setAttribute('x2', X(i)); xh.setAttribute('visibility', 'visible');
      tip(pts[i].tip, e);
    });
    s.addEventListener('mouseleave', function () { xh.setAttribute('visibility', 'hidden'); tipHide(); });
    host.appendChild(s);
  }
  function spark(host, valuesIn, color) {
    var h = arr(valuesIn); clear(host);
    if (h.length < 2) { host.textContent = '–'; return; }
    var mn = Math.min.apply(null, h), mx = Math.max.apply(null, h), W = 70, H = 18;
    var d = h.map(function (v, i) { return (i ? 'L' : 'M') + (i * W / (h.length - 1)).toFixed(1) + ',' + (H - 2 - (mx === mn ? .5 : (v - mn) / (mx - mn)) * (H - 4)).toFixed(1); }).join('');
    var s = svg('svg', {width: W, height: H, viewBox: '0 0 ' + W + ' ' + H, 'aria-hidden': 'true'});
    s.appendChild(svg('path', {d: d, fill: 'none', stroke: color || 'var(--ap-s1)', 'stroke-width': 1.5}));
    host.appendChild(s);
  }
  function hoverTip(node, text) {
    node.addEventListener('mousemove', function (e) { tip(text, e); });
    node.addEventListener('mouseleave', tipHide);
  }

  // ---------- a plain data table: cols [{key, label, num, sort}], rows [[cell]] with cell = text or
  // {text, href, img, alt, spark: [numbers], tag, num} ; cb.sort(key) when a sortable header is clicked
  function table(host, colsIn, rowsIn, cb, cls) {
    var cols = arr(colsIn), rows = arr(rowsIn);
    clear(host);
    var t = el('table', cls || ''), thead = el('thead'), hr = el('tr'), tb = el('tbody');
    cols.forEach(function (c) {
      var h = el('th', c.num ? 'num' : '', c.label);
      h.setAttribute('scope', 'col');
      if (c.sort && cb) { h.dataset.sort = c.key; h.title = 'Sort by ' + c.label; h.tabIndex = 0; }
      if (c.on) h.setAttribute('aria-sort', c.on > 0 ? 'ascending' : 'descending');
      hr.appendChild(h);
    });
    thead.appendChild(hr);
    rows.forEach(function (r) {
      var tr = el('tr');
      arr(r).forEach(function (c, i) {
        var td = el('td', (cols[i] && cols[i].num) ? 'num' : (cols[i] && cols[i].cls) || '');
        if (c === null || c === undefined) { tr.appendChild(td); return; }
        if (typeof c !== 'object') { td.textContent = String(c); tr.appendChild(td); return; }
        if (c.img) { var im = el('img'); im.src = c.img; im.alt = c.alt || ''; im.loading = 'lazy'; td.appendChild(im); }
        else if (c.spark) { spark(td, c.spark); }
        else if (c.href) {
          var a = el('a', '', c.text); a.href = c.href;
          if (/^https?:/.test(c.href)) { a.target = '_blank'; a.rel = 'noopener'; }
          if (c.title) a.title = c.title;
          td.appendChild(a);
        } else td.textContent = c.text == null ? '' : String(c.text);
        if (c.tag) { td.appendChild(document.createTextNode(' ')); td.appendChild(el('span', 'ap-tag', c.tag)); }
        if (c.bold) td.style.fontWeight = '700';
        tr.appendChild(td);
      });
      tb.appendChild(tr);
    });
    t.appendChild(thead); t.appendChild(tb); host.appendChild(t);
    if (cb) {
      var go = function (e) { var h = e.target.closest('th[data-sort]'); if (h) cb.sort(h.dataset.sort); };
      thead.addEventListener('click', go);
      thead.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go(e); } });
    }
  }
  // one row of stacked bars: [{w (0-100), color}]
  function track(host, partsIn) {
    clear(host);
    arr(partsIn).forEach(function (p) { var s = el('span'); s.style.width = p.w + '%'; s.style.background = p.color; host.appendChild(s); });
  }

  window.apps = {segs: segs, chips: chips, links: links, grid: grid, gridRow: gridRow, chart: chart, spark: spark,
                 tip: tip, tipHide: tipHide, hoverTip: hoverTip, short: short, table: table, track: track};
})();
