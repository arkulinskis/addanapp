"""Portfolio: projects we've shipped, with illustrated previews (inline SVG, no screenshots needed)."""
from .ui import esc
from .icons import icon

CATEGORIES = [
  ('all', 'All work'),
  ('business', 'Working businesses'),
  ('tools', 'Useful tools'),
  ('games', 'Engaging games'),
  ('mobile', 'Mobile-style apps'),
  ('sites', 'Websites'),
]
CAT = dict(CATEGORIES)

PROJECTS = [
  {
    'key': 'planplate', 'name': 'PlanPlate', 'domain': 'planplate.com', 'cat': 'business',
    'blurb': 'A restaurant reservation and content API platform. Managers run bookings for every location from one portal, and guests book straight from the restaurant\'s own website.',
    'built': ['Multi-restaurant manager portal', 'Drag-and-drop floor plans and table joins',
              'Opening-hour rules, special days and auto-approval', 'Public reservation and content API'],
    'tags': ['SaaS', 'Public API', 'Admin portal'], 'color': '#1F6B63', 'bg': '#DCE7E8', 'art': 'planplate',
  },
  {
    'key': 'varnote', 'name': 'Varnote', 'domain': 'varnote-offline.web.app', 'cat': 'tools',
    'blurb': 'A faster note-taking app built around inline tagging. Type #tags as you write, then slice thousands of notes down to the ones you need in a keystroke.',
    'built': ['Inline #tags while you type', 'Instant multi-tag filtering', 'Offline-first and installable'],
    'tags': ['Productivity', 'Offline-first', 'PWA'], 'color': '#3446D8', 'bg': '#E8EBFF', 'art': 'varnote',
  },
  {
    'key': 'adorablescience', 'name': 'Adorable Science', 'domain': 'adorablescience.com', 'cat': 'tools',
    'blurb': 'A multi-user science blog with a real editorial workflow. Writers draft, editors review and nothing is published until it has been approved.',
    'built': ['Writer accounts and an editorial review queue', 'Citation meter and reviewer checklists',
              'Approve, or send back with notes'],
    'tags': ['CMS', 'Roles & moderation', 'Publishing'], 'color': '#D9487A', 'bg': '#FDECF2', 'art': 'blog',
  },
  {
    'key': 'citycrossers', 'name': 'CityCrossers', 'domain': 'citycrossers.com', 'cat': 'tools',
    'blurb': 'Tinder for walking groups. Swipe on group walks, plan routes with snack stops on a live map, and meet people who would rather stroll 20 km than sprint 5.',
    'built': ['Swipe deck ranked by match score', 'Map route planner with break estimates',
              'Points, perks and a moderation admin'],
    'tags': ['Social', 'Maps', 'Gamification'], 'color': '#17A673', 'bg': '#E2F5EC', 'art': 'map',
  },
  {
    'key': 'busybun', 'name': 'BusyBun', 'domain': 'busybun.com', 'cat': 'games',
    'blurb': 'A gamified, slightly obsessive hunt for steamed-dumpling ingredients. Run errands, clear pests and fill your bun across 18 hand-built levels.',
    'built': ['18 levels across 6 themed territories', 'Built-in level builder', 'Original pests, music and mechanics'],
    'tags': ['Game', 'Level editor', 'Canvas'], 'color': '#C27A22', 'bg': '#F8EAD0', 'art': 'bun',
  },
  {
    'key': 'doremiroad', 'name': 'DoremiRoad', 'domain': 'doremiroad.com', 'cat': 'games',
    'blurb': 'A game for the musically inclined: learn theory by conquering a map. Play with a MIDI keyboard, your computer keys or touch.',
    'built': ['Web MIDI, keyboard and touch input', 'Lessons, notes, chords and ear training', 'Level editor for teachers'],
    'tags': ['EdTech', 'Web MIDI', 'Game'], 'color': '#6A4BF0', 'bg': '#ECE8FF', 'art': 'piano',
  },
  {
    'key': 'poundfighter', 'name': 'PoundFighter', 'domain': 'poundfighter.com', 'cat': 'mobile',
    'blurb': 'A quick exercise motivator. Micro-workouts become monster fights, and the microphone counts your reps: grunt, clap or shout "HUP!".',
    'built': ['Voice rep counting through the mic', '36 collectible monsters in 4 rarities', 'Daily punch card, ranks and shop'],
    'tags': ['Mobile-first', 'Voice', 'Fitness'], 'color': '#E2452F', 'bg': '#FDE6E1', 'art': 'pound',
  },
  {
    'key': 'parapeet', 'name': 'Parapeet', 'domain': 'parapeet.com', 'cat': 'mobile',
    'blurb': 'A French learning app built around real-life situations, from ordering at a café to small talk with neighbours. Short, playful and mobile-first.',
    'built': ['Lessons built around real situations', 'Bite-sized, mobile-first sessions', 'Story-driven, playful design'],
    'tags': ['Mobile-first', 'Language learning', 'EdTech'], 'color': '#3F9A35', 'bg': '#E4F2DD', 'art': 'parrot',
  },
  {
    'key': 'dilettante', 'name': 'Dilettante', 'domain': 'dilettante.com', 'cat': 'sites',
    'blurb': 'A classic restaurant website with live PlanPlate reservations built in. Guests can browse the menu and book a table without leaving the page.',
    'built': ['Classic, fast restaurant website', 'Live PlanPlate reservation widget', 'Menus and events from the content API'],
    'tags': ['Website', 'API integration', 'Hospitality'], 'color': '#7C2D2D', 'bg': '#F3EAE1', 'art': 'resto',
  },
]

