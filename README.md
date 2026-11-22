# Addanapp

**Apps built at AI speed. Signed off by senior engineers.**

Addanapp is the website and client platform for a Montréal software consultancy. It has three parts:

| Area | What it does |
| --- | --- |
| **Landing page** (`#home`) | The marketing site: hero with a live request mock, "hours vs outcomes" comparison, the 5-step AI + human method, capabilities, portfolio (three projects picked at random, a Shuffle button and a link to the full index), the YouTube channel with the Addanapp film, client workspace preview, engagement models, a partner-deck download for agencies, commitments, a bilingual Montréal section, FAQ and a project-brief form. |
| **Client workspace** (`#portal`) | Clients sign up and submit requests (feature, fix, integration, new app…), approve fixed quotes, follow progress notes, accept deliveries or request changes. |
| **Consultant console** (`#admin`) | Every request across clients as a list or Kanban board. Post progress notes (update, milestone, human-validated, question, internal), set status, progress %, fixed quote, scope summary and ETA. Also manage clients, website leads and demo data. |
| **Apps** (`#apps`, `#app/<key>`) | A client's app portfolio board (the user's App Board, moved here from their PC on 2026-11-11; the apps are spread over six made-up test clients by category). Views: Board (a lane per stage), Checklist grid, Posts, Biz dev, Money, YouTube, Dossiers, Notifications; one page per app with its checklist, "Changes for Claude" (they become requests), a Prepsto idea box, notes and links. Only that client and consultants see it. |

Other routes: `#work` (full portfolio: a spotlight of three projects side by side with Refresh and Next, then every project, with what we built, its film and its link), `#guides[/<slug>]` (the free PDF guides, unlocked with an email), `#estimate[/<code>]` (the 60-second ballpark estimator), `#signoff/sample` (a public sample sign-off record), `#r/<id>` (one request), `#new`, `#account`, `#privacy`, `#login`, `#signup`.

## Trust features (2026-11-20)

- **Ballpark estimator** (`#estimate`, Engagements menu, a button under the engagements, a line on `/pricing` + `/fr/tarifs`):
  seven one-tap questions (`client_code/estimate.py`, pure Python shared with the server) map to the published milestone
  prices only (Launch $30,000 / Operate $75,000 / Scale $150,000 / Complete $300,000; a change = per-request quote, sample
  $2,400 in 6 days; a takeover = audit first). The result updates live (milestone, price, path, why, what's included,
  "ballpark, not a quote"); the address follows the answers (`#estimate/a0110000`), so **Copy link** reopens it in any
  language. **Send as a brief** = a lead with source `estimate`; the server recomputes the estimate from the code and
  writes "Estimator: Operate (~$75,000). Answers: ..." into the message (LeadCard shows an "Estimator" chip).
- **Sign-off record** (`server_code/signoff.py`, table `signoffs`, `client_code/signoff_data.py`): before a client request
  can move to Ready for review, the consultant signs it off (Dialogs/SignOff: the 10 checks from guide 03, each
  acceptance criterion, tests passing, a note). A complete record posts a "Signed off by ..." note and emails the client;
  the client sees the green record (Components/SignoffCard, with Print). **Accept delivery** opens Dialogs/AcceptDelivery:
  a tick per criterion; anything unticked turns it into "Request changes" with those criteria written in. A changed
  delivery must be signed off again. App Board requests (portfolio clients) skip all of this. Public sample:
  `#signoff/sample` (linked from the hero's "100% human-reviewed" stamp, method step 04 and guide 03's card).
- **Locked quotes + change orders** (`server_code/quotes.py`, table `change_orders`): once the client approves a quote
  (the approval note records amount and ETA), the amount can't be edited. The consultant sends a change order
  (Dialogs/ChangeOrder: new total, new ETA, reason); the client gets an amber banner with **Keep the original scope /
  Approve change**; declining (or the consultant withdrawing it) leaves price and ETA untouched. Details shows the approved
  quote, every change order and the total; the Portal has a "No surprises" strip (approved & in progress, accepted,
  waiting for your OK, hours billed 0). Every step is a timeline line with before and after.
- New tables are read through guards: until the Schema Mismatch is accepted, the app works as before (no sign-off guard,
  no change orders).

## Apps: the portfolio board (since 2026-11-11)

