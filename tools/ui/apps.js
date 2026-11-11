/* The Apps area (#apps, #app/<key>): a client's app portfolio board. Local App Server only: signs in as the
   ADMIN_EMAILS consultant; if the local database has no portfolio yet, it sends a small one through the PC API
   (/_/api/apps/v1/push with the local test key). Then every view: board, grid (a tick), notifications (dismiss and
   bring back), posts (a Posted tick), biz dev (+ an outreach row), money, YouTube, dossier (flip), and an app page
   (a step, notes, Ask Claude). Resolves to {ok, log}. */
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
    await until(() => window.UI_READY && location.hash === hash && ready(), what || hash, 60000);
    await sleep(300);
  }
  async function signInAdmin() {
    const pw = 'Hb-local-admin-Kq7-2026';
    location.hash = '#login';
    await until(() => vis($('.auth input[type=email]')), 'sign-in box');
    type($('.auth input[type=email]'), 'arkulinskis@gmail.com'); type($('.auth input[type=password]'), pw);
    await click('Sign in', '.auth');
    await until(() => (location.hash === '#admin' && window.UI_READY) || vis($('.auth .anvil-role-msg-error')), 'signed in or error', 30000);
    if (location.hash !== '#admin') {
      await click('Create a workspace', '.auth');
      await until(() => vis($('.auth input[autocomplete=name]')), 'sign-up fields');
      type($('.auth input[autocomplete=name]'), 'Local Consultant');
      type($('.auth input[type=email]'), 'arkulinskis@gmail.com'); type($('.auth input[type=password]'), pw);
      const tick = $('.auth input[type=checkbox]'); if (tick && !tick.checked) tick.click();
      await click('Create workspace', '.auth');
    }
    await until(() => location.hash === '#admin' && window.UI_READY && $('.tabs-line'), 'the console', 40000);
  }
  async function api(action, body) {
    const r = await fetch(location.origin + '/_/api/apps/v1/' + action, {method: 'POST', headers: {Authorization: 'Bearer aal_local_test_key',
      'Content-Type': 'application/json'}, body: JSON.stringify(Object.assign({client: 'arkulinskis+arkvital@gmail.com'}, body || {}))});
    return [r.status, await r.json()];
  }
  function sample() {
    const ph = [{id: 'build', name: 'Build', desc: 'Being built', items: [{id: 'github', label: 'Code on GitHub', auto: 'Found on GitHub'}]},
                {id: 'deploy', name: 'Deploy', desc: 'Not live yet', items: [{id: 'anvil', label: 'Published on Anvil'}, {id: 'domain', label: 'Own domain live (.com)'}]},
                {id: 'test', name: 'Test', desc: 'Make sure it works', items: [{id: 'admin', label: 'Admin panel tested'}, {id: 'usability', label: 'Usability test'}]},
                {id: 'promote', name: 'Promote', desc: 'Tell people', items: [{id: 'linkedin', label: 'LinkedIn post'}, {id: 'youtube', label: 'YouTube video'}]}];
    const app = (key, name, extra) => Object.assign({key, name, card: Object.assign({name, desc: name + ': a sample app for the UI test', url: 'https://' + key + '.example',
      url_kind: 'domain', auto: {github: true, anvil: true}, live: {ok: true, status: 200, checked: new Date().toISOString()},
      seo: {missing: ['robots.txt'], checks: {title: true}}, legal: {ok: true, problems: [], kit_version: '2026-10-31'},
      promo: {linkedin: 2, youtube: 1}, structure: 'forms', commits: [{date: new Date().toISOString(), msg: 'First commit', url: 'https://github.com'}]}, extra || {}),
      promo: {intro: 'Sample posts.', items: [{id: 'li1', kind: 'linkedin', title: 'Launch', text: 'We launched!', note: 'Add a screenshot'},
        {id: 'li2', kind: 'linkedin', title: 'Story', text: 'Here is why.'}, {id: 'yt-sell', kind: 'youtube', title: 'Sell', text: 'Script words here.'}]}});
    return {create: {name: 'Arkvital', company: 'Arkvital'}, meta: {phases: ph, refreshed_at: new Date().toISOString(), errors: [],
      actions: {github: 'GitHub', live: 'Live site + SEO', hero: 'New screenshot'}, all_default: ['github', 'live'],
      money_meta: {roles: {focus: {icon: '🎯', label: 'Focus', meaning: 'the one app'}, traffic: {icon: '📣', label: 'Traffic driver', meaning: 'free, sends people'}}}},
      projects: [app('snack', 'Snack App', {money: {role: 'focus', role_icon: '🎯', role_label: 'Focus', when_label: 'Now', why: 'Best buyer.', free: 'Menu', paywall: 'Orders',
                   strategies: [{name: 'Monthly', price: '$29/mo', how: 'Card'}], feeds: [], fed_by: ['pencil']},
                   bizdev: {key: 'snack', name: 'Snack App', rank: 1, wave: '1', wave_name: 'Wave 1', score: 12, keep: '3 paying cafés', first: 'Email 5 cafés'},
                   branches: [{name: 'forms', ahead: 2, base: 'master', compare_url: 'https://github.com'}]}),
                 app('pencil', 'Pencil Club', {money: {role: 'traffic', role_icon: '📣', role_label: 'Traffic driver', when_label: 'Later', why: 'Free.', free: 'All',
                   paywall: 'Nothing', strategies: [], feeds: ['snack'], fed_by: []}}),
                 app('quiet', 'Quiet Notes', {live: {ok: false, status: 502, checked: new Date().toISOString()}})],
      docs: [{name: 'bizdev/README', text: '# Plans\n\n## Start here\n\n- [Snack App](apps/snack.md) first\n'},
             {name: 'bizdev/PLAYBOOK', text: '# Playbook\n\nTalk to ten people.'},
             {name: 'bizdev/apps/snack', text: '# Snack App\n\n**Who:** cafés.\n\n1. Email five cafés\n2. Visit two'},
             {name: 'bizdev/index', data: {apps: [{key: 'snack', name: 'Snack App', rank: 1, wave: '1', wave_name: 'Wave 1', score: 12, keep: '3 paying cafés'}]}},
             {name: 'youtube', data: {latest: {updated: new Date().toISOString(), channel: {id: 'UC1', title: 'Addanapp', subscribers: 3, views: 120},
               videos: [{id: 'abc', title: 'Snack App in 60 seconds', app: 'snack', kind: 'pitch', published: '2026-11-01', views: 40, likes: 2, comments: 0, privacy: 'public'},
                        {id: 'def', title: 'Snack reel', app: 'snack', kind: 'reel', published: '2026-11-03', views: 12, likes: 1, comments: 0, privacy: 'public'}]},
               history: {'2026-11-09': {views: 100, subscribers: 2}, '2026-11-10': {views: 110, subscribers: 3}, '2026-11-11': {views: 120, subscribers: 3}}}}]};
  }

  try {
    if (location.hash !== '#home') { window.UI_READY = false; location.hash = '#home'; await until(() => window.UI_READY, 'home'); }
    await signInAdmin();
    let [st, hello] = await api('hello', {create: {name: 'Arkvital', company: 'Arkvital'}});
    ok(st === 200, 'PC API: the local test key works');
    if (!hello.apps) {
      [st] = await api('push', sample());
      ok(st === 200, 'PC API: a sample portfolio was sent');
      location.reload();
      await until(() => window.UI_READY, 'reload after the sample', 60000);
    }
    const [s401] = await (async () => { const r = await fetch(location.origin + '/_/api/apps/v1/board'); return [r.status]; })();
    ok(s401 === 401, 'PC API: no key, no entry');

    // board
    await page('#apps/board', () => $$('.ap-card').length >= 2, 'board');
    ok($$('.aa-nav-app a').filter(vis).some((a) => a.getAttribute('href') === '#apps' && txt(a).startsWith('Apps')), 'menu: Apps link for the consultant');
    ok($$('.ap-tabs a').length === 8 && $('.ap-tabs a.on') && txt($('.ap-tabs a.on')).startsWith('Board'), 'board: 8 view tabs, Board lit');
    ok($$('.ap-stat').length >= 6 && $$('.ap-lane').length >= 4, 'board: header numbers and stage lanes');
    const nCards = $$('.ap-card').length;
    const head = $$('.ap-lane-head').find((h) => h.getAttribute('aria-expanded') === 'true' && h.closest('.ap-lane').querySelector('.ap-card'));
    head.click();
    await until(() => $$('.ap-card').length < nCards, 'a lane folds');
    $$('.ap-lane-head').find((h) => h.getAttribute('aria-expanded') === 'false' && txt(h).startsWith(txt(head).split(' ')[0])).click();
    await until(() => $$('.ap-card').length === nCards, 'the lane unfolds');
    ok(true, 'board: a lane folds and unfolds');
    const search = $('.ap-tools input[type=search]');
    type(search, 'zzzz-nothing');
    await until(() => $$('.ap-card').length === 0, 'search hides everything');
    type(search, '');
    await until(() => $$('.ap-card').length === nCards, 'search cleared');
    ok(true, 'board: search filters the cards');

    // grid
    await page('#apps/grid', () => $$('.ap-grid tbody tr').length >= 2, 'grid');
    const cell = $$('.ap-cell').find((c) => !c.classList.contains('done') && !c.classList.contains('na'));
    const key = cell.dataset.key, item = cell.dataset.item;
    const sel = '.ap-cell[data-key="' + key + '"][data-item="' + item + '"]';
    cell.click();
    await until(() => $(sel) && $(sel).classList.contains('done'), 'a square ticks');
    $(sel).click(); await until(() => $(sel).classList.contains('na'), 'not needed');
    $(sel).click(); await until(() => !$(sel).classList.contains('na') && !$(sel).classList.contains('done'), 'back to empty');
    ok(true, 'grid: a square cycles done, not needed, empty');
    $('.ap-grid th[data-sort="name"]').click();
    await until(() => $('.ap-grid th[data-sort="name"] .arrow'), 'sorted by name');
    ok(true, 'grid: sorts by a column');

    // notifications
    await page('#apps/notes', () => $$('.ap-note').length >= 1, 'notes');
    const nNotes = $$('.ap-note').length;
    ok($$('.ap-note .prompt').every((p) => txt(p).length > 5) && btn('Copy for Claude'), 'notes: each has a prompt and Copy for Claude');
    await click('Dismiss', '.ap-note');
    await until(() => $$('.ap-note').length === nNotes - 1, 'dismissed');
    const show = await until(() => $$('.ap-notes input[type=checkbox]').find(vis), 'show dismissed box');
    show.click();
    await click('Bring back', '.ap-note');
    await until(() => !$$('.ap-note.gone').length, 'brought back');
    ok(true, 'notes: dismiss and bring back');

    // posts
    await page('#apps/posts', () => $$('.ap-post').length >= 2, 'posts');
    const box = $$('.ap-post input[type=checkbox]').find((b) => !b.checked);
    box.click();
    await until(() => box.closest('.ap-post') === null || $$('.ap-post.posted').length >= 1, 'posted tick');
    const again = $$('.ap-post.posted input[type=checkbox]')[0]; again.click();
    await sleep(1200);
    ok(true, 'posts: Posted ticks and unticks');

    // biz dev + outreach
    await page('#apps/bizdev/README', () => $('.ap-md h2') || $('.ap-md p'), 'biz dev');
    await page('#apps/bizdev/outreach-log', () => vis($('.ap-log-form')), 'outreach log');
    type($$('.ap-log-form input').find((i) => i.placeholder && i.placeholder.startsWith('Reddit')), 'Email');
    type($$('.ap-log-form input').find((i) => i.placeholder && i.placeholder.startsWith('r/excel')), 'UI test café');
    await click('Add to log');
    await until(() => /UI test café/.test(txt($('.ap-log'))), 'the new row');
    ok(true, 'biz dev: plans and a new outreach row');

    // money, youtube
    await page('#apps/money', () => $$('.ap-m-card').length >= 1, 'money');
    ok(true, 'money: plans by role');
    await page('#apps/youtube', () => $$('.ap-yt-tile').length >= 3, 'youtube');
    await until(() => $('.ap-chart svg'), 'a chart');
    ok($('.ap-yt-table tbody tr'), 'youtube: tiles, a chart and the video table');

    // dossier
    await page('#apps/dossier', () => vis($('.ap-dos-top')), 'dossier');
    const first = txt($('.ap-dossier h2'));
    await click('→', '.ap-dos-nav');
    await until(() => txt($('.ap-dossier h2')) !== first, 'next dossier');
    ok($$('.ap-fact').length >= 10, 'dossier: facts and flipping to the next app');

    // one app
    const k = new URL($('.ap-dossier a.aa-btn[href^="#app/"]').href).hash;
    window.__lastApp = k;
    await page(k, () => $$('.ap-step').length >= 5, 'app page');
    const step = $$('.ap-step').find((b) => !b.classList.contains('done') && !b.classList.contains('na'));
    const sid = step.dataset.step;
    step.click();
    await until(() => $('.ap-step[data-step="' + sid + '"]').classList.contains('done'), 'step done');
    $('.ap-step[data-step="' + sid + '"]').click(); await until(() => $('.ap-step[data-step="' + sid + '"]').classList.contains('na'), 'step n/a');
    $('.ap-step[data-step="' + sid + '"]').click(); await until(() => !$('.ap-step[data-step="' + sid + '"]').classList.contains('na'), 'step empty');
    ok(true, 'app: a step cycles');
    const notes = $$('textarea').find((t) => t.placeholder && t.placeholder.startsWith('e.g. Admin'));
    type(notes, 'UI test note'); notes.blur();
    await until(() => /Notes saved/.test(document.body.textContent), 'notes saved');
    const nChanges = $$('.ap-box.claude .ap-li').length;
    type($$('textarea').find((t) => t.placeholder && t.placeholder.startsWith('e.g. Make')), 'UI test: make the start button bigger on phones.');
    await click('Ask Claude');
    await until(() => $$('.ap-box.claude .ap-li').length === nChanges + 1, 'the change is listed');
    ok(true, 'app: notes save and Ask Claude makes a request');
    say('PASSED');
    return {ok: true, log};
  } catch (e) {
    say(String(e && e.stack || e));
    return {ok: false, log};
  }
})();
