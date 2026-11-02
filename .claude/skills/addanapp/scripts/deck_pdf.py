"""Render the Addanapp partner deck (Slides artifact X7izxcayZdhgbzmsdrN9Ua) into print.html, then a PDF.

1. Artifact read of project/deck.json and every project/slides/<id>.html into one folder (keep the project/ layout).
2. Copy this script into that folder and run it (needs Pillow): it maps the /_blob/ images to the App Board hero shots
   (byte-identical copies), draws the x-icons, drops the slide that names specific firms and renumbers the footers.
3. chrome --headless=new --no-pdf-header-footer --virtual-time-budget=15000 --print-to-pdf=deck.pdf print.html
4. Copy deck.pdf to theme/assets/addanapp-partner-deck.pdf; update DECK_SLIDES and the size text in content.py.
"""
import json, re, os, subprocess, sys, hashlib
from pathlib import Path
from PIL import Image

HERE = Path(__file__).parent
HEROES = Path(r"C:\Users\arkvi\Documents\CLAUDE\APP_MAKER\board\heroes")
IMG = HERE / "img"
IMG.mkdir(exist_ok=True)
deck = json.loads((HERE / "project/deck.json").read_text(encoding="utf-8"))

# blob id -> hero key, from the alt text (verified: the blobs are the App Board hero PNGs)
KNOWN = {"134116cd4b03a11a6f85301a0e1370d8": "addanapp"}
blob_key = dict(KNOWN)
for f in (HERE / "project/slides").glob("*.html"):
  for bid, alt in re.findall(r'src="/_blob/([0-9a-f]+)" alt="([^"]*)"', f.read_text(encoding="utf-8")):
    if bid in blob_key:
      continue
    name = alt.split(":")[0].split(" landing")[0]
    key = re.sub(r"[^a-z0-9]", "", name.lower())
    if (HEROES / f"{key}.png").exists():
      blob_key[bid] = key

# check the one we downloaded matches
dl = HERE / "blobs/d155a038a6da3add90f431068c086fe5.png"
if dl.exists():
  assert hashlib.sha256(dl.read_bytes()).hexdigest() == hashlib.sha256((HEROES / f"{blob_key['d155a038a6da3add90f431068c086fe5']}.png").read_bytes()).hexdigest()

for bid, key in blob_key.items():
  out = IMG / f"{key}.jpg"
  if not out.exists():
    Image.open(HEROES / f"{key}.png").convert("RGB").save(out, quality=84, optimize=True, progressive=True)

ICONS = {
  "Key": '<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M17 6l3 3M15 8l2 2"/>',
  "CheckCircle": '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l3 3 5-6"/>',
  "Verified": '<path d="M12 2l2.4 2.1 3.2-.3.9 3.1 2.8 1.6-1.2 3 1.2 3-2.8 1.6-.9 3.1-3.2-.3L12 22l-2.4-2.1-3.2.3-.9-3.1-2.8-1.6 1.2-3-1.2-3 2.8-1.6.9-3.1 3.2.3z"/><path d="M8.5 12.2l2.4 2.4 4.6-5"/>',
  "Lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
  "Globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/>',
  "Chat": '<path d="M4 5h16v11H9l-5 4z"/>',
}


def icon(m):
  name, style = m.group(1), m.group(2)
  return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
          f'stroke-linejoin="round" style="{style};flex:none">{ICONS[name]}</svg>')


slides = []
PUBLIC_SKIP = {"fit"}  # names specific firms: kept out of the public download
for sid in [x for x in deck["order"] if x not in PUBLIC_SKIP]:
  h = (HERE / f"project/slides/{sid}.html").read_text(encoding="utf-8")
  h = re.sub(r"<aside>.*?</aside>", "", h, flags=re.S)
  h = re.sub(r'src="/_blob/([0-9a-f]+)"', lambda m: f'src="img/{blob_key[m.group(1)]}.jpg"', h)
  h = re.sub(r'<x-icon name="(\w+)" style="([^"]*)"></x-icon>', icon, h)
  h = h.replace("Nouveau Stay", "ArviStay")  # renamed 2026-11-02
  n = len(slides) + 1
  h = re.sub(r">(\d\d)</p>(\s*</div>\s*</section>)", lambda m: ">%02d</p>%s" % (n, m.group(2)), h)
  slides.append(h)

fonts = "".join(f'<link rel="stylesheet" href="{f["href"]}">' for f in deck["faces"].values())
html = f"""<!doctype html><html><head><meta charset="utf-8"><title>{deck['title']}</title>{fonts}
<style>
@page {{ size: 1920px 1080px; margin: 0 }}
* {{ box-sizing: border-box; margin: 0; padding: 0 }}
html, body {{ background: #0B1220; -webkit-print-color-adjust: exact; print-color-adjust: exact }}
section {{ width: 1920px; height: 1080px; position: relative; overflow: hidden; page-break-after: always; break-after: page }}
section:last-child {{ page-break-after: auto }}
img {{ display: block }}
x-shape {{ display: block; flex: none }}
x-shape[kind=ellipse] {{ border-radius: 50% }}
x-shape[kind=arrow-right] {{ clip-path: polygon(0 35%, 60% 35%, 60% 0, 100% 50%, 60% 100%, 60% 65%, 0 65%) }}
ul, ol {{ padding-left: 1.2em }}
table {{ border-collapse: collapse; width: 100% }}
th, td {{ text-align: left; padding: 22px 24px; vertical-align: top; line-height: 1.4 }}
th {{ font-weight: 600; border-bottom: 2px solid #E6E3DA }}
td {{ border-bottom: 1px solid #E6E3DA }}
a {{ color: inherit }}
</style></head><body>{''.join(slides)}</body></html>"""
(HERE / "print.html").write_text(html, encoding="utf-8")
print("slides", len(slides), "images", len(blob_key))
