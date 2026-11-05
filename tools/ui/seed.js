/* For screenshots of workspace pages: sign up a fresh client and submit one request. Resolves to window.SEED
   ({request: '#r/<id>'}). */
(async function () {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  async function until(fn, what, ms) {
    const end = Date.now() + (ms || 30000);
    while (Date.now() < end) { try { const v = fn(); if (v) return v; } catch (e) {} await sleep(150); }
    throw new Error('timed out waiting for: ' + what);
  }
  const $ = (s) => document.querySelector(s), $$ = (s) => Array.from(document.querySelectorAll(s));
  const vis = (e) => !!e && e.getBoundingClientRect().width > 0;
  const btn = (text, scope) => $$((scope ? scope + ' ' : '') + 'button').find((b) => vis(b) && b.textContent.trim().indexOf(text) === 0);
  function type(input, value) {
    input.focus(); input.value = value;
    input.dispatchEvent(new Event('input', { bubbles: true })); input.dispatchEvent(new Event('change', { bubbles: true }));
  }
  try {
    window.UI_READY = false; location.hash = '#signup';
    await until(() => vis($('.auth input[autocomplete=name]')), 'sign-up');
    type($('.auth input[autocomplete=name]'), 'Marie Tremblay');
    type($('.auth input[autocomplete=organization]'), 'Bistro Laurier');
    type($('.auth input[type=email]'), 'shots' + Date.now() + '@example.com');
    type($('.auth input[type=password]'), 'Hb-' + Math.random().toString(36).slice(2) + '-Kq7');
    const tick = $('.auth input[type=checkbox]'); if (tick && !tick.checked) tick.click();
    btn('Create workspace', '.auth').click();
    await until(() => location.hash === '#portal' && window.UI_READY, 'portal', 60000);
    window.UI_READY = false; location.hash = '#new';
    await until(() => window.UI_READY && $('.rf'), 'new request');
    type($('.rf input.anvil-text-box'), 'Deposits for large-party reservations');
    type($('.rf textarea'), 'Parties of 8+ should pay a 20% deposit when booking online, refundable up to 48h before.');
    btn('Submit request').click();
    await until(() => /^#r\//.test(location.hash) && window.UI_READY, 'request', 30000);
    window.SEED = { request: location.hash };
    return window.SEED;
  } catch (e) {
    return { error: String(e && e.message || e) };
  }
})();
