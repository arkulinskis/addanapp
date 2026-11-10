"""Service, pricing and French pages as plain HTML at real addresses (/client-portal-development, /fr/tarifs, ...).

Why: the app itself is one address (/) drawn by JavaScript, so Google can rank it for one thing at most and AI
assistants that don't run JavaScript see an empty page. These pages give every service its own address, title,
text and structured data in English and French, each linked to its twin with hreflang. Buttons lead into the app.

Text lives in seo_pages_text.py (PAGES, built from one JSON file per page). This file only draws it.
Add a page: add it to PAGES and to the sitemap list in APP_MAKER/seo/apps/addanapp.json ("sitemap_extra").
"""
import html
import json
import re

import anvil
import anvil.server  # outside Anvil (tools/seo_pages.py previews) a stand-in module with route = None

from .seo_pages_text import PAGES

SITE = "https://addanapp.com"
ORG = SITE + "/#org"
PREPSTO = "https://prepsto.com/#f/e4xsnwm"
LOCALE = {"en": "en_CA", "fr": "fr_CA"}
HTML_LANG = {"en": "en-CA", "fr": "fr-CA"}
# The site's own sections (the app). A home section must be #home/<section>, a bare #contact opens sign-in.
APP_LINK = {"en": "/", "fr": "/?lang=fr"}
UI = {
    "en": {"services": "Services", "pricing": "Pricing", "method": "How we work", "work": "Work",
           "quote": "Get a fixed quote", "home": "Home", "faq": "Questions", "related": "Related services",
           "switch": "Français", "switch_label": "Lire cette page en français", "privacy": "Privacy & Terms",
           "feedback": "Submit feedback", "dev": "Contact developer", "parent": "Parent company",
           "tagline": "Apps built at AI speed. Signed off by senior engineers.",
           "where": "Montréal, Québec · English and French · in person or remote",
           "menu": "Main menu", "crumbs": "Breadcrumb", "skip": "Skip to content"},
    "fr": {"services": "Services", "pricing": "Tarifs", "method": "Notre méthode", "work": "Réalisations",
           "quote": "Obtenir une soumission à prix fixe", "home": "Accueil", "faq": "Questions fréquentes",
           "related": "Services connexes", "switch": "English", "switch_label": "Read this page in English",
           "privacy": "Confidentialité et conditions", "feedback": "Envoyer un commentaire",
           "dev": "Contacter le développeur", "parent": "Société mère",
           "tagline": "Des applications bâties à la vitesse de l'IA. Validées par des ingénieurs seniors.",
           "where": "Montréal, Québec · français et anglais · en personne ou à distance",
           "menu": "Menu principal", "crumbs": "Fil d'Ariane", "skip": "Aller au contenu"},
}
SERVICE_KEYS = ["client-portal", "admin-panel", "mvp", "data-platform", "saas", "api-integration"]
NAV_KEYS = ["services", "pricing", "how-we-work"]
# Pricing milestones, for the Offer list in the pricing page's structured data (CAD, cumulative totals)
MILESTONES = [("Launch", 30000), ("Operate", 75000), ("Scale", 150000), ("Complete", 300000)]


def page(key, lang):
    p = PAGES.get(key) or {}
    return p.get(lang)


def slug(key, lang):
    p = page(key, lang)
    return p["slug"] if p else None


def _app(lang, section=None):
    base = APP_LINK[lang]
    if section in ("work", "guides", "privacy"):
        return base + "#" + section
    return base + ("#home/" + section if section else "")


def _inline(text):
    """**bold** and [text](link), after escaping. Links to other pages stay relative."""
    t = html.escape(text, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)

    def link(m):
        href = m.group(2)
        if href.startswith(SITE):
            href = href[len(SITE):] or "/"
        if href.startswith("/#") or href.startswith("#"):
            href = href.lstrip("/")
            name = href[1:].split("/")[0]
            href = "/" + href if name in ("work", "guides", "privacy", "home") else "/#home/" + href[1:]
        return '<a href="%s">%s</a>' % (html.escape(href, quote=True), m.group(1))
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, t)


