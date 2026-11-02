"""Render the Addanapp partner deck (Slides artifact X7izxcayZdhgbzmsdrN9Ua) to PDF, in English, French, Russian or Latvian.

1. Artifact read of project/deck.json and every project/slides/<id>.html into one folder (keep the project/ layout).
2. python deck_pdf.py <that folder> [--lang en|fr|ru|lv|all]
   - maps the /_blob/ images to the App Board hero shots (byte-identical copies) and draws the x-icons;
   - for fr/ru/lv, swaps every text fragment and alt text for its entry in deck_i18n/<lang>.json (keyed by the English
     fragment). New English text with no entry is listed as MISSING: add it to all three files and run again;
   - Russian headlines use PT Serif (Instrument Serif has no Cyrillic), like the website;
   - writes print-<lang>.html, renders deck-<lang>.pdf with headless Chrome, and cover-<lang>.jpg (page 1, 960x540);
   - runs a layout check (text running into the footer or off the slide) and prints any problems; fix them by shortening
     the translation, or add a per-language rule to FIT below.
3. Copy the PDFs to theme/assets/addanapp-partner-deck[-fr|-ru|-lv].pdf and the covers to partner-deck-cover[-fr|-ru|-lv].jpg;
   update DECKS (slides, sizes) in client_code/content.py.
"""
import argparse, json, re, subprocess, sys, hashlib
from pathlib import Path
from PIL import Image

SCRIPTS = Path(__file__).parent
HEROES = Path(r"C:\Users\arkvi\Documents\CLAUDE\APP_MAKER\board\heroes")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
LANGS = ["en", "fr", "ru", "lv"]

ap = argparse.ArgumentParser()
ap.add_argument("src", nargs="?", default=str(SCRIPTS), help="folder holding project/deck.json and project/slides/")
ap.add_argument("--lang", default="en", help="en, fr, ru, lv or all")
ap.add_argument("--no-pdf", action="store_true", help="only write print-<lang>.html and run the layout check")
args = ap.parse_args()
HERE = Path(args.src)
IMG = HERE / "img"
IMG.mkdir(exist_ok=True)
deck = json.loads((HERE / "project/deck.json").read_text(encoding="utf-8"))

# blob id -> hero key, from the (English) alt text (verified: the blobs are the App Board hero PNGs)
KNOWN = {"134116cd4b03a11a6f85301a0e1370d8": "addanapp", "354a571b87c22451b09e0781328cc2b2": "nouveaustay"}
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

# Per-language CSS for slides whose translation runs longer than the English (keyed by slide id).
# The translations are 15-30% longer, so the card grid (fleet) and the five-row table (fit) get a little tighter.
_TIGHT = (
  "#fleet > div:nth-of-type(2) > div { padding: 28px 32px !important; gap: 10px !important }"
  "#fleet > div:nth-of-type(2) p:last-child { font-size: 24px !important }"
  "#fit table { font-size: 24px !important }"
  "#fit td, #fit th { padding: 15px 22px !important; line-height: 1.35 !important }"
)
FIT = {
  "ru": _TIGHT,
  "fr": _TIGHT,
  "lv": _TIGHT,
}

PT_SERIF = "https://fonts.googleapis.com/css2?family=PT+Serif:ital,wght@0,400;0,700;1,400&display=swap"

# Layout check: runs in the page once fonts are ready and writes its findings into <pre id="fitcheck">.
CHECK_JS = r"""
<script>
document.fonts.ready.then(function () {
  var out = [];
  document.querySelectorAll('section').forEach(function (s, i) {
    var sr = s.getBoundingClientRect();
    var foot = null;
    s.querySelectorAll(':scope > div').forEach(function (d) {
      if (getComputedStyle(d).position === 'absolute' && d.style.bottom) foot = d;
    });
    var limit = foot ? foot.getBoundingClientRect().top - 12 : sr.bottom - 8;
    s.querySelectorAll('p, h1, h2, h3, td, th, img').forEach(function (el) {
      if (foot && foot.contains(el)) return;
      var r = el.getBoundingClientRect();
      if (r.height === 0) return;
      var txt = (el.textContent || el.alt || '').trim().slice(0, 50);
      if (r.bottom > limit + 0.5) out.push((i + 1) + ' ' + s.id + ': below the content area by ' + Math.round(r.bottom - limit) + 'px: ' + txt);
      if (r.right > sr.right - 40 && el.tagName !== 'IMG') out.push((i + 1) + ' ' + s.id + ': past the right edge: ' + txt);
      if (el.scrollWidth > el.clientWidth + 2 && el.tagName !== 'IMG') out.push((i + 1) + ' ' + s.id + ': word too wide for its box: ' + txt);
    });
  });
  var pre = document.createElement('pre'); pre.id = 'fitcheck'; pre.textContent = out.join('\n') || 'OK';
  document.body.appendChild(pre);
});
</script>"""


