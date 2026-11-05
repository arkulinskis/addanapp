/* The main journeys, run inside the real app (Anvil App Server) by tools/ui_test.py through tools/live/drive.mjs:
   the landing page (case studies + Shuffle, film, workspace tabs, deck, section links, project brief), the Work index
   (filter, a row opening), the free guides, Privacy, then a client's whole loop: sign up from a private page, new
   request, comment, dashboard, account, sign out. Resolves to {ok, log}. Keep log lines ASCII (the Windows console). */
(async function () {
  const log = [], t0 = Date.now();
  const say = (m) => log.push(((Date.now() - t0) / 1000).toFixed(1) + 's ' + m);
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  async function until(fn, what, ms) {
    const end = Date.now() + (ms || 20000);
    while (Date.now() < end) { try { const v = fn(); if (v) return v; } catch (e) {} await sleep(150); }
    throw new Error('timed out waiting for: ' + what);
  }
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => Array.from(document.querySelectorAll(s));
  const vis = (e) => !!e && e.getBoundingClientRect().width > 0;
  const txt = (e) => (e ? e.textContent : '').replace(/\s+/g, ' ').trim();
  const btn = (text, scope) => $$((scope ? scope + ' ' : '') + 'button').find((b) => vis(b) && txt(b).indexOf(text) === 0);
  async function click(text, scope) { const b = await until(() => btn(text, scope), 'button "' + text + '"'); b.scrollIntoView({ block: 'center' }); b.click(); return b; }
  function type(input, value) {
    input.focus(); input.value = value;
    input.dispatchEvent(new Event('input', { bubbles: true })); input.dispatchEvent(new Event('change', { bubbles: true }));
  }
  async function page(hash, ready, what) {
    if (location.hash !== hash) window.UI_READY = false;  // the old page stays until the router runs
    location.hash = hash;
    await until(() => window.UI_READY && location.hash === hash && ready(), what || hash, 40000);
    await sleep(300);
  }
  const ok = (cond, msg) => { if (!cond) throw new Error('FAILED: ' + msg); say('ok   ' + msg); };
  const keys = () => $$('.pf-spot').map((e) => e.getAttribute('data-pf')).join(',');

  try {
    // ---------------------------------------------------------------- landing
    await page('#home', () => $$('.pf-spot').length === 3, 'landing');
    ok(/Apps built at AI speed/.test(txt($('.lp-hero h1'))), 'landing: hero headline');
    ok(!$('[data-t]') && !$('[data-tv]'), 'landing: every template text went through the translator');
    ok(/Three of our \d+ products/.test(txt($('#work .lead'))), 'landing: the product count is filled in');
    const n = $$('.lp-proof .track a').length;
    ok(n >= 100 && n % 2 === 0 && $$('.lp-proof .track a[aria-hidden="true"]').length === n / 2, 'landing: marquee = every product twice (copy hidden)');
    ok($$('.pf-spot.flip').length === 1 && $$('.pf-spot .shot svg, .pf-spot .shot img').length >= 3, 'landing: 3 case studies with previews, middle one flipped');
    const before = keys();
    await click('Shuffle');
    await until(() => $$('.pf-spot').length === 3 && keys() !== before, 'Shuffle');
    ok(before.split(',').every((k) => keys().split(',').indexOf(k) < 0), 'landing: Shuffle shows three other products');
    $('.yt-cover').click();
    await until(() => $('.yt-frame iframe[src*="youtube-nocookie.com/embed/wzCMxAdyrHo"]'), 'film player');
    ok(true, 'landing: the film loads only after Play (youtube-nocookie)');
    await click('Consultant view');
    ok(vis($('.lp-ws .panel.on .colk')) && btn('Consultant view').getAttribute('aria-pressed') === 'true', 'landing: workspace preview tabs');
    const deck = $('#partners a.aa-btn[download]');
    ok(deck && /addanapp-partner-deck\.pdf$/.test(deck.getAttribute('href')) && $$('#partners .aa-langs a').length === 3, 'landing: deck download + 3 other languages');
    ok($$('#youtube .aa-langs a').length === 3 && $$('#youtube .aa-langs .sep').filter(vis).length === 2, 'landing: film in 3 other languages, 2 separators');
    location.hash = '#home/faq';
    await until(() => Math.abs($('#faq').getBoundingClientRect().top - $('.aa-header').offsetHeight) < 30, 'scrolled to the FAQ', 8000);
    ok(true, 'landing: #home/faq scrolls to the FAQ');
    ok($$('.aa-nav-public a.active').map(txt).join() === 'FAQ', 'header: the FAQ chapter lights up');
    ok($('#faq a[href*="FW-j_xL_DWo"]'), 'FAQ: the rebuild film link is filled in');
    // project brief
    const form = $('#lead-form');
    await click('Send brief', '#lead-form');
    await until(() => vis(form.querySelector('.anvil-role-msg-error')), 'brief error');
    ok(/name/i.test(txt(form.querySelector('.anvil-role-msg-error'))), 'brief: asks for a name first');
    const boxes = $$('#lead-form input.anvil-text-box');
    type(boxes[0], 'Flow Tester'); type(boxes[1], 'flow' + Date.now() + '@example.com'); type(boxes[2], 'Flow Inc');
    type($('#lead-form textarea'), 'We need a dashboard with roles, approvals and a weekly PDF.');
    await click('Send brief', '#lead-form');
    await until(() => /confirm/i.test(txt(form.querySelector('.anvil-role-msg-error'))), 'consent error');
    ok(true, 'brief: the consent tick is required');
    $('#lead-form input[type=checkbox]:not(.hp)').click();
    await click('Send brief', '#lead-form');
    await until(() => vis($('#lead-form .ok')), 'brief received', 30000);
    ok(true, 'brief: sent, thank-you shown');

    // ---------------------------------------------------------------- work
    await page('#work', () => $$('.pf-item').length >= 50 && $$('.lp-filter button').length >= 7, 'work');
    const all = +txt($('.lp-filter button .n'));
    ok($$('.pf-item').length === all && $$('.pf-group').length >= 6, 'work: every product (' + all + ') in category groups');
    ok(/\d+ products/.test(txt($('.pf-count'))), 'work: the count line');
    await click('Engaging games', '.lp-filter');
    const shown = $$('.pf-item').filter(vis);
    ok(shown.length > 0 && shown.length < all && shown.every((e) => e.getAttribute('data-cat') === 'games'), 'work: the games filter');
    ok(btn('Engaging games', '.lp-filter').classList.contains('on'), 'work: the chosen filter is lit');
    await click('All work', '.lp-filter');
    ok($$('.pf-item').filter(vis).length === all, 'work: All work shows everything again');
    const row = $$('.pf-item')[0];
    row.querySelector('summary').click();
    await until(() => row.open && row.querySelector('.pf-body .shot svg, .pf-body .shot img') && row.querySelectorAll('.pf-built .tk').length >= 2, 'row details');
    ok(true, 'work: a row opens to show the preview and what we built');

    // ---------------------------------------------------------------- guides
    try { localStorage.removeItem('aa.guides'); } catch (e) {}
    await page('#guides', () => $$('.gd-card').length === 5, 'guides');
    ok($$('.gd-card .anvil-role-aa-btn button').filter(vis).length === 5, 'guides: five "Get it free" buttons');
    $$('.gd-card .anvil-role-aa-btn button')[2].click();
    await until(() => document.activeElement === $('#guide-form input[type=email]'), 'email box focused');
    ok(true, 'guides: "Get it free" takes you to the email box');
    type($('#guide-form input[type=email]'), 'reader' + Date.now() + '@example.com');
    await click('Get the guides', '#guide-form');
    await until(() => $$('.gd-list .row').length === 5, 'download links', 30000);
    ok($$('.gd-card a[download]').filter(vis).length === 5, 'guides: the email unlocks all five downloads');

    // ---------------------------------------------------------------- privacy
    await page('#privacy', () => $('.legal'), 'privacy');
    await until(() => window.LegalKit && window.LegalKit.isOpen(), 'the Privacy Policy');
    window.LegalKit.close();
    ok(true, 'privacy: opens the Privacy Policy');

    // ---------------------------------------------------------------- a client's loop
    if (location.hash !== '#portal') window.UI_READY = false;
    location.hash = '#portal';
    await until(() => vis($('.auth')) && /Welcome back/.test(txt($('.auth h2'))), 'sign-in box over the landing page');
    ok(true, 'workspace: a private page asks visitors to sign in');
    await click('Create a workspace', '.auth');
    await until(() => vis($('.auth input[autocomplete=name]')), 'sign-up fields');
    const email = 'client' + Date.now() + '@example.com';
    type($('.auth input[autocomplete=name]'), 'Flow Client');
    type($('.auth input[autocomplete=organization]'), 'Flow Bistro');
    type($('.auth input[type=email]'), email);
    type($('.auth input[type=password]'), 'Hb-' + Math.random().toString(36).slice(2) + '-Kq7');
    const tick = $('.auth input[type=checkbox]'); if (tick && !tick.checked) tick.click();
    await click('Create workspace', '.auth');
    await until(() => location.hash === '#portal' && window.UI_READY && vis($('.empty')), 'the new workspace', 40000);
    ok(/Flow Bistro workspace/i.test(txt($('.page-head .eyebrow'))) && /Flow\./.test(txt($('.page-head h1'))), 'portal: greeting with the company');
    ok($('.aa-shell').classList.contains('signed-in') && $('.aa-shell').classList.contains('mode-app'), 'header: workspace mode, signed in');
    ok($$('.aa-nav-app a').filter(vis).length >= 3, 'header: workspace menu');
    // new request
    await page('#new', () => $('.rf input'), 'new request');
    await click('Submit request');
    await until(() => vis($('.rf .anvil-role-msg-error')), 'validation');
    ok(/title/i.test(txt($('.rf .anvil-role-msg-error'))), 'new request: a title is required');
    type($$('.rf input.anvil-text-box')[0], 'Gift card balance page');
    type($$('.rf textarea')[0], 'Guests should be able to check their gift card balance online.');
    await click('Bug fix', '.rf .seg');
    ok(btn('Bug fix', '.rf .seg').classList.contains('on') && btn('Bug fix', '.rf .seg').getAttribute('aria-pressed') === 'true', 'new request: the type is chosen (aria-pressed)');
    await click('High', '.rf .seg');
    await click('Submit request');
    await until(() => /^#r\//.test(location.hash) && window.UI_READY && $('.rd-h'), 'the request page', 30000);
    ok(/Gift card balance page/.test(txt($('.rd-h'))) && /Bug fix/.test(txt($('.rd-title'))) && /High priority/.test(txt($('.rd-title'))), 'request: title, type and priority');
    ok(/We've got it/.test(txt($('.banner'))) && btn('Withdraw', '.banner'), 'request: the next step (Withdraw)');
    ok($$('.stepper .s').length === 6 && $$('.stepper .s.cur').length === 1, 'request: the stepper');
    const rid = location.hash;
    type($('.composer textarea'), 'A detail from the flow test');
    await click('Send', '.composer');
    await until(() => /A detail from the flow test/.test(txt($('.tl'))), 'the comment');
    ok($$('.tl .n.mine').length === 1, 'request: the comment is in the activity');
    // dashboard
    await page('#portal', () => $$('.rq:not(.head)').length === 1, 'dashboard');
    ok(/Gift card balance page/.test(txt($('.rq:not(.head)'))) && $$('.tiles .tile').filter(vis).length === 4, 'dashboard: the request + tiles');
    type($('.toolbar input'), 'nothing-matches');
    await until(() => $$('.empty').some(vis) && !vis($('.rq-list')), 'search narrows');
    ok(true, 'dashboard: search');
    type($('.toolbar input'), '');
    await click('Closed', '.pills');
    await until(() => $$('.empty').some(vis), 'closed filter');
    ok(btn('Closed', '.pills').classList.contains('on'), 'dashboard: filter pills');
    // account
    await page('#account', () => $('.ac-two input'), 'account');
    ok($$('.ac-two input')[2].disabled && $$('.ac-two input')[2].value === email, 'account: the email (read-only)');
    type($$('.ac-two input')[3], '514 555 0100');
    await click('Save changes');
    await until(() => /Saved/.test(document.body.textContent), 'saved');
    ok(true, 'account: saved');
    // sign out
    $('.aa-me-btn').click();
    await until(() => vis($('.aa-me .aa-menu')), 'account menu');
    await click('Sign out', '.aa-me');
    await until(() => location.hash === '#home' && window.UI_READY && $('.aa-shell').classList.contains('signed-out'), 'signed out');
    ok($('.aa-shell').classList.contains('mode-public'), 'sign out: back on the public site');
    window.FLOW_REQUEST = rid;

    say('PASSED');
    return { ok: true, log: log };
  } catch (e) {
    say(String(e && e.message || e));
    return { ok: false, log: log };
  }
})();