The App Board that ran on the user's PC (`APP_MAKER/board`) now lives here. The apps are split over six made-up client
companies by category, for realistic testing (`APP_MAKER/board/clients.json`): Northgate Commerce Group (business
platforms), Brightloom Studio (creator tools), Pixel Harbor Games (games + mobile), Halo Reality Labs (VR), Cedarpoint
Learning, Meridian Digital (websites; the default for new apps). Their accounts are `arkulinskis+<id>@gmail.com`, made by
the first push with no password ("Forgot your password?" sets one). A client with a portfolio gets an **Apps** link in
the workspace menu and sees only its own apps, plans and videos; consultants see every portfolio with a client picker.

- **Who writes what.** Nothing runs on a timer (the PC worker and its job queue were removed on 2026-11-16).
  **Refresh** (all apps, or one app's button) checks from here, `server_code/apps_refresh.py`: GitHub (commits,
  branches to merge, anvil.yaml tables), live site + SEO and the `<name>.anvil.app` guess, the live database vs the code,
  and mentions on arkvital.com / addanapp.com. The browser sends `apps_refresh` 3 apps per call with a progress line; each
  call stops after 24 s (Anvil's limit is 30 s). Those facts go into the card with `card.server.at`; a PC push with older
  facts keeps them (`keep_server_facts`). Links typed on the board, Prepsto ideas/tickets and YouTube **Update numbers**
  (public counts) are server calls too. The PC's **one-shot update** (`APP_MAKER/board/addanapp_link.py sync`, or
  "Update Addanapp.bat") sends what only the PC has: the standard audit, legal status, screenshots, posts, video kits,
  biz dev + money plans, YouTube Analytics, new apps. People here tick steps, write notes, park apps, tick Posted,
  dismiss notifications, add outreach rows and ask for changes. Changes are ordinary **requests** (kind `change`,
  project = the app key) that start In progress; Claude marks them Ready for review (`board_cli.py done`), the client accepts them.
