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
- This folder **is** the Anvil repo ("git" layout). README.md is detailed (languages, SEO, code map); keep it current.

**What the user wants:** very professional, trust-building consulting look: ink navy and warm paper, Instrument Serif headlines, Inter text, JetBrains Mono labels; violet = AI draft, green = human-validated. Fonts were enlarged at their request: keep text comfortably big. Browser title "AddAnApp - triple A software delivery service". Claude deploys.

## Workflow

1. `python -I C:\Users\arkvi\Documents\CLAUDE\APP_MAKER\tools\apps_status.py addanapp -v`; pull Anvil's commits; never discard or commit someone else's uncommitted work (on 2026-10-26 there were uncommitted edits to anvil.yaml, Main and content.py from another session: check before touching those files).
2. Edit the files here.
3. `python C:\Users\arkvi\Documents\CLAUDE\APP_MAKER\tools\gitapp_check.py addanapp` → `ALL CHECKS PASSED` (the `t` loop-variable warnings in portfolio.py are known and harmless).
   Server logic: `python ...\APP_MAKER\tools\gitapp_test.py addanapp <script>` (`admin_seed_demo` loads 3 clients + 8 requests under the mock).
4. Commit only your files as arkulinskis with the Co-Authored-By line; `git push origin master`.
5. Schema changes in `anvil.yaml → db_schema` (this file uses the long `admin_ui:` form; match it); the user accepts the Schema Mismatch alert.

## Architecture

```
client_code/Main/        shell (header, language switcher, footer) + #hash router: #home #work #privacy #login #signup #portal #new #r/<id> #account #admin[/tab]
client_code/Landing/ + content.py      marketing page (all copy and markup in content.py)
client_code/Work/ + portfolio.py       full portfolio; projects + hand-drawn SVG mini-UIs (art_* functions) in each product's colours
                                       picks() + showcase(projects) = home case studies; index() = Work page <details> rows; VIDEOS = films; _screen() = 'shot' previews
client_code/Portal, NewRequest, RequestDetail, Account, Privacy, Admin
client_code/i18n.py      t("English text"), tn (plurals), dates/money per language, set_lang; VERSION busts the language packs
client_code/ui.py        HTML helpers, chips, progress bar, formatting, form reading, server-call wrapper    icons.py   dialogs.py (auth, prompts)   state.py
server_code/common.py    ADMIN_EMAILS, SITE_URL, users, ids, statuses, notes, email sending
server_code/serial.py    rows → client-safe dicts (clients never see internal notes or other clients)
server_code/api_client.py  get_me, update_me, poll_counts, my_requests, create_request, get_request, client_action
server_code/api_admin.py   admin_overview, admin_update_request, admin_create_request, admin_delete_request, admin_clients, admin_set_user, admin_leads, admin_update_lead
server_code/api_public.py  submit_lead (project-brief form), sitemap endpoint (/_/api/sitemap.xml)
server_code/email_text.py  FR/RU/LV email texts      i18n_server.py   email language per user (users.lang)      seed.py   demo data
theme/assets/            theme.css, aa.js (scroll reveal, page meta), lang-fr/ru/lv.json, logo.svg, icons, og-image.png (1200×630)
```

**Tables:** `users` (+ name, company, phone, color, role, is_admin, is_demo, email_notifications, last_seen, lang, legal_*), `requests`, `notes`, `leads`.

## Recipes

