/* app-kit.js: small browser helpers Python reaches through window.UI: browser storage, the icon table
   (tools/build_icons.py makes icons.css from it), the translator for template text (UI.tr) and accessibility glue.
   The app itself is Python Forms; page effects (scroll reveal, smooth scroll, page meta, header spy) live in aa.js. */
(function () {
  'use strict';
  var UI = window.UI = window.UI || {};
  UI.config = { key: 'aa' };   // prefix for this app's browser storage ("aa.guides", ...)
  UI.esc = function (s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  };
  UI.store = {
    get: function (k, dflt) { try { var v = localStorage.getItem(UI.config.key + '.' + k); return v == null ? dflt : JSON.parse(v); } catch (e) { return dflt; } },
    set: function (k, v) { try { localStorage.setItem(UI.config.key + '.' + k, JSON.stringify(v)); } catch (e) {} }
  };
  /* Lucide-style stroke icons (24 x 24). <i class="ic ic-NAME"></i> in a template, role ic-NAME on a Button / Link. */
  UI.ICONS = {
    'check': '<path d="M20 6 9 17l-5-5"/>',
    'check-circle': '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
    'x': '<path d="M18 6 6 18M6 6l12 12"/>',
    'minus-circle': '<circle cx="12" cy="12" r="10"/><path d="M8 12h8"/>',
    'sparkle': '<path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/><path d="M19 3v4M17 5h4"/>',
    'shield': '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
    'badge': '<path d="M12 2l2.4 2.1 3.2-.3.9 3.1 2.8 1.6-1.2 3 1.2 3-2.8 1.6-.9 3.1-3.2-.3L12 22l-2.4-2.1-3.2.3-.9-3.1L2.7 15.5l1.2-3-1.2-3 2.8-1.6.9-3.1 3.2.3z"/><path d="m9 12 2 2 4-4"/>',
    'user': '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    'users': '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    'message': '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    'file': '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/>',
    'layout': '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/>',
    'plug': '<path d="M12 22v-5M9 8V2M15 8V2M18 8v5a6 6 0 0 1-12 0V8z"/>',
    'database': '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/><path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"/>',
    'sliders': '<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6"/>',
    'phone': '<rect x="5" y="2" width="14" height="20" rx="2.5"/><path d="M11 18h2"/>',
    'game': '<rect x="2" y="6" width="20" height="12" rx="5"/><path d="M6 12h4M8 10v4M15 13h.01M18 11h.01"/>',
    'globe': '<circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15 15 0 0 1 4 10 15 15 0 0 1-4 10 15 15 0 0 1-4-10 15 15 0 0 1 4-10z"/>',
    'bot': '<rect x="3" y="8" width="18" height="12" rx="3"/><path d="M12 8V4M9 4h6M8.5 14h.01M15.5 14h.01M9.5 17.5h5"/>',
    'target': '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    'code': '<path d="m16 18 6-6-6-6M8 6l-6 6 6 6"/>',
    'eye': '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    'mail': '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
    'pin': '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>',
    'clock': '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    'lock': '<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    'key': '<circle cx="7.5" cy="15.5" r="5.5"/><path d="m21 2-9.6 9.6M15.5 7.5l3 3L22 7l-3-3"/>',
    'receipt': '<path d="M4 2v20l3-2 3 2 3-2 3 2 3-2 2 2V2l-2 2-3-2-3 2-3-2-3 2-3-2z"/><path d="M16 8H8M16 12H8M12 16H8"/>',
    'lang': '<path d="m5 8 6 6M4 14l6-6 2-3M2 5h12M7 2h1M22 22l-5-10-5 10M14 18h6"/>',
    'bell': '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>',
    'plus': '<path d="M12 5v14M5 12h14"/>',
    'arrow': '<path d="M5 12h14M12 5l7 7-7 7"/>',
    'arrow-ur': '<path d="M7 17 17 7M7 7h10v10"/>',
    'inbox': '<path d="M22 12h-6l-2 3h-4l-2-3H2"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/>',
    'flag': '<path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1zM4 22v-7"/>',
    'help': '<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3M12 17h.01"/>',
    'activity': '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    'rocket': '<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>',
    'pen': '<path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4z"/>',
    'grid': '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
    'list': '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
    'columns': '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 3v18M15 3v18"/>',
    'zap': '<path d="M13 2 3 14h9l-1 8 10-12h-9z"/>',
    'trash': '<path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>',
    'refresh': '<path d="M21 12a9 9 0 1 1-3-6.7L21 8"/><path d="M21 3v5h-5"/>',
    'logout': '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>',
    'home': '<path d="m3 10 9-7 9 7v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/>',
    'calendar': '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    'chev-down': '<path d="m6 9 6 6 6-6"/>',
    'play': '<rect x="2" y="4" width="20" height="16" rx="4"/><path d="m10 9 5 3-5 3z"/>',
    'briefcase': '<rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2M2 13h20"/>'
  };
  UI.icon = function (name, cls) {
    return '<svg class="ui-ic ' + (cls || '') + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" ' +
      'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + (UI.ICONS[name] || '') + '</svg>';
  };
  UI.reducedMotion = function () { return !!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches); };

  /* Translations of template text. Form templates hold the English text; an element marked data-t gets its inner HTML
     swapped for the visitor's language from the language pack (window.AA_PACK, keyed by the English text, loaded by the
     head script). data-tv="n:products" fills {n} from the vars Python passes (i18n.apply(self, products=53)).
     data-ta="aria-label,title" translates those attributes. English needs no pack: only the {placeholders} are filled.
     Keys missing from a pack are listed in UI.trMissing (the UI tests check it stays empty). */
  UI.trMissing = [];
  function pick(key) {
    var pack = window.AA_PACK;
    if (!pack) return key;
    var v = pack[key];
    if (Array.isArray(v)) v = v[v.length - 1];
    if (typeof v === 'string') return v;
    if (UI.trMissing.indexOf(key) < 0) UI.trMissing.push(key);
    return key;
  }
  UI.tr = function (root, vars) {
    if (!root || !root.querySelectorAll) return;
    vars = vars || {};
    var list = Array.prototype.slice.call(root.querySelectorAll('[data-t]'));
    if (root.hasAttribute && root.hasAttribute('data-t')) list.unshift(root);
    list.forEach(function (el) {
      var key = el.getAttribute('data-t') || el.innerHTML.replace(/\s+/g, ' ').trim();
      var out = pick(key);
      var map = el.getAttribute('data-tv');
      if (map) {
        map.split(',').forEach(function (pair) {
          var p = pair.split(':'), name = p[0].trim(), val = vars[(p[1] || p[0]).trim()];
          if (val != null) out = out.split('{' + name + '}').join(String(val));
        });
      }
      if (out !== el.innerHTML) el.innerHTML = out;
      el.removeAttribute('data-t');
      el.removeAttribute('data-tv');
    });
    var attrs = Array.prototype.slice.call(root.querySelectorAll('[data-ta]'));
    if (root.hasAttribute && root.hasAttribute('data-ta')) attrs.unshift(root);
    attrs.forEach(function (el) {
      el.getAttribute('data-ta').split(',').forEach(function (name) {
        name = name.trim();
        var v = el.getAttribute(name);
        if (v) el.setAttribute(name, pick(v));
      });
      el.removeAttribute('data-ta');
    });
  };

  /* Accessibility glue for things the Python side shows with classes only (WCAG AA):
     - error and note messages (Label roles msg-error / msg-note / msg-ok) are read out by screen readers;
     - toggle buttons in a .seg / .pills / .tabs group say which one is chosen (aria-pressed follows the "on" class);
     - an icon image inside a button with its own text gets alt="";
     - Anvil's own pieces: the "Build web apps with Anvil" banner link and a notification's close button get names. */
  var A11Y = '.anvil-role-msg-error,.anvil-role-msg-note,.anvil-role-msg-ok,.seg button,.pills button,.lp-filter button,button img:not([alt]),#anvil-badge,[data-notify="dismiss"],.anvil-close';
  UI.a11y = function (el) {
    if (!el || el.nodeType !== 1) return;
    var c = el.classList, want = null;
    if (c.contains('anvil-role-msg-error')) want = 'alert';
    else if (c.contains('anvil-role-msg-note') || c.contains('anvil-role-msg-ok')) want = 'status';
    if (want && el.getAttribute('role') !== want) el.setAttribute('role', want);
    if (el.tagName === 'BUTTON' && el.closest('.seg, .pills, .lp-filter')) {
      var on = c.contains('on') ? 'true' : 'false';
      if (el.getAttribute('aria-pressed') !== on) el.setAttribute('aria-pressed', on);
    }
    if (el.tagName === 'IMG' && !el.hasAttribute('alt') && el.closest('button')) el.setAttribute('alt', '');
    if (el.id === 'anvil-badge' && !el.hasAttribute('aria-label')) el.setAttribute('aria-label', 'Built with Anvil (opens anvil.works)');
    if ((el.getAttribute('data-notify') === 'dismiss' || c.contains('anvil-close')) && el.getAttribute('aria-hidden') === 'true') {
      el.removeAttribute('aria-hidden');
      el.setAttribute('aria-label', 'Close');
    }
  };
  function a11yScan(root) {
    if (!root || root.nodeType !== 1) return;
    UI.a11y(root);
    var list = root.querySelectorAll(A11Y);
    for (var i = 0; i < list.length; i++) UI.a11y(list[i]);
  }
  function a11yStart() {
    a11yScan(document.body);
    new MutationObserver(function (records) {
      for (var i = 0; i < records.length; i++) {
        var r = records[i];
        if (r.type === 'attributes') UI.a11y(r.target);
        else for (var j = 0; j < r.addedNodes.length; j++) a11yScan(r.addedNodes[j]);
      }
    }).observe(document.body, { subtree: true, childList: true, attributes: true, attributeFilter: ['class'] });
  }
  if (document.body) a11yStart(); else document.addEventListener('DOMContentLoaded', a11yStart);
})();
