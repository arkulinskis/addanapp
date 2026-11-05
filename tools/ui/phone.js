/* Phone-width check (run at 390 px wide by tools/ui_test.py): every page loads without errors and without sideways
   scrolling, signed out and signed in; the burger menu opens and closes. Resolves to {ok, log}. */
(async function () {
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
  function type(input, value) {
    input.focus(); input.value = value;
    input.dispatchEvent(new Event('input', { bubbles: true })); input.dispatchEvent(new Event('change', { bubbles: true }));
  }
  async function check(hash, ready) {
    if (location.hash !== hash) window.UI_READY = false;
    location.hash = hash;
    await until(() => window.UI_READY && location.hash === hash && (!ready || ready()), hash, 40000);
    await sleep(600);
    if (window.LegalKit && window.LegalKit.isOpen()) { window.LegalKit.close(); await sleep(300); }
    const vw = Math.min(window.innerWidth, screen.width), w = document.documentElement.scrollWidth;
    const wide = $$('body *').filter((e) => { const r = e.getBoundingClientRect(); return r.width && r.right > vw + 1 && !e.closest('.marquee, .board, .lp-filter, .tabs-line, .aa-nav, #lk-root'); })
      .slice(0, 3).map((e) => e.tagName.toLowerCase() + '.' + String(e.className).split(' ').slice(0, 2).join('.'));
    const sideways = w > vw + 1 || wide.length;
    if (sideways) bad.push(hash + ' scrolls sideways (' + w + ' > ' + vw + ') ' + wide.join(' '));
    log.push((sideways ? 'WIDE ' : 'ok   ') + hash + ' (' + w + ')');
  }
  try {
    for (const h of ['#home', '#work', '#guides', '#privacy']) await check(h);
    // the burger menu
    $('.aa-burger').click();
    await until(() => vis($('.aa-nav-public a[data-nav="faq"]')), 'phone menu');
    $('.aa-nav-public a[data-nav="faq"]').click();
    await until(() => location.hash === '#home/faq' && !$('.aa-shell').classList.contains('nav-open'), 'menu closes on a link');
    log.push('ok   burger menu opens, a link closes it');
    // sign up so the workspace pages can be checked too
    window.UI_READY = false; location.hash = '#signup';
    await until(() => vis($('.auth input[autocomplete=name]')), 'sign-up box');
    type($('.auth input[autocomplete=name]'), 'Phone Tester');
    type($('.auth input[type=email]'), 'phone' + Date.now() + '@example.com');
    type($('.auth input[type=password]'), 'Hb-' + Math.random().toString(36).slice(2) + '-Kq7');
    const tick = $('.auth input[type=checkbox]'); if (tick && !tick.checked) tick.click();
    btn('Create workspace', '.auth').click();
    await until(() => location.hash === '#portal' && window.UI_READY, 'signed in', 40000);
    await check('#portal');
    await check('#new', () => $('.rf'));
    type($('.rf input.anvil-text-box'), 'Phone-sized request');
    type($('.rf textarea'), 'Checking the request page on a phone.');
    btn('Submit request').click();
    await until(() => /^#r\//.test(location.hash) && window.UI_READY && $('.rd-h'), 'request page', 30000);
    await check(location.hash, () => $('.rd-h'));
    await check('#portal', () => $$('.rq:not(.head)').length >= 1);
    await check('#account');
    log.push(bad.length ? 'PROBLEMS: ' + bad.join(' | ') : 'PASSED');
    return { ok: !bad.length, log: log };
  } catch (e) {
    log.push(String(e && e.message || e));
    return { ok: false, log: log };
  }
})();