def icon(m):
  name, style = m.group(1), m.group(2)
  return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
          f'stroke-linejoin="round" style="{style};flex:none">{ICONS[name]}</svg>')


def translator(lang):
  if lang == "en":
    return None, set()
  tr = json.loads((SCRIPTS / "deck_i18n" / f"{lang}.json").read_text(encoding="utf-8"))
  return {k: v for k, v in tr.items() if not k.startswith("_")}, set()


def build(lang):
  tr, missing = translator(lang)

  def text(m):
    s = m.group(1)
    if tr is None or not s.strip() or re.fullmatch(r"\s*\d+\s*", s):
      return m.group(0)
    if s in tr:
      return ">" + tr[s] + "<"
    if re.search(r"[a-z]{3,}\s+[a-z]{3,}", s):   # looks like prose, not a product or library name
      missing.add(s)
    return m.group(0)

  def alt(m):
    s = m.group(1)
    if tr is None:
      return m.group(0)
    if s in tr:
      return f'alt="{tr[s]}"'
    if " " in s and ":" in s:
      missing.add(s)
    return m.group(0)

  slides = []
  for sid in deck["order"]:
    h = (HERE / f"project/slides/{sid}.html").read_text(encoding="utf-8")
    h = re.sub(r"<aside>.*?</aside>", "", h, flags=re.S)
    h = re.sub(r'src="/_blob/([0-9a-f]+)"', lambda m: f'src="img/{blob_key[m.group(1)]}.jpg"', h)
    h = re.sub(r'<x-icon name="(\w+)" style="([^"]*)"></x-icon>', icon, h)
    h = re.sub(r">([^<>]+)<", text, h)
    h = re.sub(r'alt="([^"]*)"', alt, h)
    if lang == "ru":
      h = h.replace("'Instrument Serif', Georgia, serif", "'PT Serif', Georgia, serif")
    n = len(slides) + 1
    h = re.sub(r">(\d\d)</p>(\s*</div>\s*</section>)", lambda m: ">%02d</p>%s" % (n, m.group(2)), h)
    slides.append(h)

  faces = [f["href"] for f in deck["faces"].values()] + ([PT_SERIF] if lang == "ru" else [])
  fonts = "".join(f'<link rel="stylesheet" href="{u}">' for u in faces)
  title = deck["title"] if tr is None else tr.get("Addanapp · Partner briefing", deck["title"])
  html = f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>{title}</title>{fonts}
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
{FIT.get(lang, '')}
</style></head><body>{''.join(slides)}</body></html>"""
  page = HERE / f"print-{lang}.html"
  page.write_text(html, encoding="utf-8")
  if missing:
    print(f"[{lang}] MISSING translations ({len(missing)}):")
    for s in sorted(missing):
      print("   ", json.dumps(s, ensure_ascii=False))

  # layout check on a copy with the check script (the PDF is printed from the clean page)
  chk = HERE / f"check-{lang}.html"
  chk.write_text(html.replace("</body>", CHECK_JS + "</body>"), encoding="utf-8")
  dom = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--window-size=1920,1080", "--virtual-time-budget=20000",
                        "--dump-dom", chk.resolve().as_uri()], capture_output=True, text=True, encoding="utf-8").stdout
  m = re.search(r'<pre id="fitcheck">(.*?)</pre>', dom, re.S)
  print(f"[{lang}] layout:", (m.group(1).replace("&gt;", ">").replace("&amp;", "&") if m else "check did not run"))

  if args.no_pdf:
    return
  pdf = HERE / f"deck-{lang}.pdf"
  subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=20000",
                  f"--print-to-pdf={pdf}", page.resolve().as_uri()], capture_output=True)
  import fitz  # PyMuPDF
  doc = fitz.open(pdf)
  pg = doc[0]
  pix = pg.get_pixmap(matrix=fitz.Matrix(960 / pg.rect.width, 960 / pg.rect.width))
  cover = HERE / f"cover-{lang}.png"
  pix.save(cover)
  Image.open(cover).convert("RGB").save(HERE / f"cover-{lang}.jpg", quality=84, optimize=True, progressive=True)
  print(f"[{lang}] {pdf.name}: {doc.page_count} pages, {pdf.stat().st_size / 1e6:.1f} MB; cover-{lang}.jpg")


for lang in (LANGS if args.lang == "all" else [args.lang]):
  build(lang)
