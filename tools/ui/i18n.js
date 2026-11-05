/* Translations (run by tools/ui_test.py once per language after it switched the page to fr, ru and lv): every
   template text found its translation (app-kit.js UI.trMissing stays empty, apart from tech words that were never
   translated), the headings are not English, and the sign-up box is translated too. Resolves to {ok, log}. */
(async function () {
  const ALLOWED = ['CMS', 'CSV / PDF', 'Canvas', 'ETL', 'LLMs', 'PWA', 'RAG', 'RBAC', 'REST', 'SEO', 'Stripe', 'Send brief →'];
  const log = [], bad = [];
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  async function until(fn, what, ms) {
    const end = Date.now() + (ms || 30000);
    while (Date.now() < end) { try { const v = fn(); if (v) return v; } catch (e) {} await sleep(150); }
    throw new Error('timed out waiting for: ' + what);
  }
  const $ = (s) => document.querySelector(s), $$ = (s) => Array.from(document.querySelectorAll(s));
  const vis = (e) => !!e && e.getBoundingClientRect().width > 0;
  const ascii = (s) => String(s).normalize('NFD').replace(/[^\x20-\x7e]/g, '');
  const lang = document.documentElement.lang;
  async function page(hash, ready) {
    if (location.hash !== hash) window.UI_READY = false;
    location.hash = hash;
    await until(() => window.UI_READY && location.hash === hash && (!ready || ready()), hash, 40000);
    await sleep(400);
  }
  function missing(where) {
    const m = (window.UI.trMissing || []).filter((k) => ALLOWED.indexOf(k) < 0);
    if (m.length) { bad.push(where + ': ' + m.length + ' untranslated'); m.slice(0, 8).forEach((k) => log.push('       missing: ' + ascii(k).slice(0, 100))); }
    log.push((m.length ? 'FAIL ' : 'ok   ') + where + ' (' + lang + '): ' + (m.length ? m.length + ' texts in English' : 'every text translated'));
  }
  try {
    if (!window.AA_PACK || lang === 'en') throw new Error('the page is not in another language (lang=' + lang + ')');
    await page('#home', () => $$('.pf-spot').length === 3);
    const h1 = $('.lp-hero h1').textContent;
    if (/Apps built at AI speed/.test(h1)) bad.push('the landing headline is in English');
    log.push('ok   headline: ' + ascii(h1).slice(0, 60));
    const shuffle = $('.pf-more .anvil-role-aa-btn button'), send = $('#lead-form .anvil-role-aa-btn button');
    if (!shuffle || /^Shuffle/.test(shuffle.textContent.trim()) || /^Send brief/.test(send.textContent.trim())) bad.push('buttons are in English');
    else log.push('ok   buttons translated: ' + ascii(shuffle.textContent.trim()) + ' / ' + ascii(send.textContent.trim()));
    missing('#home');
    await page('#work', () => $$('.pf-item').length > 40);
    $$('.pf-item summary')[0].click(); await sleep(800);
    missing('#work');
    await page('#guides', () => $$('.gd-card').length === 5);
    missing('#guides');
    await page('#privacy');
    if (window.LegalKit && window.LegalKit.isOpen()) window.LegalKit.close();
    missing('#privacy');
    window.UI_READY = false; location.hash = '#signup';
    await until(() => vis($('.auth input[autocomplete=name]')), 'sign-up box');
    if (/Create your workspace/.test($('.auth h2').textContent)) bad.push('the sign-up box is in English');
    missing('#signup box');
    log.push(bad.length ? 'PROBLEMS: ' + bad.join(' | ') : 'PASSED');
    return { ok: !bad.length, log: log };
  } catch (e) {
    log.push(String(e && e.message || e));
    return { ok: false, log: log };
  }
})();