# ------------------------------------------------------------------ illustrations

FONT = "font-family=\"Inter, system-ui, sans-serif\""


def _browser(inner, url, bg):
  return f'''<svg viewBox="0 0 400 250" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
  <rect width="400" height="250" fill="{bg}"/>
  <rect x="30" y="28" width="340" height="230" rx="12" fill="#0B1220" opacity=".07"/>
  <rect x="28" y="22" width="344" height="236" rx="12" fill="#fff"/>
  <path d="M28 34a12 12 0 0 1 12-12h320a12 12 0 0 1 12 12v8H28z" fill="#F4F3EF"/>
  <circle cx="42" cy="32" r="3" fill="#DDD9CF"/><circle cx="52" cy="32" r="3" fill="#DDD9CF"/><circle cx="62" cy="32" r="3" fill="#DDD9CF"/>
  <rect x="140" y="26.5" width="120" height="11" rx="5.5" fill="#fff"/>
  <text x="200" y="34.6" text-anchor="middle" font-size="6.5" fill="#8C94A3" {FONT}>{url}</text>
  {inner}</svg>'''


def _phone(inner, bg, extra=''):
  return f'''<svg viewBox="0 0 400 250" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
  <rect width="400" height="250" fill="{bg}"/>{extra}
  <rect x="141" y="22" width="124" height="250" rx="22" fill="#0B1220" opacity=".1"/>
  <rect x="138" y="16" width="124" height="250" rx="22" fill="#111827"/>
  <rect x="144" y="22" width="112" height="240" rx="17" fill="#fff"/>
  <rect x="182" y="27" width="36" height="8" rx="4" fill="#111827"/>
  {inner}</svg>'''


