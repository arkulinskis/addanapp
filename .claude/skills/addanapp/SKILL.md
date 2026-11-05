---
name: addanapp
description: Context, workflow and recipes for Addanapp (addanapp.com), the user's Anvil site for their Montréal software consultancy: a marketing landing page with portfolio, a client workspace for feature requests, and a consultant console; English, French, Russian and Latvian. Load this before any content change, portfolio update, translation, feature request, bug fix or deploy for Addanapp.
---

# Addanapp: working on the app

**What it is:** the website and client platform of the user's consultancy ("Apps built at AI speed. Signed off by senior engineers.").
- **Landing page** (`#home`): hero with a live request mock, hours vs outcomes, the 5-step AI + human method, capabilities, a **portfolio**: 3 projects picked at random on every visit + Shuffle + "See all 53 products in depth" (→ `#work`, the full index grouped by category with filters; the user's own apps), the **YouTube** section (`#youtube`: channel youtube.com/@addanapp + click-to-play Addanapp film), client workspace preview, engagement models, the **partner deck** download (`#partners`), commitments, a bilingual Montréal section, FAQ, project-brief form (→ leads).
- **Client workspace** (`#portal`, `#new`, `#r/<id>`, `#account`): clients submit requests (feature, fix, integration, new app…), approve fixed quotes, follow progress notes, accept deliveries or request changes.
- **Consultant console** (`#admin`): every request as a list or Kanban board; progress notes (update, milestone, human-validated, question, internal), status, progress %, quote, scope, ETA; clients; leads; demo data.
- Lifecycle: Submitted → Scoping → Quote ready → In progress → Ready for review → Delivered (+ On hold, Closed). Internal notes never reach clients; client-visible notes and status changes are emailed.

**Where it lives:**
- App repo **github.com/arkulinskis/addanapp**, branch `master`; Anvil pulls master. Live: https://addanapp.com (domain assumed in `SITE_URL`, server_code/common.py, and the head tags).
- Folder `C:\Users\arkvi\Documents\CLAUDE\addanapp-forms` **is** the Anvil repo ("git" layout). Since 2026-11-05 the app is
  **native Anvil Forms** (Python Forms + HTML templates, the `Layouts/Shell` layout, custom components, RepeatingPanels),
  made from `APP_MAKER/template-forms`'s patterns; converted on branch `forms`. The old folder `addanapp` (the HTML-string
  version) is retired once `forms` is merged: never deploy from it. README.md is detailed (languages, SEO, code map); keep it current.

**What the user wants:** very professional, trust-building consulting look: ink navy and warm paper, Instrument Serif headlines, Inter text, JetBrains Mono labels; violet = AI draft, green = human-validated. Fonts were enlarged at their request: keep text comfortably big. Browser title "AddAnApp - triple A software delivery service". Claude deploys.

## Workflow

