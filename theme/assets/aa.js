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

  /* Header "chapters": every home-page section carries data-ch (the header link it belongs to, or "" for none).
     While the visitor scrolls the home page, the link of the section under the header lights up. */
  var spyOn = false, spyBusy = false;
  function spyRun() {
    spyBusy = false;
    var secs = document.querySelectorAll('.lp [data-ch]');
    if (!secs.length) return;  // not on the home page: the router marks the header itself
    var line = (document.querySelector('.aa-header') || { offsetHeight: 0 }).offsetHeight + window.innerHeight * 0.3;
    var cur = '';
    secs.forEach(function (s) { if (s.getBoundingClientRect().top <= line) cur = s.getAttribute('data-ch'); });
    document.querySelectorAll('.aa-nav-public a[data-nav]').forEach(function (a) {
      a.classList.toggle('active', !!cur && a.getAttribute('data-nav') === cur);
    });
  }
  function spy() {
    if (!spyOn) {
      spyOn = true;
      window.addEventListener('scroll', function () {
        if (!spyBusy) { spyBusy = true; window.requestAnimationFrame(spyRun); }
      }, { passive: true });
    }
    setTimeout(spyRun, 60);
  }

  /* The router lights up the header link of the page (or home-page section) that is open. */
  function markNav(key) {
    document.querySelectorAll('.aa-nav-public a[data-nav]').forEach(function (a) {
      a.classList.toggle('active', !!key && a.getAttribute('data-nav') === key);
    });
  }

  /* Swap a film cover for the YouTube player (privacy-enhanced; nothing loads from YouTube before this click). */
  function playFilm(frame, vid, title) {
    if (!frame) return;
    var f = document.createElement('iframe');
    f.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(vid) + '?autoplay=1&rel=0&playsinline=1';
    f.title = title || '';
    f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
    f.allowFullscreen = true;
    f.referrerPolicy = 'strict-origin-when-cross-origin';
    frame.innerHTML = '';
    frame.appendChild(f);
  }

  /* Work page filter: show one category of the index (rows and group headings carry data-cat). */
  function filterWork(root, key) {
    if (!root) return;
    root.querySelectorAll('[data-cat]').forEach(function (el) {
      el.classList.toggle('gone', key !== 'all' && el.getAttribute('data-cat') !== key);
    });
  }

  return { reveal: reveal, scrollTo: scrollTo, setMeta: setMeta, copy: copy, spy: spy, markNav: markNav,
           playFilm: playFilm, filterWork: filterWork };
})();
