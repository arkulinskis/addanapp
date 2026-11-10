"""Landing-page data that depends on the visitor's language or is shared by several pages: the films, the partner
deck, the free guides and the project-brief choices. The page copy itself is in Pages/Landing/form_template.html
(English, translated through i18n.apply)."""
from . import i18n

# Blank until the official address is ready; every spot that shows it hides itself while empty.
CONTACT_EMAIL = ''

# The Addanapp YouTube channel and the film about Addanapp itself, one per language (APP_MAKER/youtube/manifest.json:
# addanapp, addanapp-fr/ru/lv). Visitors get the film in their language, with links to the others.
# The film is a click-to-play embed: nothing loads from YouTube until the visitor presses play (Landing.play).
YT_CHANNEL = 'https://www.youtube.com/@addanapp'
YT_FILMS = {  # lang: (video id, length, cover in theme/assets)
  'en': ('wzCMxAdyrHo', '1:06', 'yt-addanapp.jpg'),
  'fr': ('MKOIck45xWQ', '1:19', 'yt-addanapp-fr.jpg'),
  'ru': ('awzVxnVHrco', '1:24', 'yt-addanapp-ru-2.jpg'),
  'lv': ('yzDUcUaH2q0', '1:24', 'yt-addanapp-lv.jpg'),
}
YT_FILM, YT_FILM_LENGTH, YT_COVER = YT_FILMS.get(i18n.lang, YT_FILMS['en'])
# A second film shows another kind of work: Parapeet, a live 2023 app we rebuilt (before/after, English only).
YT_REBUILD, YT_REBUILD_LENGTH, YT_REBUILD_COVER = 'FW-j_xL_DWo', '1:29', 'yt-parapeet.jpg'

# The partner deck, one PDF per language (rendered by .claude/skills/addanapp/scripts/deck_pdf.py from the
# "Addanapp Partner Deck" Slides artifact; its firms slide names firms only as examples).
# The visitor's language is the main download; the other three are linked under it.
DECKS = {  # lang: (pdf, cover, size)
  'en': ('addanapp-partner-deck.pdf', 'partner-deck-cover.jpg', '3 MB'),
  'fr': ('addanapp-partner-deck-fr.pdf', 'partner-deck-cover-fr.jpg', '3 MB'),
  'ru': ('addanapp-partner-deck-ru.pdf', 'partner-deck-cover-ru.jpg', '3 MB'),
  'lv': ('addanapp-partner-deck-lv.pdf', 'partner-deck-cover-lv.jpg', '3 MB'),
}
DECK_SLIDES = 20
DECK_LANG = i18n.lang if i18n.lang in DECKS else 'en'
DECK_COVER = '_/theme/' + DECKS[DECK_LANG][1]


def deck(code=None):
  """Attributes of a link that downloads the partner deck in one language (default: the visitor's)."""
  code = code if code in DECKS else DECK_LANG
  name = 'Addanapp-partner-deck' + ('' if code == 'en' else '-' + code.upper()) + '.pdf'
  return {'href': '_/theme/' + DECKS[code][0], 'target': '_blank', 'rel': 'noopener', 'download': name, 'hreflang': code}


def film_url(code):
  return 'https://www.youtube.com/watch?v=' + YT_FILMS[code][0]


def other_languages():
  """The languages other than the visitor's, for "Other languages:" link rows."""
  return [(c, i18n.NAMES[c]) for c in i18n.CODES if c != i18n.lang]


# Free guides (lead magnets). PDFs and covers live in theme/assets/guides/.
# The #guides page asks for an email before showing the download links (api_public.request_guides).
# (slug, number, title, hook, what's inside, pages)
GUIDES = [
  ('spreadsheet-escape-plan', '01', 'Your Spreadsheet Is Already an App',
   'Is your business running on a spreadsheet only one person understands?',
   ['The 10-sign test', 'A calculator for what "it works fine" really costs', 'A five-move plan to graduate safely'], 10),
  ('one-page-app-brief', '02', 'The One-Page App Brief',
   'Got an app idea but no idea what it should cost?',
   ['The 7 boxes of a good brief', 'A fill-in template and a worked example', '12 questions to ask any developer'], 10),
  ('ai-built-human-signed', '03', 'AI-Built, Human-Signed',
   'Your next developer will use AI. Who checks the code?',
   ['What AI is great at, and where it trips', 'The 10-point sign-off checklist', 'Green flags and red flags'], 9),
  ('build-buy-or-bolt-on', '04', 'Build, Buy or Bolt On',
   'Paying for six tools to do one job?',
   ['An 8-question decision test', 'A 3-year cost worksheet', 'Five small add-ons that pay off fast'], 9),
  ('law-25-app-checklist', '05', 'Law 25 for Your Next App',
   'Collecting names and emails in Québec? Read this first.',
   ['A 15-point privacy checklist', 'Requirements to paste into your developer brief', 'Bonus: email lists and CASL'], 9),
]
GUIDE_SLUGS = [g[0] for g in GUIDES]
# Same English labels as api_public.GUIDE_SITUATIONS; the last two count as buying signals there.
GUIDE_SITUATIONS = ['We run on spreadsheets', 'We pay for too many tools', 'Just curious', 'I have an app idea',
                    "We're building something now"]


def guide_cover(slug):
  return f'_/theme/guides/{slug}.jpg'


# Lead form choices are saved in English (the value) and shown translated (the label).
LEAD_TYPES = ['A new app or product', 'A feature for an existing app', 'An admin panel or internal tool', 'A client portal',
              'API or integration work', 'Taking over an existing app', 'Something else']
LEAD_BUDGETS = ['Not sure yet', 'Under $30k', '$30k – $75k', '$75k – $150k', '$150k – $300k', '$300k+']
