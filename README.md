# Addanapp

**Apps built at AI speed. Signed off by senior engineers.**

Addanapp is the website and client platform for a Montréal software consultancy. It has three parts:

| Area | What it does |
| --- | --- |
| **Landing page** (`#home`) | The marketing site: hero with a live request mock, "hours vs outcomes" comparison, the 5-step AI + human method, capabilities, portfolio (three projects picked at random, a Shuffle button and a link to the full index), the YouTube channel with the Addanapp film, client workspace preview, engagement models, a partner-deck download for agencies, commitments, a bilingual Montréal section, FAQ and a project-brief form. |
| **Client workspace** (`#portal`) | Clients sign up and submit requests (feature, fix, integration, new app…), approve fixed quotes, follow progress notes, accept deliveries or request changes. |
| **Consultant console** (`#admin`) | Every request across clients as a list or Kanban board. Post progress notes (update, milestone, human-validated, question, internal), set status, progress %, fixed quote, scope summary and ETA. Also manage clients, website leads and demo data. |

Other routes: `#work` (full portfolio: every project, with what we built, its film and its link), `#guides[/<slug>]` (the free PDF guides, unlocked with an email), `#r/<id>` (one request), `#new`, `#account`, `#privacy`, `#login`, `#signup`.

## Request lifecycle

`Submitted → Scoping → Quote ready → In progress → Ready for review → Delivered` (plus `On hold` and `Closed`).

- The consultant sets the fixed quote and ETA, then moves the request to **Quote ready**. The client clicks **Approve quote** and it moves to In progress.
- The consultant marks it **Ready for review**. The client clicks **Accept delivery** (it becomes Delivered and can be invoiced) or **Request changes** (it goes back to In progress with their comment).
- Internal notes are never sent to clients. Client-visible notes and status changes are emailed to the client, and client actions are emailed to consultants.

## Getting it running in Anvil

1. In the Anvil editor, pull `master` from GitHub (or clone the repo as a new app).
2. Accept the **data table schema** from `anvil.yaml` (4 tables: `users`, `requests`, `notes`, `leads`). The `users.lang` column stores each person's language for emails.
3. Run the app and create a workspace with **arkulinskis@gmail.com**. Emails listed in `ADMIN_EMAILS` (`server_code/common.py`) become consultants automatically. Other consultants can be promoted from **Console → Clients**.
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
                   RequestDetail, Account, Admin
  Components/      Avatar, Progress, Seg (one-of-several buttons), RequestForm (also in the console's dialog), Shot (a
                   project's SVG preview or screenshot)
  Items/           RepeatingPanel rows: ShowcaseCard, WorkGroup/WorkRow/WorkDetail, ProofLink, LangLink, Tick, Tag, Pill,
                   Tile, AttnRow, RequestRow, BoardColumn/BoardCard, Step, NoteItem, KvRow, GuideCard, GuideLink,
                   PersonCard, LeadCard, AppNavLink, SegOption
  Dialogs/         AuthBox (sign in / create workspace), PromptText, NewForClient
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
  api_public.py    project-brief form, sitemap
  seed.py          demo data
theme/assets/      app.css (design system + the layer that styles Anvil's components), theme.css (loading spinner),
                   icons.css (made by tools/build_icons.py from app-kit.js), app-kit.js (icons, storage, template translator,
                   accessibility glue), aa.js (scroll reveal, smooth scroll, page meta, header spy, film player),
                   lang-fr/ru/lv.json, logo, og-image
tools/             check.py, ui_test.py + ui/, i18n_check.py, assets.py, build_icons.py, testing/ (server tests + mock)
```

## Design

Ink navy and warm paper, editorial serif headlines (Instrument Serif), Inter for reading and JetBrains Mono for labels.
Violet means *AI draft* and green means *human-validated*, and that pairing runs through the site and the app.
The portfolio (53 projects, all live) lives in `client_code/portfolio.py`. **Home page:** three live projects picked at random on every visit (`picks()`), shown as large case-study panels, with **See all 53 products in depth** (→ `#work`) and a **Shuffle** button that swaps in three others. **`#work`:** the full index, every project as a compact row grouped by category with filter chips; each row opens in place to show the preview, what we built, a **Watch the film** link to its one-minute film on the Addanapp YouTube channel (`VIDEOS`) and the live link. Previews are hand-drawn SVG mini-UIs for the first 27 projects; the 26 added on 2026-11-02 (`'art': 'shot'`) show the real landing page (`theme/assets/pf/<key>.jpg`, from the App Board hero shots) in a matching browser frame. Categories: Working businesses, Useful tools, **Learning & guides** (added 2026-11-02), Engaging games, VR & mixed reality, Mobile-style apps, Websites. `'new': True` shows a **New** badge (none right now); a project with no `domain` shows **Launching soon** and isn't a link.

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
| [Google Fonts](https://fonts.google.com) | Loaded from a CDN | Instrument Serif, Inter, JetBrains Mono, PT Serif |

**Built into the browser:** localStorage, Clipboard, IntersectionObserver.

**Anvil platform:** Anvil, Anvil Data Tables, Anvil Google service, Anvil JS bridge (anvil.js), Anvil Users, Anvil Email, Anvil timezones (anvil.tz).

<!-- libraries:end -->
