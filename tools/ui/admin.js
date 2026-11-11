/* The consultant console (local App Server only: signs in as the ADMIN_EMAILS address, which becomes a consultant
   there). Loads demo data, list + board views, filters, a request's Manage panel and notes, clients, leads, a request
   made for a client, and the tools. Resolves to {ok, log}. */
(async function () {
  const log = [], t0 = Date.now();
  const say = (m) => log.push(((Date.now() - t0) / 1000).toFixed(1) + 's ' + m);
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
  async function click(text, scope) { const b = await until(() => btn(text, scope), 'button "' + text + '"'); b.scrollIntoView({ block: 'center' }); b.click(); return b; }
  const ok = (c, m) => { if (!c) throw new Error('FAILED: ' + m); say('ok   ' + m); };
  function type(input, value) {
    input.focus(); input.value = value;
    input.dispatchEvent(new Event('input', { bubbles: true })); input.dispatchEvent(new Event('change', { bubbles: true }));
  }
  async function page(hash, ready, what) {
    if (location.hash !== hash) window.UI_READY = false;
    location.hash = hash;
    await until(() => window.UI_READY && location.hash === hash && ready(), what || hash, 40000);
    await sleep(300);
  }
  async function signInAdmin() {
    const pw = 'Hb-local-admin-Kq7-2026';
    location.hash = '#login';
    await until(() => vis($('.auth input[type=email]')), 'sign-in box');
    type($('.auth input[type=email]'), 'arkulinskis@gmail.com'); type($('.auth input[type=password]'), pw);
    await click('Sign in', '.auth');
    await until(() => (location.hash === '#admin' && window.UI_READY) || vis($('.auth .anvil-role-msg-error')), 'signed in or error', 30000);
    if (location.hash !== '#admin') {  // no consultant account in this local database yet: create it
      await click('Create a workspace', '.auth');
      await until(() => vis($('.auth input[autocomplete=name]')), 'sign-up fields');
      type($('.auth input[autocomplete=name]'), 'Local Consultant');
      type($('.auth input[type=email]'), 'arkulinskis@gmail.com'); type($('.auth input[type=password]'), pw);
      const tick = $('.auth input[type=checkbox]'); if (tick && !tick.checked) tick.click();
      await click('Create workspace', '.auth');
    }
    await until(() => location.hash === '#admin' && window.UI_READY && $('.tabs-line'), 'the console', 40000);
  }

  try {
    if (location.hash !== '#home') { window.UI_READY = false; location.hash = '#home'; await until(() => window.UI_READY, 'home'); }
    await signInAdmin();
    ok($('.aa-shell').classList.contains('mode-app') && [4, 5].includes($$('.aa-nav-app a').filter(vis).length), 'console: signed in, consultant menu (5 with Apps)');
    // tools: demo data
    await page('#admin/tools', () => btn('Load demo data'), 'tools');
    await click('Load demo data');
    await until(() => /Demo data (loaded|is already)/.test(document.body.textContent), 'demo data');
    ok(true, 'tools: demo data loaded');
    // requests
    await page('#admin', () => $$('.rq.admin:not(.head)').length >= 5, 'requests');
    ok($$('.tiles.six .tile').length === 6 && /open request/.test(txt($('.page-head .ph-sub'))), 'requests: six tiles and the summary line');
    ok($$('.rq.admin:not(.head) .cl').filter(vis).length >= 5, 'requests: the client column');
    await click('Board', '.pills');
    await until(() => $$('.board .col').filter(vis).length === 6, 'board');
    ok($$('.board .kc').length >= 5, 'requests: the board view');
    await click('List', '.pills');
    await until(() => vis($('.rq-list')), 'list');
    await click('All', '.pills');
    const nAll = $$('.rq.admin:not(.head)').length;
    const dd = $('.toolbar select');
    dd.selectedIndex = 1; dd.dispatchEvent(new Event('change', { bubbles: true }));
    await until(() => $$('.rq.admin:not(.head)').length < nAll, 'client filter');
    ok(true, 'requests: the client filter narrows the list');
    dd.selectedIndex = 0; dd.dispatchEvent(new Event('change', { bubbles: true }));
    // a demo request: manage + notes
    const target = $$('.rq.admin:not(.head)').find((r) => /Gift card balance page/.test(r.textContent)) || $$('.rq.admin:not(.head)')[0];
    const href = target.getAttribute('href');
    await page(href, () => $('.manage'), 'a request');
    ok(vis($('.manage')) && vis($$('.side .sec-card')[1]) && $$('.kv .kv-row').length === 7, 'request: Manage panel, client card, 7 details');
    type($('.composer textarea'), 'Internal from the console test');
    const kind = $('.composer select'); kind.selectedIndex = 4; kind.dispatchEvent(new Event('change', { bubbles: true }));
    await click('Post note', '.composer');
    await until(() => $$('.tl .n.internal').some((n) => /Internal from the console test/.test(n.textContent)), 'internal note');
    ok(true, 'request: an internal note');
    const prio = $$('.manage select')[1]; prio.selectedIndex = 3; prio.dispatchEvent(new Event('change', { bubbles: true }));
    await click('Save & notify client', '.manage');
    await until(() => /Urgent priority/.test(txt($('.rd-title'))), 'saved priority');
    ok(true, 'request: Manage saves (priority now urgent)');
    // clients
    await page('#admin/clients', () => $$('.person').length >= 4, 'clients');
    ok($$('.person .anvil-role-chip-ink').some(vis) && /client/.test(txt($('.page-head .ph-sub'))), 'clients: people with roles and the summary');
    const marie = $$('.person').find((p) => /Bistro Laurier/.test(p.textContent));
    btn('View requests', '.people') && $$('.person').indexOf(marie) >= 0 && marie.querySelectorAll('button')[1].click();
    await until(() => location.hash === '#admin' && window.UI_READY && $$('.rq.admin:not(.head)').length >= 1 &&
      $$('.rq.admin:not(.head)').every((r) => /Marie|Bistro/.test(r.textContent)), 'that client\'s requests');
    ok(true, 'clients: "View requests" shows that client\'s requests');
    // new request for a client
    await click('New request for a client');
    await until(() => vis($('.dlg .rf')), 'the dialog');
    type($('.dlg .rf input.anvil-text-box'), 'Console-made request');
    type($('.dlg .rf textarea'), 'Made from the console for the client.');
    await click('Create request', '.dlg');
    await until(() => /^#r\//.test(location.hash) && window.UI_READY && /Console-made request/.test(txt($('.rd-h'))), 'the new request');
    ok(true, 'console: a request made for a client');
    await click('Delete request', '.manage');
    await until(() => vis($('.anvil-modal-content')) && btn('Delete', '.anvil-modal-content'), 'confirm');
    await click('Delete', '.anvil-modal-content');
    await until(() => location.hash === '#admin' && window.UI_READY, 'back to the console');
    ok(true, 'console: delete asks first, then goes back to the list');
    // leads
    await page('#admin/leads', () => $$('.lead-card').length >= 1 || $$('.empty').some(vis), 'leads');
    ok($$('.lead-card').length >= 1 && vis(btn('Project briefs')), 'leads: cards and the brief / guide filter');
    await click('Guide readers');
    await until(() => $$('.lead-card').every((c) => /Free guides/.test(c.textContent)), 'guide readers');
    ok(true, 'leads: guide readers filter');
    say('PASSED');
    return { ok: true, log };
  } catch (e) {
    say(String(e && e.message || e));
    return { ok: false, log };
  }
})();