- **App Secrets for Refresh**: `github_token` (fine-grained, read-only: Contents, Metadata, Pull requests), `prepsto_key`
  (Claude's Prepsto API key), `youtube_api_key` (Google API key, YouTube Data API v3 only). A missing one gives a message
  naming it. Links typed on the board live in `state.links` until the PC's `pull` writes them into apps.json.
- **The PC API**: `/_/api/apps/v1/<action>` (`server_code/apps_sync.py`) with `Authorization: Bearer <key>`. Only the
  key's SHA-256 is in the code (`KEY_HASHES`); the key is in `~/.addanapp/apps-link.json` on the PC. The local App
  Server also accepts the test key `aal_local_test_key` (tests only; never on addanapp.com).
- **Tables**: `app_projects` (card = facts, state = clicks, screenshots, posts, video kit), `app_docs` (steps, plans,
  outreach log, YouTube numbers, dismissed notifications), `app_jobs` (unused since 2026-11-16, kept for its old rows).
- **Code**: `server_code/apps_core.py` (stages, tags, notifications, markdown), `api_apps.py` (browser), `apps_refresh.py`
  (Refresh, links, Prepsto, YouTube from here), `apps_sync.py` (PC); `client_code/apps_data.py` (shared state), `Pages/Apps` (the views' frame), `Pages/AppDetail`,
  `Components/Ap*` (views and shared blocks), `Items/Ap*`; `theme/assets/apps.css` and `apps.js` (draws the grid,
  step strips, charts and tables with textContent only). The Apps area is in English only.

## Request lifecycle

`Submitted → Scoping → Quote ready → In progress → Ready for review → Delivered` (plus `On hold` and `Closed`).

- The consultant sets the fixed quote and ETA, then moves the request to **Quote ready**. The client clicks **Approve quote** and it moves to In progress.
- After approval the quote is **locked**: a price or ETA change is a change order the client approves first.
- The consultant **signs off** the delivery (10 checks + each acceptance criterion), then marks it **Ready for review**. The client ticks each criterion and clicks **Accept delivery** (it becomes Delivered and can be invoiced) or **Request changes** (it goes back to In progress with their comment and the criteria that didn't pass).
- Internal notes are never sent to clients. Client-visible notes and status changes are emailed to the client, and client actions are emailed to consultants.

## Getting it running in Anvil

1. In the Anvil editor, pull `master` from GitHub (or clone the repo as a new app).
2. Accept the **data table schema** from `anvil.yaml` (4 tables: `users`, `requests`, `notes`, `leads`). The `users.lang` column stores each person's language for emails.
3. Run the app and create a workspace with **your admin email** (App Secret `admin_emails`). Emails listed in `ADMIN_EMAILS` (`server_code/common.py`) become consultants automatically. Other consultants can be promoted from **Console → Clients**.
4. Optional: **Console → Tools → Load demo data** adds 3 fictional clients and 8 requests at every stage. Demo clients can't sign in and never get email.

Services used: Data Tables, Users (email + password, sign-up on, no email confirmation, Continue with Google), Google, Email.

The app is built as **native Anvil Forms** (since 2026-11-05): Python Forms with HTML templates, one layout (`Layouts/Shell`),
custom components and RepeatingPanels; JavaScript only for small page effects. Runtime: `anvil.yaml → runtime_options`
version 3 with the Python 3.14 server (the form format needs it).

## Checking a change

- `python tools/check.py` → **ALL CHECKS PASSED**: Anvil's validator (`anvil validate`: every template and Python file
  type-checked), JavaScript syntax, asset hashes (`tools/assets.py`), server tests (`tools/testing/test_server.py`, a strict
  Anvil mock: public forms, workspace, console, who may do what).
- `python -I tools/ui_test.py` → **ALL UI TESTS PASSED** (Docker Desktop running): the app in the open-source Anvil App
  Server, driven by headless Chrome: the journeys (`tools/ui/flow.js`), every page at 390 px (`phone.js`), the consultant
  console (`admin.js`), accessibility (`a11y.js`: axe-core WCAG 2.2 AA + keyboard checks) and the translations (`i18n.js`,
  in French, Russian and Latvian). `--shots DIR` saves screenshots of every page, desktop and phone.
- `python -I tools/i18n_check.py` lists template texts that have no translation (offline).

## Languages

The whole site and app are available in **English, French, Russian and Latvian**. Pick one from the globe button in the header (or the footer, or **Account → Language**).

- English is built into the code and loads with no extra download. Text in a form template is written in English and
  marked `data-t` (`<h2 data-t>Most consultancies sell hours. <em>We sell outcomes.</em></h2>`); `i18n.apply(self)` at the end
  of the form's `__init__` swaps it for the visitor's language (the element's inner HTML is the key), fills `{n}`-style
  values (`data-tv="n:products"`), translates `data-ta` attributes and the text of the form's Buttons and Labels. Text set
  from Python goes through `tp("English text")` (plain text) or `t()` (HTML) in `client_code/i18n.py`.
- The other languages are packs in `theme/assets/lang-fr.json`, `lang-ru.json` and `lang-lv.json`, keyed by the English text. A pack is only downloaded when the visitor chose that language: the choice is saved in the browser (`localStorage` key `aa.lang`), and a small script at the top of `anvil.yaml → native_deps.head_html` starts the download while the app boots. Switching language reloads the page.
- Notification emails go out in each person's language. The app saves it on the user row (`users.lang`) when they open the app; email texts are in `server_code/email_text.py`.
- Status notes and server messages are stored in English and translated when shown, so consultants and clients can use different languages.
- **Editing a translation:** change the value in the `lang-*.json` file (and in `email_text.py` for email wording), then bump `VERSION` in `i18n.py` and `?v=` in the head script so browsers fetch the new pack. A string with no translation falls back to English.
- The Privacy & Terms documents come from the shared LegalKit, which has English and French. Russian and Latvian visitors see them in English.

## SEO

- Title, meta description, canonical, Open Graph and Twitter cards, geo tags and keywords are in `anvil.yaml → native_deps.head_html` and `metadata`.
- JSON-LD structured data in the page head covers `ProfessionalService`/`Organization` (Montréal, areas served, services), `WebSite`, `WebPage`, `FAQPage` (same text as the on-page FAQ) an `ItemList` of portfolio projects (each with its YouTube film as `subjectOf`), a `VideoObject` for the Addanapp film, and the YouTube channel as the organisation's `sameAs`.
- All indexable content lives on the home page with semantic sections, one `h1`, and a French paragraph (`lang="fr-CA"`) for French-language searches such as "développement d'applications sur mesure Montréal".
- Each route sets its own `<title>`, and private workspace pages are marked `noindex`.
- Sitemap: `/_/api/sitemap.xml`. Submit it in Google Search Console.
- Share image: `theme/assets/og-image.png` (1200×630).

**Assumptions to check:** the domain is `https://addanapp.com` (set in `SITE_URL` in `server_code/common.py` and in the head tags). The contact email is blank for now (`CONTACT_EMAIL` in `client_code/content.py`; the spots that show it stay hidden). Turnaround promises (2-day quotes, 1–3 week features) and the privacy policy's 24-month lead retention are placeholder copy, so edit them to match how you work.

## Code map

```
client_code/
  startup.py       start-up: language pack, Privacy & Terms kit, who is signed in, router
  router.py        #addresses -> page Forms (same addresses as before), sign-in rules, page titles
  Layouts/Shell/   header (chapter links + menus, language switch, account menu, burger), footer, unread-count timer
  Pages/           Landing (all the marketing copy, in the template), Work, Guides, Privacy, Portal, NewRequest,
                   RequestDetail, Account, Admin, Estimate (#estimate), SignoffSample (#signoff/sample)
  Components/      Avatar, Progress, Seg (one-of-several buttons), RequestForm (also in the console's dialog), Shot (a
                   project's SVG preview or screenshot), SignoffCard (a sign-off record), BudgetStrip (Portal sums)
  Items/           RepeatingPanel rows: ShowcaseCard, WorkGroup/WorkRow/WorkDetail, ProofLink, LangLink, Tick, Tag, Pill,
                   Tile, AttnRow, RequestRow, BoardColumn/BoardCard, Step, NoteItem, KvRow, GuideCard, GuideLink,
                   PersonCard, LeadCard, AppNavLink, SegOption, EstQuestion, SoLine, SoCheck
  Dialogs/         AuthBox (sign in / create workspace), PromptText, NewForClient, SignOff, AcceptDelivery, ChangeOrder
  estimate.py      the estimator's questions, prices (from the pricing page) and share code; pure, the server uses it too
  signoff_data.py  the 10 sign-off checks, acceptance criteria parsing, the public sample; pure, shared with the server
  i18n.py          translations: t(), tp(), plurals, apply() for templates, dates and money per language
  content.py       films, partner decks, free guides, project-brief choices (data; the copy is in the templates)
  portfolio.py     portfolio projects, films (VIDEOS), the SVG preview "engine" (art_*), random picks
  ui.py            constants, formatting, chips, the server-call wrapper
  state.py         signed-in person, unread counts, toasts, accessibility helpers
server_code/
  common.py        users, ids, statuses, notes, email templates
  i18n_server.py   email language per user; email_text.py holds the French, Russian and Latvian email texts
  serial.py        rows → client-safe dicts (clients never see internal notes or other clients)
  api_client.py    profile, my requests, create, comment / approve / accept / request changes / withdraw
  api_admin.py     overview, update request + notes, clients, leads
  api_public.py    project-brief form (+ the estimator's briefs), sitemap
  signoff.py       sign-off records (admin_save_signoff, the "sign off before review" guard, the client's criteria)
  quotes.py        locked quotes, change orders (admin_send/cancel_change_order are in api_admin), the Portal sums
  seed.py          demo data (incl. sign-offs on delivered/review requests and one pending change order)
theme/assets/      app.css (design system + the layer that styles Anvil's components), trust.css (estimator, sign-off,
                   change orders, budget strip, print), theme.css (loading spinner),
                   icons.css (made by tools/build_icons.py from app-kit.js), app-kit.js (icons, storage, template translator,
                   accessibility glue), aa.js (scroll reveal, smooth scroll, page meta, header spy, film player),
                   lang-fr/ru/lv.json, logo, og-image
tools/             check.py, ui_test.py + ui/, i18n_check.py, assets.py, build_icons.py, testing/ (server tests + mock)
```

## Design

Ink navy and warm paper, editorial serif headlines (Instrument Serif), Inter for reading and JetBrains Mono for labels.
Violet means *AI draft* and green means *human-validated*, and that pairing runs through the site and the app.
The portfolio (53 projects, all live) lives in `client_code/portfolio.py`. **Home page:** three live projects picked at random on every visit (`picks()`), shown as large case-study panels, with **See all 53 products in depth** (→ `#work`) and a **Shuffle** button that swaps in three others. **`#work`:** first a **spotlight**, three live projects side by side as cards (preview, category, name, the blurb's first sentence, tags, Film, Try it live, and Details, which opens that project's row in the index). The live projects are shuffled into a deck per visit: **Next** steps through it three at a time ("Set 2 of 21"; at the end a fresh round starts), **Refresh** reshuffles with the cards on screen moved to the back. Under 1020 px the cards become a swipeable row (scroll snap). Below it, the full index, every project as a compact row grouped by category with filter chips; each row opens in place to show the preview, what we built, a **Watch the film** link to its one-minute film on the Addanapp YouTube channel (`VIDEOS`) and the live link. Previews are hand-drawn SVG mini-UIs for the first 27 projects; the 26 added on 2026-11-02 (`'art': 'shot'`) show the real landing page (`theme/assets/pf/<key>.jpg`, from the App Board hero shots) in a matching browser frame. Categories: Working businesses, Useful tools, **Learning & guides** (added 2026-11-02), Engaging games, VR & mixed reality, Mobile-style apps, Websites. `'new': True` shows a **New** badge (none right now); a project with no `domain` shows **Launching soon** and isn't a link.

**YouTube** (`#youtube` on the home page): the channel youtube.com/@addanapp and a click-to-play embed of the Addanapp film in the visitor's language (`YT_FILMS` in content.py: English, French, Russian, Latvian), with links to the other three under it. Nothing loads from YouTube until the visitor presses play; then it plays from youtube-nocookie.com (listed in Privacy as the `youtube_play` provider).

**Partner deck** (`#partners`, after Engagements; also in the header's Engagements menu and the footer): all 20 slides of the "Addanapp Partner Deck" Slides artifact (https://claude.ai/artifact/X7izxcayZdhgbzmsdrN9Ua) as a PDF in four languages, `theme/assets/addanapp-partner-deck.pdf` (English) and `addanapp-partner-deck-fr/-ru/-lv.pdf`, each with its cover image (`partner-deck-cover[-fr|-ru|-lv].jpg`). The visitor's language is the main download; the other three are listed under it (`DECKS` in content.py). Its "firms like these" slide names firms only as examples, with a no-affiliation note: the user is not partnering with them. Re-render after the deck changes (recipe in the addanapp skill; translations in `.claude/skills/addanapp/scripts/deck_i18n/`).

**Free guides** (`#guides`, added 2026-11-03; home teaser `#home/guides` after the commitments, Engagements menu and footer): five short PDF lead magnets made in `Documents/CLAUDE/addanapp-guides` (rebuild there, then copy `out/<slug>.pdf` and a 480 px cover JPG to `theme/assets/guides/`). One email unlocks all five: `api_public.request_guides` saves a lead (`source` = `guide`, or `guide+news` when the person ticked the unticked "occasional tips" box; their situation is the `kind`; the CASL consent wording, time and language are written into `message`), emails the links at most once a day per address, and returns them; the browser remembers them in localStorage (`aa.guides`). Only "I have an app idea" / "We're building something now" alert the consultants and count in the Leads badge. The Leads tab filters briefs vs guide readers and exports the tips list as CSV (`admin_newsletter_csv`). The PDFs are public theme assets (this repo is public), so the email step is a soft gate. No tips emails are sent yet: a real newsletter needs a sender with an unsubscribe link and a mailing address (CASL).

**Header "chapters"** (keeping a long page tidy): the header has six links and no more. Each home-page section belongs to one of them through `data-ch` on its `<section>` (or `data-ch=""` for none), and the link of the section in view lights up while you scroll (`aa.spy` in aa.js). Sections without their own link are reached from a small menu on their chapter's link (the `aa-nav-grp` blocks in `Layouts/Shell`: **Work** → all products, films on YouTube; **Engagements** → ways to work together, partner with us, partner deck). On phones the menu lists those sub-links under their link. A new section joins a chapter (and, if visitors need to jump to it, that chapter's menu) rather than getting a new header link.

<!-- libraries:start -->
## Libraries and outside services

What this project uses besides its own code. Generated by `APP_MAKER/tools/libraries.py`; to change it, edit `APP_MAKER/libraries/catalog.py` and re-run the script.

| Name | How it gets in | Used here for |
|---|---|---|
| [YouTube embeds](https://developers.google.com/youtube/player_parameters) | Outside web service | Plays a YouTube video inside the page (the privacy-friendlier youtube-nocookie address). |
| [YouTube Data API](https://developers.google.com/youtube/v3) | Outside web service | Uploads videos, captions and thumbnails to a YouTube channel. |
| [Google Fonts](https://fonts.google.com) | Loaded from a CDN | Instrument Serif, Inter, JetBrains Mono, PT Serif |

**Built into the browser:** localStorage, Clipboard, IntersectionObserver.

**Anvil platform:** Anvil, Anvil Data Tables, Anvil Email, Anvil JS bridge (anvil.js), Anvil Secrets, Anvil Users, Anvil Google service, Anvil HTTP, Anvil timezones (anvil.tz), Anvil Media.

**Build and test tools (not shipped):** axe-core, Node.js, Headless Chrome (DevTools Protocol).

<!-- libraries:end -->