def art_planplate(p):
  c, s = p['color'], '#CFE3E0'
  tables = ''
  for (x, y, r, on) in [(130, 78, 11, 1), (166, 78, 11, 0), (202, 78, 11, 1), (238, 78, 11, 1),
                        (130, 118, 11, 0), (166, 118, 11, 1), (220, 122, 16, 1)]:
    tables += f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c if on else s}"/>'
  tables += f'<rect x="118" y="146" width="44" height="18" rx="5" fill="{c}"/><rect x="170" y="146" width="44" height="18" rx="5" fill="{s}"/>'
  rows = ''
  for i, (t, w, col) in enumerate([('18:00', 46, c), ('18:30', 36, '#E8A33D'), ('19:00', 52, c), ('19:15', 30, c), ('20:00', 40, s)]):
    y = 62 + i * 21
    rows += (f'<rect x="276" y="{y}" width="86" height="16" rx="4" fill="#F6F8F8"/><text x="282" y="{y + 10.8}" font-size="6.5" fill="#5D6778" {FONT}>{t}</text>'
             f'<rect x="306" y="{y + 5}" width="{w}" height="6" rx="3" fill="{col}"/>')
  bars = ''
  for i, (x, w, col) in enumerate([(112, 70, c), (190, 46, '#E8A33D'), (244, 90, c), (130, 54, s), (196, 80, c), (284, 40, c)]):
    y = 196 + (i // 3) * 16
    bars += f'<rect x="{x}" y="{y}" width="{w}" height="10" rx="5" fill="{col}" opacity="{1 if col != s else .9}"/>'
  inner = f'''<rect x="28" y="42" width="74" height="216" fill="#F3F7F7"/>
  <circle cx="44" cy="58" r="7" fill="none" stroke="#0B1220" stroke-width="2.4"/><rect x="56" y="55" width="34" height="6" rx="3" fill="{c}"/>
  <rect x="38" y="80" width="54" height="9" rx="4.5" fill="{c}" opacity=".16"/><rect x="38" y="97" width="44" height="6" rx="3" fill="#C9D3D3"/>
  <rect x="38" y="111" width="50" height="6" rx="3" fill="#C9D3D3"/><rect x="38" y="125" width="38" height="6" rx="3" fill="#C9D3D3"/>
  <rect x="112" y="56" width="152" height="118" rx="8" fill="#FAFBFB" stroke="#E4ECEC"/>
  {tables}{rows}
  <line x1="112" y1="186" x2="362" y2="186" stroke="#EEF2F2"/>{bars}'''
  return _browser(inner, 'app.planplate.com', p['bg'])


def art_varnote(p):
  c = p['color']
  notes = ''
  data = [(['#idea', '#q4'], 120), (['#client'], 150), (['#idea'], 96), (['#todo', '#client'], 136)]
  for i, (tags, w) in enumerate(data):
    y = 84 + i * 40
    on = i in (0, 2)
    notes += f'<rect x="44" y="{y}" width="200" height="32" rx="7" fill="{"#F4F5FF" if on else "#fff"}" stroke="{"#C9CFFF" if on else "#EDEBE5"}"/>'
    notes += f'<rect x="54" y="{y + 8}" width="{w}" height="5.5" rx="2.75" fill="#3A4457" opacity=".75"/>'
    tx = 54
    for t in tags:
      tw = 8 + len(t) * 4.6
      hot = t == '#idea'
      notes += (f'<rect x="{tx}" y="{y + 18}" width="{tw}" height="9" rx="4.5" fill="{c if hot else "#EEF0F4"}"/>'
                f'<text x="{tx + 4}" y="{y + 24.7}" font-size="6" font-weight="600" fill="{"#fff" if hot else "#5D6778"}" {FONT}>{t}</text>')
      tx += tw + 5
  inner = f'''<rect x="44" y="52" width="200" height="22" rx="11" fill="#F4F3EF"/>
  <circle cx="57" cy="63" r="4" fill="none" stroke="#8C94A3" stroke-width="1.4"/>
  <rect x="68" y="58.5" width="28" height="9" rx="4.5" fill="{c}"/><text x="72" y="65" font-size="6" font-weight="600" fill="#fff" {FONT}>#idea</text>
  <text x="104" y="65.2" font-size="6.5" fill="#8C94A3" {FONT}>2 of 248 notes</text>
  {notes}
  <rect x="256" y="52" width="102" height="192" rx="8" fill="#FBFBFD" stroke="#EDEBE5"/>
  <rect x="268" y="66" width="62" height="7" rx="3.5" fill="#182031"/>
  <rect x="268" y="84" width="78" height="4.5" rx="2.25" fill="#C5C9D3"/><rect x="268" y="95" width="70" height="4.5" rx="2.25" fill="#C5C9D3"/>
  <rect x="268" y="106" width="40" height="4.5" rx="2.25" fill="#C5C9D3"/><rect x="311" y="104" width="26" height="8.5" rx="4.25" fill="{c}"/>
  <rect x="268" y="120" width="74" height="4.5" rx="2.25" fill="#C5C9D3"/><rect x="268" y="131" width="58" height="4.5" rx="2.25" fill="#C5C9D3"/>
  <rect x="268" y="142" width="2" height="10" fill="{c}"/>'''
  return _browser(inner, 'varnote-offline.web.app', p['bg'])


def art_blog(p):
  c = p['color']
  inner = f'''<rect x="28" y="42" width="344" height="24" fill="#fff"/><line x1="28" y1="66" x2="372" y2="66" stroke="#F1EEE8"/>
  <circle cx="48" cy="54" r="6" fill="{c}"/><rect x="58" y="51" width="56" height="6" rx="3" fill="#182031"/>
  <rect x="280" y="49" width="40" height="10" rx="5" fill="#F4F3EF"/><rect x="326" y="49" width="34" height="10" rx="5" fill="{c}"/>
  <rect x="60" y="80" width="190" height="72" rx="8" fill="{p['bg']}"/>
  <circle cx="110" cy="116" r="20" fill="{c}" opacity=".25"/><circle cx="148" cy="108" r="11" fill="{c}" opacity=".45"/><circle cx="186" cy="122" r="16" fill="{c}" opacity=".3"/>
  <path d="M100 116a10 10 0 0 1 20 0" stroke="{c}" stroke-width="2.4" fill="none"/>
  <rect x="60" y="164" width="170" height="9" rx="4.5" fill="#182031"/><rect x="60" y="179" width="120" height="9" rx="4.5" fill="#182031"/>
  <rect x="60" y="198" width="190" height="4.5" rx="2.25" fill="#C5C9D3"/><rect x="60" y="208" width="176" height="4.5" rx="2.25" fill="#C5C9D3"/>
  <rect x="60" y="218" width="184" height="4.5" rx="2.25" fill="#C5C9D3"/><rect x="246" y="216" width="12" height="8" rx="2" fill="{c}" opacity=".2"/>
  <text x="249" y="222.2" font-size="5.5" font-weight="700" fill="{c}" {FONT}>1</text>
  <rect x="266" y="80" width="94" height="96" rx="8" fill="#fff" stroke="#EDEBE5"/>
  <text x="276" y="96" font-size="6.5" font-weight="700" fill="#182031" {FONT}>Review checklist</text>
  <circle cx="281" cy="110" r="4.5" fill="#0E9F6E"/><path d="M279 110l1.5 1.5 2.6-2.8" stroke="#fff" stroke-width="1.2" fill="none"/><rect x="290" y="108" width="54" height="4.5" rx="2.25" fill="#C5C9D3"/>
  <circle cx="281" cy="126" r="4.5" fill="#0E9F6E"/><path d="M279 126l1.5 1.5 2.6-2.8" stroke="#fff" stroke-width="1.2" fill="none"/><rect x="290" y="124" width="46" height="4.5" rx="2.25" fill="#C5C9D3"/>
  <circle cx="281" cy="142" r="4.5" fill="none" stroke="#C5C9D3" stroke-width="1.2"/><rect x="290" y="140" width="50" height="4.5" rx="2.25" fill="#C5C9D3"/>
  <rect x="276" y="154" width="74" height="12" rx="6" fill="#0E9F6E"/><text x="313" y="162" text-anchor="middle" font-size="6" font-weight="700" fill="#fff" {FONT}>Approve &amp; publish</text>
  <g transform="rotate(-8 312 206)"><rect x="276" y="192" width="74" height="26" rx="5" fill="none" stroke="{c}" stroke-width="1.8"/>
  <text x="313" y="203.5" text-anchor="middle" font-size="6" font-weight="800" fill="{c}" letter-spacing="1" {FONT}>UNDER THE</text>
  <text x="313" y="212" text-anchor="middle" font-size="6" font-weight="800" fill="{c}" letter-spacing="1" {FONT}>MICROSCOPE</text></g>'''
  return _browser(inner, 'adorablescience.com', p['bg'])


def art_map(p):
  c = p['color']
  inner = f'''<rect x="28" y="42" width="344" height="216" fill="#EEF3EC"/>
  <g stroke="#fff" stroke-width="7" stroke-linecap="round" fill="none"><path d="M20 120 L380 90"/><path d="M20 200 L380 175"/><path d="M110 40 L140 260"/><path d="M270 40 L262 260"/></g>
  <g stroke="#fff" stroke-width="3" stroke-linecap="round" fill="none" opacity=".9"><path d="M20 160 L380 135"/><path d="M200 40 L205 260"/></g>
  <ellipse cx="320" cy="70" rx="44" ry="22" fill="#CDEBD9"/><ellipse cx="74" cy="226" rx="40" ry="20" fill="#CDEBD9"/>
  <path d="M28 186 C 90 170, 140 214, 220 190 S 330 160, 372 176" stroke="#BFE3F5" stroke-width="14" fill="none"/>
  <path d="M64 78 C 110 64, 130 120, 170 120 S 230 90, 262 132 S 240 196, 200 204" stroke="{c}" stroke-width="3.2" fill="none" stroke-dasharray="1 6" stroke-linecap="round"/>
  <circle cx="64" cy="78" r="9" fill="#fff" stroke="{c}" stroke-width="2.4"/><circle cx="170" cy="120" r="9" fill="#FFE8DB" stroke="#FF7A3D" stroke-width="2.4"/>
  <circle cx="262" cy="132" r="9" fill="#FFE8DB" stroke="#FF7A3D" stroke-width="2.4"/><circle cx="200" cy="204" r="9" fill="#fff" stroke="{c}" stroke-width="2.4"/>
  <g transform="rotate(5 316 170)"><rect x="276" y="112" width="84" height="112" rx="10" fill="#fff" stroke="#E5ECE7"/>
  <rect x="276" y="112" width="84" height="54" rx="10" fill="#FFD9A8"/><rect x="276" y="150" width="84" height="16" fill="#FFD9A8"/>
  <text x="318" y="146" text-anchor="middle" font-size="22" {FONT}>&#129360;</text>
  <rect x="286" y="174" width="60" height="6" rx="3" fill="#182031"/><rect x="286" y="186" width="40" height="4.5" rx="2.25" fill="#C5C9D3"/>
  <circle cx="296" cy="208" r="8" fill="#fff" stroke="#E2E8E4"/><path d="M293 205l6 6M299 205l-6 6" stroke="#D14343" stroke-width="1.4"/>
  <circle cx="340" cy="208" r="8" fill="{c}"/><path d="M336.5 208.5l2.3 2.3 4.3-4.6" stroke="#fff" stroke-width="1.5" fill="none"/></g>'''
  return _browser(inner, 'citycrossers.com', p['bg'])


def art_bun(p):
  c = p['color']
  tiles = ''
  for r in range(6):
    for col in range(9):
      x, y = 40 + col * 36, 48 + r * 34
      shade = '#F3DDB3' if (r + col) % 2 == 0 else '#EED2A0'
      tiles += f'<rect x="{x}" y="{y}" width="36" height="34" fill="{shade}"/>'
  inner = f'''<g>{tiles}</g>
  <rect x="148" y="116" width="36" height="34" fill="#B98A56"/><rect x="184" y="116" width="36" height="34" fill="#B98A56"/>
  <rect x="148" y="116" width="72" height="6" fill="#9E7140"/>
  <circle cx="94" cy="96" r="7" fill="#7A3E1D"/><circle cx="104" cy="104" r="5" fill="#7A3E1D"/><circle cx="86" cy="106" r="4" fill="#7A3E1D"/>
  <circle cx="300" cy="200" r="10" fill="#3F8F3F"/><path d="M296 196q4-8 8 0" stroke="#2E6E2E" stroke-width="2" fill="none"/>
  <circle cx="330" cy="88" r="9" fill="#D24C3A"/><rect x="328" y="76" width="4" height="6" rx="2" fill="#3F8F3F"/>
  <ellipse cx="244" cy="202" rx="20" ry="7" fill="#000" opacity=".12"/>
  <path d="M224 196 q0 -30 20 -30 q20 0 20 30z" fill="#FFF8EC" stroke="#5B3A1E" stroke-width="2.2"/>
  <path d="M236 172 q8 -8 16 0 M240 168 q4 6 8 0" stroke="#C9A27A" stroke-width="1.6" fill="none"/>
  <circle cx="238" cy="186" r="2" fill="#2B1B10"/><circle cx="250" cy="186" r="2" fill="#2B1B10"/>
  <circle cx="233" cy="191" r="2.6" fill="#F2A6A6"/><circle cx="255" cy="191" r="2.6" fill="#F2A6A6"/>
  <path d="M241 191 q3 3 6 0" stroke="#2B1B10" stroke-width="1.4" fill="none"/>
  <rect x="40" y="48" width="324" height="20" fill="#0B1220" opacity=".55"/>
  <text x="50" y="62" font-size="8" font-weight="700" fill="#fff" {FONT}>Grandma's Kitchen · 1-2</text>
  <g transform="translate(270 52)"><rect width="88" height="12" rx="6" fill="#fff" opacity=".2"/><rect width="58" height="12" rx="6" fill="{c}"/>
  <text x="6" y="8.6" font-size="6.5" font-weight="700" fill="#fff" {FONT}>Filling 4/6</text></g>'''
  return _browser(inner, 'busybun.com', p['bg'])


def art_piano(p):
  c = p['color']
  keys = ''
  for i in range(14):
    x = 46 + i * 22.7
    hot = i in (0, 2, 4)
    keys += f'<rect x="{x}" y="176" width="21.7" height="70" rx="3" fill="{c if hot else "#fff"}" stroke="#D9D5E8"/>'
  for i in [0, 1, 3, 4, 5, 7, 8, 10, 11, 12]:
    x = 46 + i * 22.7 + 15
    keys += f'<rect x="{x}" y="176" width="13" height="42" rx="2" fill="#1B1730"/>'
  staff = ''.join(f'<line x1="60" y1="{86 + j * 9}" x2="250" y2="{86 + j * 9}" stroke="#C9C3E2" stroke-width="1.2"/>' for j in range(5))
  notes = ''
  for (x, y) in [(104, 122), (140, 113), (176, 104)]:
    notes += f'<ellipse cx="{x}" cy="{y}" rx="7" ry="5.2" fill="{c}" transform="rotate(-18 {x} {y})"/><line x1="{x + 6.4}" y1="{y - 1}" x2="{x + 6.4}" y2="{y - 30}" stroke="{c}" stroke-width="1.6"/>'
  inner = f'''<rect x="28" y="42" width="344" height="216" fill="#FBFAFF"/>
  <text x="66" y="68" font-size="8" font-weight="700" fill="#182031" {FONT}>Play the C major triad</text>
  {staff}<line x1="104" y1="131" x2="118" y2="131" stroke="#C9C3E2" stroke-width="1.2"/>{notes}
  <text x="68" y="114" font-size="34" fill="#3A4457" font-family="serif">&#119070;</text>
  <g transform="translate(270 60)">
    <path d="M10 6 L46 0 L80 10 L84 46 L60 70 L22 66 L4 40 Z" fill="{c}" opacity=".18" stroke="{c}" stroke-width="1.2"/>
    <path d="M10 6 L46 0 L44 34 L4 40 Z" fill="{c}" opacity=".7"/>
    <path d="M46 0 L80 10 L84 46 L44 34 Z" fill="{c}" opacity=".45"/>
    <circle cx="44" cy="34" r="4" fill="#fff" stroke="{c}" stroke-width="1.6"/>
    <text x="44" y="88" text-anchor="middle" font-size="6.5" font-weight="700" fill="#5D6778" {FONT}>Realm of Harmony</text>
  </g>{keys}'''
  return _browser(inner, 'doremiroad.com', p['bg'])


def art_pound(p):
  c = p['color']
  bars = ''
  for i, h in enumerate([6, 12, 20, 30, 18, 26, 34, 22, 12, 8, 16, 10]):
    bars += f'<rect x="{158 + i * 7.4}" y="{226 - h / 2}" width="4" height="{h}" rx="2" fill="{c}" opacity="{.4 + (h / 60)}"/>'
  inner = f'''<rect x="144" y="40" width="112" height="16" fill="#fff"/>
  <text x="152" y="52" font-size="7" font-weight="800" fill="#182031" {FONT}>Fight 2/3</text>
  <rect x="210" y="45" width="38" height="9" rx="4.5" fill="#FFF3D6"/><text x="215" y="51.8" font-size="6" font-weight="700" fill="#B7791F" {FONT}>&#163; 1,240</text>
  <rect x="152" y="62" width="96" height="94" rx="12" fill="{p['bg']}"/>
  <path d="M176 140 q-6 -40 24 -52 q30 12 24 52z" fill="{c}" opacity=".85"/>
  <circle cx="191" cy="108" r="5" fill="#fff"/><circle cx="209" cy="108" r="5" fill="#fff"/>
  <circle cx="192" cy="109" r="2.2" fill="#111"/><circle cx="210" cy="109" r="2.2" fill="#111"/>
  <path d="M190 124 l5 -4 5 4 5 -4 5 4" stroke="#fff" stroke-width="1.8" fill="none"/>
  <path d="M182 92 l-6 -10 M218 92 l6 -10" stroke="{c}" stroke-width="3" stroke-linecap="round"/>
  <rect x="160" y="146" width="80" height="6" rx="3" fill="#fff" opacity=".7"/><rect x="160" y="146" width="30" height="6" rx="3" fill="#fff"/>
  <text x="200" y="186" text-anchor="middle" font-size="22" font-weight="800" fill="#182031" {FONT}>12</text>
  <text x="200" y="198" text-anchor="middle" font-size="6.5" font-weight="600" fill="#8C94A3" {FONT}>SQUATS · SAY &#8220;HUP!&#8221;</text>
  {bars}'''
  extra = (f'<circle cx="70" cy="60" r="34" fill="{c}" opacity=".12"/><circle cx="335" cy="190" r="46" fill="{c}" opacity=".1"/>'
           f'<g transform="translate(296 66)"><rect width="74" height="30" rx="15" fill="#fff"/><text x="37" y="19.5" text-anchor="middle" font-size="9" font-weight="800" fill="{c}" {FONT}>HUP! +3</text></g>'
           f'<g transform="translate(34 160)"><rect width="80" height="30" rx="15" fill="#fff"/><text x="40" y="19.5" text-anchor="middle" font-size="8" font-weight="700" fill="#182031" {FONT}>Combo x4 &#128293;</text></g>')
  return _phone(inner, p['bg'], extra)


def art_parrot(p):
  c = p['color']
  inner = f'''<rect x="144" y="40" width="112" height="20" fill="#F7FAF5"/>
  <text x="152" y="53" font-size="7" font-weight="800" fill="#2A3A6B" {FONT}>Au café</text>
  <rect x="216" y="46" width="32" height="8" rx="4" fill="{p['bg']}"/><rect x="216" y="46" width="20" height="8" rx="4" fill="{c}"/>
  <g transform="translate(152 70)"><circle cx="9" cy="9" r="9" fill="#E8F1FF"/><path d="M5 12q4-12 9-3" stroke="#5DBBD9" stroke-width="3" fill="none"/>
  <rect x="22" y="0" width="70" height="26" rx="9" fill="#F1F4F7"/><text x="28" y="11" font-size="6.6" fill="#182031" {FONT}>Bonjour ! Pour</text><text x="28" y="20" font-size="6.6" fill="#182031" {FONT}>vous, madame ?</text></g>
  <g transform="translate(166 104)"><rect x="0" y="0" width="82" height="26" rx="9" fill="{c}"/><text x="7" y="11" font-size="6.6" fill="#fff" {FONT}>Un café crème,</text><text x="7" y="20" font-size="6.6" fill="#fff" {FONT}>s'il vous plaît.</text></g>
  <g transform="translate(152 140)"><rect x="22" y="0" width="64" height="17" rx="8" fill="#F1F4F7"/><text x="28" y="11" font-size="6.6" fill="#182031" {FONT}>Et avec ça ?</text></g>
  <text x="152" y="176" font-size="6" font-weight="700" fill="#8C94A3" letter-spacing=".6" {FONT}>CHOOSE YOUR ANSWER</text>
  <rect x="152" y="182" width="96" height="16" rx="8" fill="#fff" stroke="{c}" stroke-width="1.4"/><text x="200" y="192.6" text-anchor="middle" font-size="6.6" font-weight="600" fill="#182031" {FONT}>Un croissant aussi.</text>
  <rect x="152" y="202" width="96" height="16" rx="8" fill="#fff" stroke="#E2E8E0"/><text x="200" y="212.6" text-anchor="middle" font-size="6.6" fill="#5D6778" {FONT}>C'est tout, merci.</text>
  <rect x="152" y="226" width="96" height="18" rx="9" fill="#2A3A6B"/><text x="200" y="237.6" text-anchor="middle" font-size="7" font-weight="700" fill="#fff" {FONT}>Continuer</text>'''
  extra = (f'<path d="M40 250 q20 -90 70 -110 q-30 40 -20 110z" fill="{c}" opacity=".2"/>'
           f'<path d="M330 250 q10 -120 60 -150 q-20 60 -10 150z" fill="{c}" opacity=".18"/>'
           f'<path d="M300 40 q30 -10 50 10 q-25 4 -50 -10z" fill="{c}" opacity=".25"/>')
  return _phone(inner, p['bg'], extra)


def art_resto(p):
  c = p['color']
  inner = f'''<rect x="28" y="42" width="344" height="92" fill="#2A1A17"/>
  <rect x="28" y="42" width="344" height="92" fill="url(#rg)" opacity=".9"/>
  <defs><radialGradient id="rg" cx=".75" cy=".3" r=".8"><stop offset="0" stop-color="#8A4B2A"/><stop offset="1" stop-color="#2A1A17"/></radialGradient></defs>
  <text x="56" y="62" font-size="6" fill="#E8D5B5" letter-spacing="2" {FONT}>EST. 1987 · MONTR&#201;AL</text>
  <text x="56" y="92" font-size="26" font-style="italic" fill="#FBF3E6" font-family="Georgia, serif">Dilettante</text>
  <text x="56" y="110" font-size="7" fill="#E8D5B5" {FONT}>Cuisine du march&#233; · Wine bar</text>
  <g fill="#E8D5B5" opacity=".7"><rect x="236" y="56" width="24" height="3" rx="1.5"/><rect x="268" y="56" width="24" height="3" rx="1.5"/><rect x="300" y="56" width="24" height="3" rx="1.5"/></g>
  <text x="56" y="156" font-size="9" font-style="italic" fill="#2A1A17" font-family="Georgia, serif">Ce soir</text>
  <g font-size="6.5" fill="#3A4457" {FONT}>
    <text x="56" y="174">Tartare de saumon</text><text x="196" y="174" text-anchor="end">18</text>
    <text x="56" y="190">Canard confit, lentilles</text><text x="196" y="190" text-anchor="end">32</text>
    <text x="56" y="206">Tarte au sucre</text><text x="196" y="206" text-anchor="end">11</text></g>
  <line x1="56" y1="179" x2="196" y2="179" stroke="#EFE7DC"/><line x1="56" y1="195" x2="196" y2="195" stroke="#EFE7DC"/>
  <rect x="222" y="118" width="134" height="124" rx="10" fill="#fff" stroke="#EADFD2"/>
  <text x="234" y="136" font-size="7.5" font-weight="700" fill="#182031" {FONT}>Reserve a table</text>
  <text x="234" y="146" font-size="5.5" fill="#8C94A3" {FONT}>Powered by PlanPlate</text>
  <rect x="234" y="154" width="52" height="16" rx="5" fill="#F7F3EE"/><text x="240" y="164.5" font-size="6.5" fill="#182031" {FONT}>Fri, Nov 7</text>
  <rect x="292" y="154" width="52" height="16" rx="5" fill="#F7F3EE"/><text x="298" y="164.5" font-size="6.5" fill="#182031" {FONT}>2 guests</text>
  <rect x="234" y="176" width="34" height="14" rx="7" fill="#fff" stroke="#E2D8CB"/><text x="251" y="185.4" text-anchor="middle" font-size="6" fill="#182031" {FONT}>18:30</text>
  <rect x="272" y="176" width="34" height="14" rx="7" fill="{c}"/><text x="289" y="185.4" text-anchor="middle" font-size="6" font-weight="700" fill="#fff" {FONT}>19:00</text>
  <rect x="310" y="176" width="34" height="14" rx="7" fill="#fff" stroke="#E2D8CB"/><text x="327" y="185.4" text-anchor="middle" font-size="6" fill="#182031" {FONT}>20:15</text>
  <rect x="234" y="204" width="110" height="20" rx="10" fill="{c}"/><text x="289" y="216.8" text-anchor="middle" font-size="7" font-weight="700" fill="#fff" {FONT}>Book now</text>'''
  return _browser(inner, 'dilettante.com', p['bg'])


ARTS = {'planplate': art_planplate, 'varnote': art_varnote, 'blog': art_blog, 'map': art_map, 'bun': art_bun,
        'piano': art_piano, 'pound': art_pound, 'parrot': art_parrot, 'resto': art_resto}


def art(p):
  return ARTS[p['art']](p)


def url(p):
  return 'https://' + p['domain']


# ------------------------------------------------------------------ cards

def card(p, detailed=False, reveal=''):
  tags = ''.join(f'<span>{esc(t)}</span>' for t in p['tags'])
  built = ''
  if detailed:
    built = ('<ul class="built">' + ''.join(f'<li>{icon("check")}<span>{esc(b)}</span></li>' for b in p['built']) + '</ul>')
  return f'''
  <a class="wk {reveal}" data-cat="{p['cat']}" href="{url(p)}" target="_blank" rel="noopener" aria-label="{esc(p['name'])}: {esc(CAT[p['cat']])}, opens {esc(p['domain'])}">
    <div class="shot" style="background:{p['bg']}">{art(p)}</div>
    <div class="info">
      <div class="cat"><span>{esc(CAT[p['cat']])}</span><span class="live">Live</span></div>
      <h3>{esc(p['name'])}<span class="go">&#8599;</span></h3>
      <p>{esc(p['blurb'])}</p>
      {built}
      <div class="tags">{tags}</div>
      <div class="dom">{esc(p['domain'])}</div>
    </div>
  </a>'''


def filter_bar():
  out = '<div class="lp-filter" role="tablist" aria-label="Filter work by category">'
  for key, label in CATEGORIES:
    n = len(PROJECTS) if key == 'all' else len([p for p in PROJECTS if p['cat'] == key])
    out += f'<button type="button" class="{"on" if key == "all" else ""}" data-act="filter" data-arg="{key}" role="tab">{esc(label)}<span class="n">{n}</span></button>'
  return out + '</div>'


def grid(detailed=False, feature_first=False):
  cls = 'lp-work feature-first' if feature_first else 'lp-work'
  cards = ''.join(card(p, detailed, 'rv d%d' % (i % 3)) for i, p in enumerate(PROJECTS))
  return f'<div class="{cls}">{cards}</div>'


def apply_filter(root_node, key):
  """Show cards of a category (DOM only)."""
  btns = root_node.querySelectorAll('.lp-filter button')
  for i in range(btns.length):
    b = btns.item(i)
    if b.getAttribute('data-arg') == key:
      b.classList.add('on')
    else:
      b.classList.remove('on')
  grid_el = root_node.querySelector('.lp-work')
  if grid_el is not None:
    if key == 'all':
      grid_el.classList.add('feature-first')
    else:
      grid_el.classList.remove('feature-first')
  cards = root_node.querySelectorAll('.wk')
  for i in range(cards.length):
    c = cards.item(i)
    c.classList.add('in')
    if key == 'all' or c.getAttribute('data-cat') == key:
      c.classList.remove('gone')
    else:
      c.classList.add('gone')