def _plain(text):
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return t.replace("**", "")


def _ld(key, lang, p):
    url = SITE + p["slug"]
    page_id = url + "#page"
    graph = [{"@type": "WebPage", "@id": page_id, "url": url, "name": p["title"], "description": p["description"],
              "inLanguage": HTML_LANG[lang], "isPartOf": {"@id": SITE + "/#website"}, "about": {"@id": ORG},
              "breadcrumb": {"@id": url + "#crumbs"}, "publisher": {"@id": ORG}}]
    crumbs = [(UI[lang]["home"], SITE + ("/fr" if lang == "fr" else "/"))]
    if key in SERVICE_KEYS:
        crumbs.append((UI[lang]["services"], SITE + slug("services", lang)))
    if key != "fr-home":
        crumbs.append((p["h1"], url))
    graph.append({"@type": "BreadcrumbList", "@id": url + "#crumbs", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]})
    stype = PAGES[key].get("service_type")
    if stype:
        graph.append({"@type": "Service", "@id": url + "#service", "name": p["h1"], "serviceType": stype,
                      "description": p["description"], "url": url, "provider": {"@id": ORG},
                      "areaServed": [{"@type": "City", "name": "Montréal"}, {"@type": "Country", "name": "Canada"},
                                     {"@type": "Country", "name": "United States"}],
                      "availableLanguage": ["en", "fr"],
                      "offers": {"@type": "AggregateOffer", "priceCurrency": "CAD", "lowPrice": "30000",
                                 "highPrice": "300000", "offerCount": len(MILESTONES)}})
    if key == "pricing":
        graph.append({"@type": "OfferCatalog", "@id": url + "#milestones", "name": p["h1"], "itemListElement": [
            {"@type": "Offer", "name": n, "price": str(v), "priceCurrency": "CAD", "seller": {"@id": ORG},
             "description": "Cumulative project total after the %s milestone" % n} for n, v in MILESTONES]})
    if p.get("faq"):
        graph.append({"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
            {"@type": "Question", "name": _plain(q), "acceptedAnswer": {"@type": "Answer", "text": _plain(a)}}
            for q, a in p["faq"]]})
    # The business itself, the same entity the home page describes (one @id across the site)
    graph.append({"@type": ["ProfessionalService", "Organization"], "@id": ORG, "name": "Addanapp",
                  "url": SITE + "/", "logo": SITE + "/_/theme/logo-512.png",
                  "address": {"@type": "PostalAddress", "addressLocality": "Montréal", "addressRegion": "QC",
                              "addressCountry": "CA"},
                  "knowsLanguage": ["en", "fr"], "sameAs": ["https://www.youtube.com/@addanapp"]})
    graph.append({"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": "Addanapp",
                  "publisher": {"@id": ORG}})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False).replace("</", "<\\/")


def _alternates(key):
    out = []
    en, fr = slug(key, "en"), slug(key, "fr")
    if key == "fr-home":
        en = "/"
    if en:
        out.append('<link rel="alternate" hreflang="en" href="%s%s">' % (SITE, en))
    if fr:
        out.append('<link rel="alternate" hreflang="fr" href="%s%s">' % (SITE, fr))
    if en:
        out.append('<link rel="alternate" hreflang="x-default" href="%s%s">' % (SITE, en))
    return "\n".join(out)


def _section(s, idx, pricing):
    body = "".join("<p>%s</p>" % _inline(x) for x in s.get("paragraphs", []))
    if s.get("bullets"):
        body += "<ul>%s</ul>" % "".join("<li>%s</li>" % _inline(b) for b in s["bullets"])
    h2 = html.escape(s["h2"], quote=False)
    if pricing and re.search(r"\$|\d\s?000", s["h2"]) and ("—" in s["h2"] or "–" in s["h2"]):
        parts = re.split(r"\s[—–]\s", s["h2"], 1)
        name, price = parts[0], parts[-1]
        return ('<section class="ms" id="s%d"><div class="ms-n">%d</div><h2><span>%s</span> <b>%s</b></h2>%s</section>'
                % (idx, idx, html.escape(name, quote=False), html.escape(price, quote=False), body))
    return '<section id="s%d"><h2>%s</h2>%s</section>' % (idx, h2, body)


