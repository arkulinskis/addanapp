"""Regenerate the Work ItemList in Addanapp's head JSON-LD from portfolio.py, add the YouTube channel and the film.

Run from anywhere: python -I .claude/skills/addanapp/scripts/jsonld.py  (after any change to PROJECTS or VIDEOS).
"""
import json, re, sys, types, importlib.util
from pathlib import Path

APP = Path(__file__).resolve().parents[4]  # the addanapp repo

# load portfolio.py with stand-ins for its sibling modules
pkg = types.ModuleType("aa"); pkg.__path__ = []; sys.modules["aa"] = pkg
for name, attrs in {"ui": {"esc": lambda s: s}, "icons": {"icon": lambda *a, **k: ""},
                    "i18n": {"t": lambda s, **k: s.format(**k) if k else s, "tn": lambda n, a, b, **k: (a if n == 1 else b).format(n=n)}}.items():
  m = types.ModuleType("aa." + name); m.__dict__.update(attrs); sys.modules["aa." + name] = m
spec = importlib.util.spec_from_file_location("aa.portfolio", APP / "client_code/portfolio.py")
pf = importlib.util.module_from_spec(spec); sys.modules["aa.portfolio"] = pf; spec.loader.exec_module(pf)

Y = APP / "anvil.yaml"
text = Y.read_text(encoding="utf-8")
open_tag = '    <script type="application/ld+json">\n'
a = text.index(open_tag) + len(open_tag)
b = text.index('    </script>', a)
raw = text[a:b]
data = json.loads(raw)
# the block is json.dumps(indent=1) shifted right by 4 spaces: check we can reproduce it exactly
again = '\n'.join('    ' + ln for ln in json.dumps(data, indent=1, ensure_ascii=False).split('\n')) + '\n'
assert again == raw, "JSON-LD layout differs; adjust the dump"

graph = data["@graph"]
org = next(g for g in graph if g.get("@id") == "https://addanapp.com/#org")
org["sameAs"] = ["https://www.youtube.com/@addanapp"]

old = next(g for g in graph if g.get("@type") == "ItemList")
old_cat = {it["item"]["name"]: it["item"].get("applicationCategory") for it in old["itemListElement"]}
CAT_APP = {"business": "BusinessApplication", "tools": "UtilitiesApplication", "learn": "EducationalApplication",
           "games": "GameApplication", "vr": "GameApplication", "mobile": "LifestyleApplication", "sites": "BusinessApplication"}
OVERRIDE = {"Reelstuber": "MultimediaApplication", "VideoBlog Buddy": "MultimediaApplication", "ImgNovella": "DesignApplication",
            "Make Your Own Clothes": "DesignApplication", "Fillfox": "BusinessApplication", "Hookline": "BusinessApplication",
            "Marguru": "BusinessApplication", "Sheetsmith": "BusinessApplication", "Tai Chi Please": "HealthApplication",
            "Brain Mechanic": "HealthApplication", "Little Hero Books": "EducationalApplication", "PerfectCast": "SocialNetworkingApplication"}
items = []
pos = 0
for key, label in pf.CATEGORIES[1:]:  # index order: grouped by category
  for p in pf.in_category(key):
    if not p.get("domain"):
      continue
    pos += 1
    app = {"@type": "SoftwareApplication", "name": p["name"], "url": "https://" + p["domain"], "description": p["blurb"],
           "creator": {"@id": "https://addanapp.com/#org"}, "keywords": ", ".join(p["tags"] + [label]),
           "applicationCategory": old_cat.get(p["name"]) or OVERRIDE.get(p["name"]) or CAT_APP[p["cat"]], "operatingSystem": "Web"}
    vid = pf.VIDEOS.get(p["key"])
    if vid:
      app["subjectOf"] = {"@type": "VideoObject", "name": p["name"] + " in about a minute", "url": "https://www.youtube.com/watch?v=" + vid,
                          "thumbnailUrl": "https://i.ytimg.com/vi/%s/hqdefault.jpg" % vid, "uploadDate": "2026-11-02"}
    items.append({"@type": "ListItem", "position": pos, "item": app})
old["itemListElement"] = items

if not any(g.get("@id") == "https://addanapp.com/#film" for g in graph):
  graph.append({"@type": "VideoObject", "@id": "https://addanapp.com/#film",
                "name": "Addanapp: Apps Built at AI Speed, Signed Off by Senior Engineers",
                "description": "A one-minute film about Addanapp, the Montréal studio that builds web apps, admin panels, client portals and data platforms with AI speed and senior-engineer sign-off.",
                "thumbnailUrl": "https://addanapp.com/_/theme/yt-addanapp.jpg", "uploadDate": "2026-11-02", "duration": "PT1M6S",
                "embedUrl": "https://www.youtube-nocookie.com/embed/wzCMxAdyrHo", "url": "https://www.youtube.com/watch?v=wzCMxAdyrHo",
                "publisher": {"@id": "https://addanapp.com/#org"}})

new = '\n'.join('    ' + ln for ln in json.dumps(data, indent=1, ensure_ascii=False).split('\n')) + '\n'
Y.write_text(text[:a] + new + text[b:], encoding="utf-8", newline="\n")
print("items", len(items), "with films", sum(1 for i in items if "subjectOf" in i["item"]))