1. `python -I C:\Users\arkvi\Documents\CLAUDE\APP_MAKER\tools\apps_status.py addanapp -v`; `git pull --ff-only` (read Anvil's "Edited ..." commits); never discard or commit someone else's uncommitted work.
2. Edit: a page's template and Python side by side (`client_code/Pages/X/form_template.html` + `__init__.py`).
3. `python tools/check.py` (no -I) → **ALL CHECKS PASSED**: Anvil's validator (every template + Python file type-checked),
   JS syntax, asset hashes, server tests (`tools/testing/test_server.py`, strict mock; add a test for every server change).
4. `python -I tools/ui_test.py` (Docker Desktop running) → **ALL UI TESTS PASSED**: flow.js (journeys), phone.js (390 px),
   admin.js (console), a11y.js (axe WCAG 2.2 AA), i18n.js (fr, ru, lv). `--only x.js` runs one; `--restart` after server
   or anvil.yaml edits; `--shots DIR` = screenshots of every page (desktop + phone): read them. Extend the scripts with new behaviour.
5. Commit only your files as arkulinskis with the Co-Authored-By line; `git push origin master`.
6. Schema changes in `anvil.yaml → db_schema` (this file uses the long `admin_ui:` form; match it); the user accepts the Schema Mismatch alert.

## Architecture

```
anvil.yaml               startup: module `startup`; runtime_options version 3 + server python314 (HTML forms need it);
                         head_html: Prepsto widget, the language-pack script (sets window.AA_PACK), legal-kit.js, fonts,
                         icons.css, app.css, app-kit.js, aa.js (all ?v=<hash>: tools/assets.py), favicons, SEO + JSON-LD
client_code/
  startup.py             language pack -> legal.setup(lang) -> state.refresh_me() -> router.start()
  router.py              #home[/section] #work #guides[/slug] #privacy #login #signup #portal #new #r/<id> #account
                         #admin[/requests|clients|leads|tools]; the sign-in box opens over the landing page (Dialogs/AuthBox);
                         page titles/meta (ui.set_meta); CHAPTER maps home sections to their header link
  Layouts/Shell          header (six chapter links + two menus, language switch, account menu, burger; workspace menu
                         = RepeatingPanel of Items/AppNavLink), footer, a Timer polling unread counts every 60 s. Anvil keeps
                         one Shell between pages: refresh(nav, public) after every page
  Pages/Landing          the whole marketing page: copy in the template (data-t), proof marquee, 3 random case studies
                         (Items/ShowcaseCard, Shuffle), films (aa.playFilm), workspace tabs, deck links, project brief
  Pages/Work             full index: Items/WorkGroup -> Items/WorkRow (<details>; Items/WorkDetail made on first open)
  Pages/Guides           free guides: email form -> request_guides -> Items/GuideLink + Items/GuideCard
  Pages/Portal, NewRequest, RequestDetail, Account     the client workspace (RequestDetail also = consultant view + Manage)
  Pages/Admin            the console: requests (Items/Tile, Pill, RequestRow, BoardColumn/BoardCard), clients
                         (Items/PersonCard), leads (Items/LeadCard), tools
  Components/            Avatar, Progress, Seg (+ Items/SegOption), RequestForm (collect/validate), Shot (project preview)
  Dialogs/               AuthBox, PromptText, NewForClient
  i18n.py                t() (HTML) / tp() (plain) / tn() plurals / apply(form, **vars) for templates / dates + money / VERSION
  content.py             films (YT_FILMS, YT_REBUILD), decks (DECKS, deck()), GUIDES, lead-form choices: data only
  portfolio.py           PROJECTS, CATEGORIES, VIDEOS, the SVG preview engine (art_*), shot_html(), picks()
  ui.py                  STATUS/KINDS/... (mirror the server), chips (Label roles), formatting, ui.call (FAIL on error)
  state.py               me, counts, toast, set_attr / set_control_attr / heading / refocus_later, date_box
server_code/             unchanged by the conversion: common.py, serial.py, api_client.py, api_admin.py, api_public.py,
                         email_text.py, i18n_server.py, seed.py, seo_routes.py (SEO kit), legal_server.py (legal kit)
theme/assets/            app.css (design system + "Native Anvil Forms layer" at the end), theme.css (spinner only),
                         icons.css (generated), app-kit.js (UI.ICONS, UI.tr translator, a11y glue), aa.js, lang-*.json
tools/                   check.py, ui_test.py + ui/*.js, i18n_check.py, assets.py, build_icons.py, testing/
```

**Tables:** `users` (+ name, company, phone, color, role, is_admin, is_demo, email_notifications, last_seen, lang, legal_*), `requests`, `notes`, `leads`.

## How things are done here (native Forms)

- **Static copy** is plain HTML in the template, in English, with `data-t` on the element whose inner HTML is the text
  (the pack key, whitespace collapsed). When a text sits next to an icon or other markup, wrap just the text:
  `<span><i class="ic ic-check"></i><x-t data-t>Fixed quote before work starts</x-t></span>` (`x-t` is an inline,
  style-free wrapper). Values: `data-tv="n:products"` + `i18n.apply(self, products=53)`. Attributes: `data-ta="aria-label"`.
  Every form calls `i18n.apply(self)` at the end of `__init__` (it also translates its Buttons/Labels/placeholders).
- **Changing text** = a Label with role `t` inside the old markup (`<b class="ttl"><Label role t></b>`: the Label's own box
  disappears, so the old CSS applies), or for display-only text in items `anvil:dom-node` + `.textContent`.
- **Actions** = Anvil Buttons with roles `aa-btn` + `accent` / `green` / `ghost` / `light` / `ghost-light` / `danger` / `sm` /
  `lg` / `block` (+ `ic-<name>` for an icon), or `aa-link`; navigation = plain `<a href="#...">`.
- **Lists** = RepeatingPanel (role `contents`) + an `Items/` Form; items talk to the page with
  `self.parent.raise_event("x-pick", key=...)`. A list of ticks is `role="list"` / `role="listitem"` divs (an `<li>` inside
  Anvil's panel wrapper breaks list semantics). Selectors like `:first-child` don't see across items: pass a `first` flag.
- **Chips** = Labels: `ui.chip(label, text, 'ai')`, `ui.status_chip(label, status)`, `ui.priority_chip(...)`.
- **Inputs** = TextBox/TextArea/DropDown inside `<label class="f"><span class="lbl">...</span>...</label>`; dates =
  TextBox + `state.date_box()`; tick boxes with linked text stay plain `<input type=checkbox anvil:dom-node>`.
- **Server calls** = `ui.call(fn, ...)`: the server raises `Exception("message")` for normal problems; the message is
  shown translated (`i18n.server_text`) and `ui.FAIL` comes back. A page that shows its own empty state calls
  `anvil.server.call` in a try (RequestDetail).
- **Anvil's classes are prefixed on runtime v3** (`anvil-form-control`, `anvil-btn`, `anvil-label-text`; the App Server 1.18
  used `form-control`, `label-text`): app.css covers both with `:is(...)`.

## Recipes

- **Any visible text:** in a template, write the English and mark it `data-t` (see "How things are done here"); in Python,
  `tp("English text")` (or `t()` when it holds HTML). Add the translation to `theme/assets/lang-fr.json`, `lang-ru.json`,
  `lang-lv.json` (keyed by the English text, exactly as written; append at the end of each pack). Then bump `VERSION` in
  `client_code/i18n.py` **and** `?v=` in the head script in anvil.yaml so browsers fetch the new packs.
  `python -I tools/i18n_check.py` lists template texts without a translation; ui_test's i18n.js checks it in the browser.
  Email wording: `server_code/email_text.py` too.
- **Recent / not-yet-live projects:** `'new': True` shows a "New" badge (none since 2026-11-02: 26 apps arrived at once, so the VR flags were dropped too). Use it for one or two genuinely new projects at a time.
- **Categories:** `CATEGORIES` in portfolio.py (key, label); index groups and filter chips follow that order. `vr` = **VR & mixed reality** (added 2026-11-01 at the user's request): WebXR apps (Snackpuncher, WallTracer, MrBigStage; they live on .anvil.app addresses until they get domains, so update `domain` and the JSON-LD `url` then). VR previews use `_visor(inner, bg, clip_id)`, a headset-visor frame (scene clipped to x 32-368, y 34-214, nose cut-out at the bottom centre; give each art its own clip id) plus `_chip()` for HUD labels. A new VR app → `'cat': 'vr'` and a `_visor` art. A new category needs its label in the three packs and its name in the JSON-LD `keywords`. `'domain': ''` shows "Launching soon" with no link.
- **Removing a project:** delete its PROJECTS entry, its `art_*` function and `ARTS` key (unless another project uses it), its JSON-LD ListItem (renumber `position`), the now-unused keys in the three packs, and its name in the Work page description (router.py `set_meta`). CAF Guide was removed this way on 2026-10-31 at the user's request.
- **Portfolio names can differ from the app's own name:** the hotel builder (registry `nouveaustay`) is shown as **ArviStay** at arvistay.com, as the user asked. ToonyLoony is toonyloony.com (loonytoony.com is someone else's parked domain).
- **Previewing art locally:** copy portfolio.py into a scratch package next to a stub `i18n` module (`tp = lambda s, **k: s`), write `art(p)` SVGs into an HTML page at 1200×750 and screenshot it with headless Chrome (`--headless=new --screenshot`); read the PNG before shipping. Or simply `ui_test.py --shots` and look at the Work page.
- **Home-page case studies (since 2026-11-02, the user's request):** three live projects picked at random per visit (`portfolio.picks()`, using only `random.random()` for Skulpt), Shuffle (`Landing.shuffle_button_click`, excludes the ones on screen). There's no `featured` flag any more. The panel's headline is the blurb's **first sentence**, and the index row uses it as the one-line summary, so write every blurb (and its translations) as a short punchy first sentence followed by the detail.
- **New portfolio project:** an entry in portfolio.py (category, domain, blurb, built, tags, color, bg, art) and its film id in `VIDEOS` (from `APP_MAKER/youtube/manifest.json`; skip private ones, check with YouTube oEmbed). Preview: either an `art_<name>()` SVG mini-UI (register in `ARTS`) or `'art': 'shot'` = `theme/assets/pf/<key>.jpg`, the App Board hero shot (`APP_MAKER/board/heroes/<key>.png`) resized to 720x450 JPEG q80. `color`/`bg`: the app's loader `brand=` and `html, body { background }` in its theme.css. Translate blurb, built and new tags in the three packs (append lines at the end of each pack: they mix list layouts, so don't re-dump them), bump i18n VERSION + `?v=`, then `python -I .claude/skills/addanapp/scripts/jsonld.py` rewrites the head JSON-LD ItemList (+ film `subjectOf`). Update "53" nowhere by hand: counts come from `len(PROJECTS)`. The user's apps and their live URLs are in `APP_MAKER/apps.json`; CAF Guide stays out (user's request).
- **Video structured data (Search Console, 2026-11-04):** every head `VideoObject` needs `description`, `embedUrl` and an `uploadDate` with time + timezone (`2026-11-02T15:21:46+00:00`, not a bare date). `jsonld.py` builds them from `scripts/video_meta.json` (YouTube publishedAt, duration, first description line). After a new upload, refresh it from `APP_MAKER/youtube` with `yt.channel_videos(yt.yt())` (same fields, keyed by video id, UTF-8), then rerun `jsonld.py`. Non-public films are left out.
- **Free guides (`#guides`, 2026-11-03):** list in `GUIDES` (content.py) and `GUIDES` (api_public.py), keep both in step; PDFs + covers in `theme/assets/guides/`, sources in `Documents/CLAUDE/addanapp-guides` (`python src/build.py`). Guide leads use `source` guide / guide+news, no extra columns (so no schema change); quiet ones (not a buying-signal situation) don't count in the Leads badge (`is_quiet_guide_lead`). New guide = PDF + cover + both lists + the fan of covers in Pages/Landing + title/hook/bullets in the three packs. Server tests in tools/testing/test_server.py (bad email, honeypot, repeat request = one row, one email a day, CSV).
- **YouTube embed:** `YT_FILMS` in content.py, one Addanapp film per language (ids in `APP_MAKER/youtube/manifest.json`: addanapp, addanapp-fr/ru/lv; covers `theme/assets/yt-addanapp[-fr|-ru|-lv].jpg` from each `Documents/CLAUDE/addanapp-video[-xx]/youtube-thumbnail.jpg` at 960x540). The visitor's language plays; the others are linked under it. `Landing.play_click` (via `aa.playFilm`) swaps in a youtube-nocookie iframe only on click. A second card under it (`YT_REBUILD`, 2026-11-03) plays Parapeet's before/after film (FW-j_xL_DWo, English only) in the same frame, to show rebuild work ("Not only new apps"); `Landing.rebuild_click` plays it. The FAQ "Can you take over an existing app?" links the same film (a second `<p data-t data-tv="link:faq_link">` in that FAQ entry in Pages/Landing; mirror FAQ text in the FAQPage JSON-LD in anvil.yaml). Privacy lists it via the legal kit's `youtube_play` provider. Any other third-party embed needs the same click-to-load pattern + a legal-kit provider.
- **Partner deck PDFs (EN/FR/RU/LV):** from the Slides artifact https://claude.ai/artifact/X7izxcayZdhgbzmsdrN9Ua. Read its project/ files into a scratch folder, then `python .claude/skills/addanapp/scripts/deck_pdf.py <folder> --lang all` (steps in its docstring): it translates every text fragment from `scripts/deck_i18n/<fr|ru|lv>.json` (keyed by the English fragment; new English text is listed as MISSING), uses PT Serif for Russian headlines, renders `deck-<lang>.pdf` + `cover-<lang>.jpg`, and runs a layout check that fails on text running into a slide's footer (fix by shortening the translation or a `FIT` rule). Copy them to `theme/assets/addanapp-partner-deck[-fr|-ru|-lv].pdf` and `partner-deck-cover[-fr|-ru|-lv].jpg`; sizes in `DECKS` (content.py). Translations are Claude's: a native speaker's read is worth it before big sends. The "fit" slide lists kinds of firm with Vooban, Mirego, Moov AI, Deloitte and Avanade only as examples ("No partnership or affiliation"): the user is NOT partnering with them, so never word it as a partnership. Deck facts to keep current: product count (portfolio), library count (APP_MAKER/libraries/data.json), films (APP_MAKER/youtube/manifest.json); check the App Board (`board_cli.py status/queue`) before claiming an app has real customers. Cover image = page 1 at 960x540.
- **Header "chapters" (the user's rule for keeping the long page clean, 2026-11-02):** six header links, no more (French/Russian/Latvian already need tighter spacing to fit 1200px; `@media (min-width: 1241px)` block in theme.css). Every home section has `data-ch="<header link key>"` (or `""`), which drives the scroll highlight (`aa.spy`). A section without its own link goes in its chapter's menu (the `aa-nav-grp` blocks in `Layouts/Shell`), never a new top-level link. `CHAPTER` in router.py maps `#home/<section>` routes to their link.
- **SEO:** title/meta/OG/JSON-LD live in `anvil.yaml → native_deps.head_html` and `metadata`; each route sets its own `<title>`; private pages are `noindex`.

## Gotchas

- **Continue with Google** (`Dialogs/AuthBox.google_button_click`; strings in lang-*.json): `login_with_google()` returns None for someone without an account, so the code then calls `signup_with_google()`; on the sign-up view it needs the Privacy & Terms tick first. Needs `use_google` + the Google service in anvil.yaml.
- Portfolio previews: SVG on a 400×250 canvas; `_phone()` content goes past the bottom edge, so keep phone UI above y≈248, and a coloured phone screen needs `rx="17"` from y=22 (redraw the notch). Check new art large before shipping: text easily spills out of shapes.
- **Arkvital** (arkvital.com, Websites) is the user's personal site. Never say on Addanapp that the same person runs both: describe it neutrally as a client-style project.
- Russian `New` is "Новые" because the admin lead filter uses the same string; the portfolio badge shares it.
- **Never use `t` (or any imported name) as a comprehension variable.** The browser's Python leaks it into the function: `[t[0] for t in TABS]` in Admin.__init__ turned `t()` into a tuple and the consultant console crashed right after the admin signed in ("'tuple' object is not callable", fixed 2026-11-02).
- **Templated Forms aren't containers**: no `get_components()`; i18n.apply finds a form's components through its attributes.
- The browser's Python has no `vars()` (NotImplementedError).
- `prop:` text with `&amp;` reaches Python as `&`: `tp()` looks the key up both ways.
- Accessibility (2026-11-05, a11y.js green): `--faint` darkened to #646C7B (4.6:1 on every surface), in-sentence links
  underlined, the header menu arrows 24 px wide, progress bars named, lists as role=list/listitem.

- Russian and Latvian visitors see the Privacy & Terms page in English (the legal kit has EN/FR only).
- Placeholder business facts to confirm with the user before relying on them: hello@addanapp.com, 2-day quotes, 1–3 week features, 24-month lead retention.
- `python -I` hides PyYAML: run tools/check.py without `-I` (ui_test.py with `-I`).
- The header's frosted glass lives on `.aa-header::before`, not on `.aa-header`: a `backdrop-filter` (or filter/transform) on the header traps the full-screen burger menu (`position: fixed`) inside the 60px bar. Fixed 2026-10-26.

## Privacy & Terms (legal kit)

From `C:/Users/arkvi/Documents/CLAUDE/APP_MAKER/legal-kit`. Don't edit `theme/assets/legal-kit.js`, `client_code/legal.py` or `server_code/legal_server.py` here: change `apps/addanapp.json` there, run `python -I build.py addanapp && python -I install.py addanapp`, then `python tools/assets.py`, commit and push here.
- Sign-up keeps the consent tick box (Dialogs/AuthBox puts `legal.consent_field()` in its `consent` dom-node); `legal.refresh_soon()` after sign-in (state.refresh_me), `legal.signed_out()` after sign-out (Shell).