- **Any visible text:** wrap it in `t("English text")` and add the translation to `theme/assets/lang-fr.json`, `lang-ru.json`, `lang-lv.json` (keyed by the English text). Then bump `VERSION` in `client_code/i18n.py` **and** `?v=` in the head script in anvil.yaml so browsers fetch the new packs. Email wording: `server_code/email_text.py` too.
- **Recent / not-yet-live projects:** `'new': True` shows a "New" badge (none since 2026-11-02: 26 apps arrived at once, so the VR flags were dropped too). Use it for one or two genuinely new projects at a time.
- **Categories:** `CATEGORIES` in portfolio.py (key, label); index groups and filter chips follow that order. `vr` = **VR & mixed reality** (added 2026-11-01 at the user's request): WebXR apps (Snackpuncher, WallTracer, MrBigStage; they live on .anvil.app addresses until they get domains, so update `domain` and the JSON-LD `url` then). VR previews use `_visor(inner, bg, clip_id)`, a headset-visor frame (scene clipped to x 32-368, y 34-214, nose cut-out at the bottom centre; give each art its own clip id) plus `_chip()` for HUD labels. A new VR app → `'cat': 'vr'` and a `_visor` art. A new category needs its label in the three packs and its name in the JSON-LD `keywords`. `'domain': ''` shows "Launching soon" with no link.
- **Removing a project:** delete its PROJECTS entry, its `art_*` function and `ARTS` key (unless another project uses it), its JSON-LD ListItem (renumber `position`), the now-unused keys in the three packs, and its name in the Work page description (Main `set_meta`). CAF Guide was removed this way on 2026-10-31 at the user's request.
- **Portfolio names can differ from the app's own name:** the hotel builder (registry `nouveaustay`) is shown as **ArviStay** at arvistay.com, as the user asked. ToonyLoony is toonyloony.com (loonytoony.com is someone else's parked domain).
- **Previewing art locally:** copy portfolio.py into a scratch package next to stub `ui`/`icons`/`i18n` modules (it uses relative imports), write `art(p)` SVGs into an HTML page at 1200×750 and screenshot it with headless Chrome (`--headless=new --screenshot`); read the PNG before shipping.
- **Home-page case studies (since 2026-11-02, the user's request):** three live projects picked at random per visit (`portfolio.picks()`, using only `random.random()` for Skulpt), Shuffle (`Landing._shuffle`, excludes the ones on screen). There's no `featured` flag any more. The panel's headline is the blurb's **first sentence**, and the index row uses it as the one-line summary, so write every blurb (and its translations) as a short punchy first sentence followed by the detail.
- **New portfolio project:** an entry in portfolio.py (category, domain, blurb, built, tags, color, bg, art) and its film id in `VIDEOS` (from `APP_MAKER/youtube/manifest.json`; skip private ones, check with YouTube oEmbed). Preview: either an `art_<name>()` SVG mini-UI (register in `ARTS`) or `'art': 'shot'` = `theme/assets/pf/<key>.jpg`, the App Board hero shot (`APP_MAKER/board/heroes/<key>.png`) resized to 720x450 JPEG q80. `color`/`bg`: the app's loader `brand=` and `html, body { background }` in its theme.css. Translate blurb, built and new tags in the three packs (append lines at the end of each pack: they mix list layouts, so don't re-dump them), bump i18n VERSION + `?v=`, then `python -I .claude/skills/addanapp/scripts/jsonld.py` rewrites the head JSON-LD ItemList (+ film `subjectOf`). Update "53" nowhere by hand: counts come from `len(PROJECTS)`. The user's apps and their live URLs are in `APP_MAKER/apps.json`; CAF Guide stays out (user's request).
- **Video structured data (Search Console, 2026-11-04):** every head `VideoObject` needs `description`, `embedUrl` and an `uploadDate` with time + timezone (`2026-11-02T15:21:46+00:00`, not a bare date). `jsonld.py` builds them from `scripts/video_meta.json` (YouTube publishedAt, duration, first description line). After a new upload, refresh it from `APP_MAKER/youtube` with `yt.channel_videos(yt.yt())` (same fields, keyed by video id, UTF-8), then rerun `jsonld.py`. Non-public films are left out.
- **Free guides (`#guides`, 2026-11-03):** list in `GUIDES` (content.py) and `GUIDES` (api_public.py), keep both in step; PDFs + covers in `theme/assets/guides/`, sources in `Documents/CLAUDE/addanapp-guides` (`python src/build.py`). Guide leads use `source` guide / guide+news, no extra columns (so no schema change); quiet ones (not a buying-signal situation) don't count in the Leads badge (`is_quiet_guide_lead`). New guide = PDF + cover + both lists + title/hook/bullets in the three packs. Server tests: scratch script for `gitapp_test.py` covering bad email, honeypot, repeat request (one row, one email a day), hot alert, CSV.
- **YouTube embed:** `YT_FILMS` in content.py, one Addanapp film per language (ids in `APP_MAKER/youtube/manifest.json`: addanapp, addanapp-fr/ru/lv; covers `theme/assets/yt-addanapp[-fr|-ru|-lv].jpg` from each `Documents/CLAUDE/addanapp-video[-xx]/youtube-thumbnail.jpg` at 960x540). The visitor's language plays; the others are linked under it. `Landing._play` swaps in a youtube-nocookie iframe only on click. A second card under it (`YT_REBUILD`, 2026-11-03) plays Parapeet's before/after film (FW-j_xL_DWo, English only) in the same frame, to show rebuild work ("Not only new apps"); `_play(vid)` picks the film from the card's `data-arg`. The FAQ "Can you take over an existing app?" links the same film (`FAQ_EXTRA` in content.py: an optional third item on a FAQ entry adds a paragraph; mirror it in the FAQPage JSON-LD in anvil.yaml). Privacy lists it via the legal kit's `youtube_play` provider. Any other third-party embed needs the same click-to-load pattern + a legal-kit provider.
- **Partner deck PDFs (EN/FR/RU/LV):** from the Slides artifact https://claude.ai/artifact/X7izxcayZdhgbzmsdrN9Ua. Read its project/ files into a scratch folder, then `python .claude/skills/addanapp/scripts/deck_pdf.py <folder> --lang all` (steps in its docstring): it translates every text fragment from `scripts/deck_i18n/<fr|ru|lv>.json` (keyed by the English fragment; new English text is listed as MISSING), uses PT Serif for Russian headlines, renders `deck-<lang>.pdf` + `cover-<lang>.jpg`, and runs a layout check that fails on text running into a slide's footer (fix by shortening the translation or a `FIT` rule). Copy them to `theme/assets/addanapp-partner-deck[-fr|-ru|-lv].pdf` and `partner-deck-cover[-fr|-ru|-lv].jpg`; sizes in `DECKS` (content.py). Translations are Claude's: a native speaker's read is worth it before big sends. The "fit" slide lists kinds of firm with Vooban, Mirego, Moov AI, Deloitte and Avanade only as examples ("No partnership or affiliation"): the user is NOT partnering with them, so never word it as a partnership. Deck facts to keep current: product count (portfolio), library count (APP_MAKER/libraries/data.json), films (APP_MAKER/youtube/manifest.json); check the App Board (`board_cli.py status/queue`) before claiming an app has real customers. Cover image = page 1 at 960x540.
- **Header "chapters" (the user's rule for keeping the long page clean, 2026-11-02):** six header links, no more (French/Russian/Latvian already need tighter spacing to fit 1200px; `@media (min-width: 1241px)` block in theme.css). Every home section has `data-ch="<header link key>"` (or `""`), which drives the scroll highlight (`aa.spy`). A section without its own link goes in its chapter's menu (`_group(...)` items in Main's SHELL), never a new top-level link. `CHAPTER` in Main maps `#home/<section>` routes to their link.
- **SEO:** title/meta/OG/JSON-LD live in `anvil.yaml → native_deps.head_html` and `metadata`; each route sets its own `<title>`; private pages are `noindex`.

## Gotchas

- **Continue with Google** (client_code/dialogs.py `_AuthBox.google` (strings in lang-*.json)): `login_with_google()` returns None for someone without an account, so the code then calls `signup_with_google()`; on the sign-up view it needs the Privacy & Terms tick first. Needs `use_google` + the Google service in anvil.yaml.
- Portfolio previews: SVG on a 400×250 canvas; `_phone()` content goes past the bottom edge, so keep phone UI above y≈248, and a coloured phone screen needs `rx="17"` from y=22 (redraw the notch). Check new art large before shipping: text easily spills out of shapes.
- **Arkvital** (arkvital.com, Websites) is the user's personal site. Never say on Addanapp that the same person runs both: describe it neutrally as a client-style project.
- Russian `New` is "Новые" because the admin lead filter uses the same string; the portfolio badge shares it.
- **Never use `t` (or any imported name) as a comprehension variable.** The browser's Python leaks it into the function: `[t[0] for t in TABS]` in Admin.__init__ turned `t()` into a tuple and the consultant console crashed right after the admin signed in ("'tuple' object is not callable", fixed 2026-11-02). gitapp_check now fails on it. Plain `for t in tags:` loops in portfolio.py are fine as long as that function doesn't call `t()`.

- Russian and Latvian visitors see the Privacy & Terms page in English (the legal kit has EN/FR only).
- Placeholder business facts to confirm with the user before relying on them: hello@addanapp.com, 2-day quotes, 1–3 week features, 24-month lead retention.
- `python -I` hides PyYAML: run gitapp_check/gitapp_test without `-I`.
- The header's frosted glass lives on `.aa-header::before`, not on `.aa-header`: a `backdrop-filter` (or filter/transform) on the header traps the full-screen burger menu (`position: fixed`) inside the 60px bar. Fixed 2026-10-26.

## Privacy & Terms (legal kit)

From `C:/Users/arkvi/Documents/CLAUDE/APP_MAKER/legal-kit`. Don't edit `theme/assets/legal-kit.js`, `client_code/legal.py` or `server_code/legal_server.py` here: change `apps/addanapp.json` there, run `python -I build.py addanapp && python -I install.py addanapp`, then commit and push here.
- Sign-up keeps the consent tick box (dialogs.auth); `legal.refresh_soon()` after sign-in, `legal.signed_out()` after sign-out.
