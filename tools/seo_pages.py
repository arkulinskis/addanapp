"""Build the service/pricing/French pages: tools/seo_pages/*.json -> server_code/seo_pages_text.py, then check them.

    python -I tools/seo_pages.py            build + check
    python -I tools/seo_pages.py --preview  also write every page as HTML into tools/seo_pages/_preview/

The JSON files are the text (one per page, "en" + "fr"); server_code/seo_pages.py draws them.
Checks: titles 30-65 chars, descriptions 110-170, one H1, every internal link points at a real page,
EN/FR twins link to each other, JSON-LD parses, sitemap list in APP_MAKER/seo/apps/addanapp.json matches.
"""
import importlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "seo_pages"
OUT = ROOT / "server_code" / "seo_pages_text.py"
FACTS = ROOT.parent / "APP_MAKER" / "seo" / "apps" / "addanapp.json"
ORDER = ["fr-home", "services", "client-portal", "admin-panel", "mvp", "data-platform", "saas", "api-integration",
         "pricing", "how-we-work", "law-25"]
APP_ANCHORS = {"/", "/?lang=fr"}


def build():
    pages = {}
    for key in ORDER:
        f = SRC / (key + ".json")
        d = json.loads(f.read_text(encoding="utf-8"))
        pages[key] = {"service_type": d.get("service_type"), "en": d.get("en"), "fr": d.get("fr")}
    body = json.dumps(pages, ensure_ascii=False, indent=1)
    body = body.replace(": null", ": None").replace(": true", ": True").replace(": false", ": False")
    text = ('"""Text of the service, pricing and French pages. Built by tools/seo_pages.py from tools/seo_pages/*.json:\n'
            'edit the JSON and rebuild, don\'t edit this file."""\nPAGES = ' + body + "\n")
    OUT.write_bytes(text.encode("utf-8"))
    return pages


def check(pages, preview=False):
    sys.path.insert(0, str(ROOT))
    if "anvil" not in sys.modules:  # stand-in so the server module imports outside Anvil (no routes registered)
        import types
        fake, server = types.ModuleType("anvil"), types.ModuleType("anvil.server")
        server.route = None
        fake.server = server
        sys.modules["anvil"], sys.modules["anvil.server"] = fake, server
    mod = importlib.import_module("server_code.seo_pages")
    problems = []
    slugs = {p[lang]["slug"] for p in pages.values() for lang in ("en", "fr") if p.get(lang)}
    if preview:
        (SRC / "_preview").mkdir(exist_ok=True)
    for path, key, lang in mod.all_routes():
        p = pages[key][lang]
        out = mod.render(key, lang)
        name = "%s-%s" % (key, lang)
        if not 30 <= len(p["title"]) <= 65:
            problems.append("%s: title is %d chars" % (name, len(p["title"])))
        if not 110 <= len(p["description"]) <= 170:
            problems.append("%s: description is %d chars" % (name, len(p["description"])))
        if out.count("<h1") != 1:
            problems.append("%s: %d h1" % (name, out.count("<h1")))
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', out, re.S):
            try:
                json.loads(m.group(1).replace("<\\/", "</"))
            except ValueError as e:
                problems.append("%s: JSON-LD %s" % (name, e))
        for href in re.findall(r'href="(/[^"]*)"', out):
            h = href.split("#")[0] or "/"
            if h in slugs or h in APP_ANCHORS or h.startswith("/_/theme/") or h == "/llms.txt":
                continue
            problems.append("%s: link to unknown page %s" % (name, href))
        other = "fr" if lang == "en" else "en"
        twin = pages[key].get(other)
        if twin and ('hreflang="%s" href="https://addanapp.com%s"' % (other, twin["slug"])) not in out:
            problems.append("%s: no hreflang to %s" % (name, twin["slug"]))
        words = len(re.sub(r"<[^>]+>", " ", out.split("<main")[1] if "<main" in out else out).split())
        print("%-22s %-48s %5d words  %s" % (name, path, words, p["title"]))
        if preview:
            (SRC / "_preview" / (name + ".html")).write_text(out.replace('href="/', 'href="https://addanapp.com/')
                                                             .replace('src="/', 'src="https://addanapp.com/'),
                                                             encoding="utf-8")
    facts = json.loads(FACTS.read_text(encoding="utf-8"))
    extra = set(facts.get("sitemap_extra", []))
    missing = sorted(slugs - extra)
    if missing:
        problems.append("sitemap_extra in seo/apps/addanapp.json is missing: %s" % ", ".join(missing))
    print("\n%d pages, %d problems" % (len(mod.all_routes()), len(problems)))
    for x in problems:
        print("  -", x)
    return not problems


if __name__ == "__main__":
    ok = check(build(), preview="--preview" in sys.argv)
    sys.exit(0 if ok else 1)
