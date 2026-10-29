/* Addanapp browser helpers: scroll reveal, smooth scroll, page meta, header state. */
window.aa = (function () {
  var observer = null;

  function reveal(root) {
    root = root || document;
    var els = root.querySelectorAll('.rv:not(.in)');
    if (!('IntersectionObserver' in window)) {
      els.forEach(function (el) { el.classList.add('in'); });
      return;
    }
    if (!observer) {
      observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            e.target.classList.add('in');
            observer.unobserve(e.target);
          }
        });
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    }
    els.forEach(function (el) { observer.observe(el); });
  }

  function scrollTo(id) {
    var el = document.getElementById(id);
    if (!el) return false;
    var top = el.getBoundingClientRect().top + window.pageYOffset - (document.querySelector('.aa-header') || { offsetHeight: 0 }).offsetHeight + 1;
    window.scrollTo({ top: Math.max(0, top), behavior: 'smooth' });
    return true;
  }

  function setMeta(title, description, path) {
    if (title) document.title = title;
    if (description) {
      var m = document.querySelector('meta[name="description"]');
      if (!m) {
        m = document.createElement('meta');
        m.setAttribute('name', 'description');
        document.head.appendChild(m);
      }
      m.setAttribute('content', description);
    }
    var robots = document.querySelector('meta[name="robots"]');
    if (robots) robots.setAttribute('content', path === 'private' ? 'noindex, nofollow' : 'index, follow, max-image-preview:large');
  }

  function copy(text) {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text);
        return true;
      }
    } catch (e) {}
    var t = document.createElement('textarea');
    t.value = text; t.style.position = 'fixed'; t.style.opacity = '0';
    document.body.appendChild(t); t.select();
    var ok = false;
    try { ok = document.execCommand('copy'); } catch (e) {}
    document.body.removeChild(t);
    return ok;
  }

  // Portfolio index (home page): hovering or focusing a project row shows its preview in the sticky panel.
  function pfShow(index, key) {
    if (!index || !key) return;
    index.querySelectorAll('.pf-pv').forEach(function (el) { el.classList.toggle('on', el.getAttribute('data-pv') === key); });
    index.querySelectorAll('.pf-row[data-pf]').forEach(function (el) { el.classList.toggle('hot', el.getAttribute('data-pf') === key); });
  }

  function pfHover(e) {
    var row = e.target && e.target.closest ? e.target.closest('.pf-row[data-pf]') : null;
    if (!row || row.classList.contains('hot')) return;
    var index = row.closest('.pf-index');
    if (index && index.querySelector('.pf-pv')) pfShow(index, row.getAttribute('data-pf'));
  }

  document.addEventListener('mouseover', pfHover);
  document.addEventListener('focusin', pfHover);

  return { reveal: reveal, scrollTo: scrollTo, setMeta: setMeta, copy: copy, pfShow: pfShow };
})();