def render(key, lang):
    p = page(key, lang)
    if not p:
        return None
    u, e = UI[lang], html.escape
    other = "fr" if lang == "en" else "en"
    other_slug = "/" if (key == "fr-home" and other == "en") else slug(key, other)
    url = SITE + p["slug"]
    nav = "".join('<a href="%s"%s>%s</a>' % (slug(k, lang), ' aria-current="page"' if k == key else "",
                                             u["services"] if k == "services" else u["pricing"] if k == "pricing"
                                             else u["method"]) for k in NAV_KEYS if slug(k, lang))
    nav += '<a href="%s">%s</a>' % (_app(lang, "work"), u["work"])
    switch = ('<a class="lang" href="%s" hreflang="%s" lang="%s" title="%s">%s</a>'
              % (other_slug, other, other, e(u["switch_label"]), u["switch"])) if other_slug else ""
    crumbs = ['<a href="%s">%s</a>' % ("/fr" if lang == "fr" else "/", u["home"])]
    if key in SERVICE_KEYS:
        crumbs.append('<a href="%s">%s</a>' % (slug("services", lang), u["services"]))
    pricing = key == "pricing"
    sections = "".join(_section(s, i + 1, pricing) for i, s in enumerate(p.get("sections", [])))
    if pricing:
        n = 0
        def renum(m):
            nonlocal n
            n += 1
            return '<div class="ms-n">%d</div>' % n
        sections = re.sub(r'<div class="ms-n">\d+</div>', renum, sections)
    faq = "".join('<div class="q"><h3>%s</h3><p>%s</p></div>' % (_inline(q), _inline(a)) for q, a in p.get("faq", []))
    related = ""
    if key in SERVICE_KEYS or key in ("pricing", "how-we-work", "law-25"):
        items = [k for k in SERVICE_KEYS if k != key and page(k, lang)][:6]
        related = '<nav class="rel" aria-label="%s"><h2>%s</h2><ul>%s</ul></nav>' % (
            e(u["related"]), u["related"],
            "".join('<li><a href="%s">%s</a></li>' % (slug(k, lang), e(page(k, lang)["h1"])) for k in items))
    cta = p.get("cta") or {}
    quote_href = _app(lang, "contact")
    return TEMPLATE % {
        "lang": HTML_LANG[lang], "title": e(p["title"]), "desc": e(p["description"]), "url": e(url),
        "alts": _alternates(key), "locale": LOCALE[lang], "locale_alt": LOCALE[other], "ld": _ld(key, lang, p),
        "home": "/fr" if lang == "fr" else "/", "nav": nav, "switch": switch, "menu": e(u["menu"]),
        "quote": e(u["quote"]), "quote_href": quote_href, "skip": e(u["skip"]),
        "crumbs": ('<nav class="crumbs" aria-label="%s">%s</nav>' % (e(u["crumbs"]), " / ".join(crumbs)))
        if key != "fr-home" else "",
        "h1": e(p["h1"]), "intro": "".join("<p>%s</p>" % _inline(x) for x in p.get("intro", [])),
        "sections": sections,
        "faq": ('<section class="faq" id="faq"><h2>%s</h2>%s</section>' % (u["faq"], faq)) if faq else "",
        "related": related,
        "cta_h": e(cta.get("heading", u["quote"])), "cta_t": _inline(cta.get("text", "")),
        "cta_b": e(cta.get("button", u["quote"])), "tagline": e(u["tagline"]), "where": e(u["where"]),
        "privacy": e(u["privacy"]), "privacy_href": _app(lang, "privacy"), "feedback": e(u["feedback"]),
        "prepsto": PREPSTO, "dev": e(u["dev"]), "parent": e(u["parent"]), "pagecls": "pricing" if pricing else "",
    }


