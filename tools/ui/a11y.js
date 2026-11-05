/* Accessibility check (WCAG 2.2 A + AA), run inside the real app by tools/ui_test.py through tools/live/drive.mjs.
   1. axe-core (APP_MAKER/vendor/axe-core, injected by ui_test.py) on every page, signed out and signed in (Addanapp is
      light-only): a "serious" or "critical" WCAG problem fails the run; smaller ones and best-practice hints are notes.
   2. Keyboard and screen-reader checks on the sign-in box: a real heading, autocomplete on the fields, the Google logo
      marked as decoration, errors read out, toggle buttons that say which one is on, and the Privacy & Terms page
      keeping Tab inside. Resolves to {ok, log}. Keep log lines ASCII (the Windows console). */
(async function () {
  /*AXE*/
  const PUBLIC = ['#home', '#work', '#guides', '#privacy'];
  const MEMBER = ['#portal', '#new', '#account'];
  const log = [], bad = [];
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  async function until(fn, what, ms) {
    const end = Date.now() + (ms || 30000);
    while (Date.now() < end) { try { const v = fn(); if (v) return v; } catch (e) {} await sleep(150); }
    throw new Error('timed out waiting for: ' + what);
  }
  const $ = (s) => document.querySelector(s), $$ = (s) => Array.from(document.querySelectorAll(s));
  const vis = (e) => !!e && e.getBoundingClientRect().width > 0;
  const txt = (e) => (e ? e.textContent : '').replace(/\s+/g, ' ').trim();
  const btn = (text, scope) => $$((scope ? scope + ' ' : '') + 'button').find((b) => vis(b) && txt(b).indexOf(text) === 0);
  const ascii = (s) => String(s).normalize('NFD').replace(/[^\x20-\x7e]/g, '');
  const ok = (cond, msg) => { if (cond) log.push('ok   ' + msg); else { bad.push(msg); log.push('FAIL ' + msg); } };
  function type(input, value) {
    input.focus(); input.value = value;
    input.dispatchEvent(new Event('input', { bubbles: true })); input.dispatchEvent(new Event('change', { bubbles: true }));
  }
  async function page(hash, ready) {
    if (location.hash !== hash) window.UI_READY = false;
    location.hash = hash;
    await until(() => window.UI_READY && location.hash === hash && (!ready || ready()), hash, 60000);
    await sleep(900);
  }
  if (!window.axe) { const s = document.createElement('script'); s.textContent = window.__AXE_SRC; document.head.appendChild(s); }

  async function scan(hash, ready) {
    await page(hash, ready);
    document.querySelectorAll('.rv').forEach((e) => e.classList.add('in'));  // scroll-reveal: measure the final colours
    if (window.LegalKit && window.LegalKit.isOpen()) window.LegalKit.close();
    await sleep(1000);
    await axeRun(hash);
  }
  async function axeRun(where) {
    const res = await window.axe.run(document, {
      runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice'] },
    });
    let serious = 0;
    for (const v of res.violations) {
      const wcag = v.tags.some((t) => /^wcag2/.test(t));
      const fail = wcag && (v.impact === 'serious' || v.impact === 'critical');
      const at = v.nodes.slice(0, 2).map((n) => ascii(n.target.join(' ')).slice(0, 70)).join(' | ');
      log.push((fail ? 'FAIL ' : 'note ') + where + ' ' + v.id + ' (' + v.impact + ', ' + v.nodes.length + 'x): ' + at);
      if (fail) {
        serious++; bad.push(where + ' ' + v.id);
        for (const n of v.nodes.slice(0, 4)) log.push('       ' + ascii(n.html).replace(/\s+/g, ' ').slice(0, 150) + ' :: ' + ascii((n.failureSummary || '').split(/\n/).slice(1).join(' ')).slice(0, 150));
      }
    }
    if (!serious) log.push('ok   ' + where + ': no serious WCAG problems (' + res.passes.length + ' rules pass)');
  }

  try {
    // ---------------------------------------------------------------- the sign-in box
    window.UI_READY = false; location.hash = '#login';
    await until(() => vis($('.auth input[type=email]')), 'sign-in box');
    ok(!!$('.auth [role=heading]'), 'sign-in: the title is a heading');
    ok($('.auth input[type=email]').autocomplete === 'email' && $('.auth input[type=password]').autocomplete === 'current-password',
      'sign-in: email and password have autocomplete');
    const g = $('.anvil-role-google img');
    ok(!g || g.getAttribute('alt') === '', 'sign-in: the Google logo is marked as decoration (alt="")');
    btn('Sign in', '.auth').click();  // empty form
    await until(() => vis($('.auth .anvil-role-msg-error')), 'the error');
    ok($('.auth .anvil-role-msg-error').getAttribute('role') === 'alert', 'sign-in: the error is read out (role=alert)');
    await axeRun('#login box');
    // a script's focus() doesn't always count as keyboard focus, so read the CSS: no app.css rule that removes the focus
    // outline may apply to a tick box on this page
    const kills = [], ticks = $$('input[type=checkbox]');
    for (const sh of document.styleSheets) { if (!/app\.css/.test(sh.href || '')) continue; for (const r of sh.cssRules) {
      if (!r.selectorText || !/:focus/.test(r.selectorText) || !/outline:\s*(none|0)/.test(r.cssText)) continue;
      const sel = r.selectorText.replace(/:focus(-visible|-within)?/g, '');
      try { if (ticks.some((t) => t.matches(sel))) kills.push(r.selectorText); } catch (e) {}
    } }
    ok(!kills.length, 'tick boxes keep their focus ring' + (kills.length ? ' (' + ascii(kills.join(', ')).slice(0, 200) + ')' : ''));
    // Privacy & Terms keeps Tab inside
    const lk = $$('.auth [data-lk-open]').find(vis);
    if (lk) {
      lk.click();
      await until(() => window.LegalKit && window.LegalKit.isOpen(), 'the Privacy page');
      const behind = Array.from(document.body.children).filter((e) => e.id !== 'lk-root' && e.tagName !== 'SCRIPT');
      ok(behind.length && behind.every((e) => e.inert), 'privacy page: the app behind it is inert (Tab stays inside)');
      window.LegalKit.close();
    }
    const close = $('.anvil-modal-header .anvil-close, .modal-header .close, [data-dismiss="modal"]');
    if (close) close.click(); else document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
    await sleep(800);

    // ---------------------------------------------------------------- axe on every page
    for (const h of PUBLIC) await scan(h);
    await page('#work', () => $$('.pf-item').length > 40);
    $$('.pf-item summary')[0].click(); await sleep(600);
    await axeRun('#work (row open)');
    ok($$('.lp-filter button').every((b) => b.hasAttribute('aria-pressed')), 'work: filter buttons say which one is on');
    // sign up so the workspace pages can be checked too
    window.UI_READY = false; location.hash = '#signup';
    await until(() => vis($('.auth input[autocomplete=name]')), 'sign-up box');
    type($('.auth input[autocomplete=name]'), 'Access Tester');
    type($('.auth input[type=email]'), 'a11y' + Date.now() + '@example.com');
    type($('.auth input[type=password]'), 'Hb-' + Math.random().toString(36).slice(2) + '-Kq7');
    const box = $('.auth input[type=checkbox]'); if (box && !box.checked) box.click();
    btn('Create workspace', '.auth').click();
    await until(() => location.hash === '#portal' && window.UI_READY, 'signed in', 40000);
    for (const h of MEMBER) await scan(h);
    await page('#new', () => $('.rf'));
    ok($$('.rf .seg button').length >= 10 && $$('.rf .seg button').every((b) => b.hasAttribute('aria-pressed')), 'new request: type and priority say which one is chosen');
    type($('.rf input.anvil-text-box'), 'Accessibility check request');
    type($('.rf textarea'), 'A request for the accessibility check.');
    btn('Submit request').click();
    await until(() => /^#r\//.test(location.hash) && window.UI_READY && $('.rd-h'), 'request page', 30000);
    await sleep(900);
    await axeRun('#r (request)');
    await scan('#portal', () => $$('.rq:not(.head)').length >= 1);
    log.push(bad.length ? 'PROBLEMS: ' + bad.join(' | ') : 'PASSED');
    return { ok: !bad.length, log: log };
  } catch (e) {
    log.push(String(e && e.message || e));
    return { ok: false, log: log };
  }
})();