TEMPLATE = """<!doctype html>
<html lang="%(lang)s"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<link rel="canonical" href="%(url)s">
%(alts)s
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<meta property="og:type" content="website"><meta property="og:site_name" content="Addanapp">
<meta property="og:title" content="%(title)s"><meta property="og:description" content="%(desc)s">
<meta property="og:url" content="%(url)s"><meta property="og:image" content="https://addanapp.com/_/theme/og-image.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:locale" content="%(locale)s"><meta property="og:locale:alternate" content="%(locale_alt)s">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0B1220">
<link rel="icon" type="image/svg+xml" href="/_/theme/logo.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/_/theme/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/_/theme/apple-touch-icon.png">
<link rel="alternate" type="text/plain" title="For AI assistants" href="/llms.txt">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<script type="application/ld+json">%(ld)s</script>
<script src="https://prepsto.com/_/theme/widget.js" data-prepsto="e4xsnwm" data-button="false" data-label="Submit feedback" async></script>
<style>
:root{--night:#0B1220;--night2:#121b2e;--on-night:#f4f6fb;--on-night-2:#b9c1d3;--page:#fbfaf7;--card:#ffffff;
--text:#141824;--muted:#556074;--line:#e5e3dc;--accent:#ff6a3d;--accent-ink:#ffffff;--link:#1f4fd6;--focus:#ff6a3d}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--page:#0e1422;--card:#151d30;--text:#e9edf5;
--muted:#a3adc2;--line:#25304a;--link:#8fb0ff}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%%}
body{margin:0;overflow-wrap:break-word;background:var(--page);color:var(--text);font:17px/1.65 Inter,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--link);text-underline-offset:3px}a:focus-visible,button:focus-visible{outline:3px solid var(--focus);outline-offset:2px;border-radius:4px}
.skip{position:absolute;left:-999px;top:8px;background:var(--card);color:var(--text);padding:8px 14px;z-index:9}.skip:focus{left:16px}
.wrap{max-width:1040px;margin:0 auto;padding:0 16px}.narrow{max-width:760px}
header.top{background:var(--night);color:var(--on-night)}
.bar{display:flex;align-items:center;gap:18px;min-height:64px;flex-wrap:wrap;padding-top:8px;padding-bottom:8px}
.brand{display:flex;align-items:center;gap:10px;color:var(--on-night);text-decoration:none;font-weight:700;font-size:18px;margin-right:auto}
.brand img{width:30px;height:30px;border-radius:8px}
.bar nav{display:flex;gap:4px;flex-wrap:wrap}
.bar nav a,.lang{color:var(--on-night-2);text-decoration:none;font-size:15px;padding:8px 10px;border-radius:8px}
.bar nav a:hover,.lang:hover,.bar nav a[aria-current]{color:var(--on-night);background:rgba(255,255,255,.07)}
.btn{display:inline-flex;align-items:center;gap:8px;background:var(--accent);color:var(--accent-ink);text-decoration:none;
font-weight:600;padding:12px 20px;border-radius:999px;transition:transform .15s ease}.btn:hover{transform:translateY(-1px)}
.btn.sm{padding:8px 16px;font-size:15px}
.hero{padding-top:28px;padding-bottom:56px}.crumbs{font-size:14px;color:var(--on-night-2);margin-bottom:22px}.crumbs a{color:var(--on-night-2)}
h1,h2{font-family:"Instrument Serif",Georgia,serif;font-weight:400;letter-spacing:-.01em}
h1{font-size:clamp(34px,6vw,56px);line-height:1.08;margin:0 0 18px;max-width:18ch}
.hero p{color:var(--on-night-2);font-size:19px;max-width:62ch;margin:0 0 14px}.hero p strong{color:var(--on-night)}
.hero a:not(.btn){color:var(--on-night)}.hero .btn{margin-top:14px}
main{padding:48px 0 24px}
main section{margin:0 0 44px}
h2{font-size:clamp(27px,4vw,36px);line-height:1.15;margin:0 0 12px}h3{font-size:18px;margin:0 0 6px}
main p{margin:0 0 14px;max-width:70ch}main ul{padding-left:22px;max-width:68ch}main li{margin:6px 0}
.pricing main .ms{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:26px 26px 12px;position:relative}
.ms-n{position:absolute;top:22px;right:24px;width:34px;height:34px;border-radius:50%%;background:var(--night);color:var(--on-night);
display:grid;place-items:center;font-weight:700;font-size:15px}
.ms h2{display:flex;flex-direction:column;gap:2px;padding-right:48px}.ms h2 b{font-family:Inter,sans-serif;font-size:20px;font-weight:700;color:var(--accent)}
.faq .q{border-top:1px solid var(--line);padding:18px 0 4px}
.rel ul{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px;max-width:none}
.rel li{margin:0}.rel a{display:block;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;
text-decoration:none;color:var(--text);font-weight:600}.rel a:hover{border-color:var(--accent)}
.cta{background:var(--night);color:var(--on-night);border-radius:22px;padding:36px 28px;margin:12px 0 56px}
.cta h2{color:var(--on-night)}.cta p{color:var(--on-night-2)}.cta a:not(.btn){color:var(--on-night)}
footer{border-top:1px solid var(--line);padding:26px 0 40px;color:var(--muted);font-size:15px}
footer p{margin:4px 0}footer a{color:var(--muted)}
@media (max-width:640px){.bar nav{order:3;width:100%%;overflow-x:auto}.bar .btn.sm{display:none}.cta{padding:28px 20px}}
@media (prefers-reduced-motion:reduce){.btn{transition:none}}
</style></head>
<body class="%(pagecls)s">
<a class="skip" href="#main">%(skip)s</a>
<header class="top"><div class="wrap bar">
<a class="brand" href="%(home)s"><img src="/_/theme/logo.svg" alt="" width="30" height="30">Addanapp</a>
<nav aria-label="%(menu)s">%(nav)s</nav>%(switch)s
<a class="btn sm" href="%(quote_href)s">%(quote)s</a>
</div>
<div class="wrap hero">%(crumbs)s
<h1>%(h1)s</h1>%(intro)s
<a class="btn" href="%(quote_href)s">%(quote)s <span aria-hidden="true">→</span></a>
</div></header>
<main id="main"><div class="wrap narrow">
%(sections)s
%(faq)s
%(related)s
<section class="cta"><h2>%(cta_h)s</h2><p>%(cta_t)s</p><a class="btn" href="%(quote_href)s">%(cta_b)s <span aria-hidden="true">→</span></a></section>
</div></main>
<footer><div class="wrap">
<p><strong>Addanapp</strong> · %(tagline)s</p><p>%(where)s</p>
<p><a href="%(prepsto)s" target="_blank" rel="noopener" data-prepsto-open>%(feedback)s</a> · <a href="%(privacy_href)s">%(privacy)s</a>
· %(dev)s: <a href="https://arkvital.com" target="_blank" rel="noopener">arkvital.com</a>
· %(parent)s: <a href="https://addanapp.com">addanapp.com</a> · <a href="/llms.txt">llms.txt</a></p>
</div></footer>
</body></html>
"""


def all_routes():
    """[(path, key, lang)] for every page that exists."""
    out = []
    for key in PAGES:
        for lang in ("en", "fr"):
            s = slug(key, lang)
            if s:
                out.append((s, key, lang))
    return out


ROUTE = getattr(anvil.server, "route", None)
if ROUTE:
    def _page_route(i, path, key, lang):
        def seo_page(**params):
            return anvil.server.HttpResponse(
                200, anvil.BlobMedia("text/html; charset=utf-8", render(key, lang).encode("utf-8")),
                headers={"Cache-Control": "public, max-age=3600"})
        seo_page.__name__ = "seo_page_%d" % i
        return anvil.server.route(path)(seo_page)

    for _i, (_path, _key, _lang) in enumerate(all_routes()):
        _page_route(_i, _path, _key, _lang)
