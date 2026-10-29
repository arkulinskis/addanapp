# Addanapp

**Apps built at AI speed. Signed off by senior engineers.**

Addanapp is the website and client platform for a Montréal software consultancy. It has three parts:

| Area | What it does |
| --- | --- |
| **Landing page** (`#home`) | The marketing site: hero with a live request mock, "hours vs outcomes" comparison, the 5-step AI + human method, capabilities, portfolio (featured case studies + a full project index with filters), client workspace preview, engagement models, commitments, a bilingual Montréal section, FAQ and a project-brief form. |
| **Client workspace** (`#portal`) | Clients sign up and submit requests (feature, fix, integration, new app…), approve fixed quotes, follow progress notes, accept deliveries or request changes. |
| **Consultant console** (`#admin`) | Every request across clients as a list or Kanban board. Post progress notes (update, milestone, human-validated, question, internal), set status, progress %, fixed quote, scope summary and ETA. Also manage clients, website leads and demo data. |

Other routes: `#work` (full portfolio), `#r/<id>` (one request), `#new`, `#account`, `#privacy`, `#login`, `#signup`.

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

Services used: Data Tables, Users (email + password, sign-up on, no email confirmation), Email.

## Languages

The whole site and app are available in **English, French, Russian and Latvian**. Pick one from the globe button in the header (or the footer, or **Account → Language**).

- English is built into the code and loads with no extra download. Every visible string goes through `t("English text")` (`client_code/i18n.py`).
- The other languages are packs in `theme/assets/lang-fr.json`, `lang-ru.json` and `lang-lv.json`, keyed by the English text. A pack is only downloaded when the visitor chose that language: the choice is saved in the browser (`localStorage` key `aa.lang`), and a small script at the top of `anvil.yaml → native_deps.head_html` starts the download while the app boots. Switching language reloads the page.
- Notification emails go out in each person's language. The app saves it on the user row (`users.lang`) when they open the app; email texts are in `server_code/email_text.py`.
- Status notes and server messages are stored in English and translated when shown, so consultants and clients can use different languages.
- **Editing a translation:** change the value in the `lang-*.json` file (and in `email_text.py` for email wording), then bump `VERSION` in `i18n.py` and `?v=` in the head script so browsers fetch the new pack. A string with no translation falls back to English.
- The Privacy & Terms documents come from the shared LegalKit, which has English and French. Russian and Latvian visitors see them in English.

## SEO

- Title, meta description, canonical, Open Graph and Twitter cards, geo tags and keywords are in `anvil.yaml → native_deps.head_html` and `metadata`.
- JSON-LD structured data in the page head covers `ProfessionalService`/`Organization` (Montréal, areas served, services), `WebSite`, `WebPage`, `FAQPage` (same text as the on-page FAQ) and an `ItemList` of portfolio projects.
- All indexable content lives on the home page with semantic sections, one `h1`, and a French paragraph (`lang="fr-CA"`) for French-language searches such as "développement d'applications sur mesure Montréal".
- Each route sets its own `<title>`, and private workspace pages are marked `noindex`.
- Sitemap: `/_/api/sitemap.xml`. Submit it in Google Search Console.
- Share image: `theme/assets/og-image.png` (1200×630).

**Assumptions to check:** the domain is `https://addanapp.com` (set in `SITE_URL` in `server_code/common.py` and in the head tags). The contact email is `hello@addanapp.com` (`client_code/content.py`). Turnaround promises (2-day quotes, 1–3 week features) and the privacy policy's 24-month lead retention are placeholder copy, so edit them to match how you work.

## Code map

```
client_code/
  Main/            app shell (header, footer) + hash router
  Landing/         marketing page (markup in content.py)
  Work/            full portfolio page
  Portal/          client dashboard
  NewRequest/      request form (also reused by the console's "request for a client")
  RequestDetail/   one request: stepper, client actions, timeline, consultant manage panel
  Admin/           consultant console: requests (list/board), clients, leads, tools
  Account/ Privacy/
  i18n.py          translations: t(), plurals, dates and money per language, language switching
  content.py       landing page copy and markup
  portfolio.py     portfolio projects + illustrated SVG previews
  ui.py            constants, HTML helpers, formatting, form reading, server-call wrapper
  icons.py         inline SVG icons and the logo
  dialogs.py       sign in / create workspace, text prompts
  state.py         signed-in user, unread counts, navigation
server_code/
  common.py        users, ids, statuses, notes, email templates
  i18n_server.py   email language per user; email_text.py holds the French, Russian and Latvian email texts
  serial.py        rows → client-safe dicts (clients never see internal notes or other clients)
  api_client.py    profile, my requests, create, comment / approve / accept / request changes / withdraw
  api_admin.py     overview, update request + notes, clients, leads
  api_public.py    project-brief form, sitemap
  seed.py          demo data
theme/assets/      theme.css (design system), aa.js (scroll reveal, page meta), lang-fr/ru/lv.json, logo, icons, og-image
```

## Design

Ink navy and warm paper, editorial serif headlines (Instrument Serif), Inter for reading and JetBrains Mono for labels.
Violet means *AI draft* and green means *human-validated*, and that pairing runs through the site and the app.
The portfolio (22 projects, all live) has two parts, on both the home page and `#work`: **case studies** (the projects with a `featured` number, now PlanPlate, Prepsto and Subsudo) as large split panels, then **the full index**, every project as a compact row grouped by category with filter chips. On the home page each row links to the live product and hovering it shows its preview in a sticky side panel (desktop); on `#work` each row opens in place to show the preview and what we built. The previews are hand-drawn SVG mini-UIs in each product's own colours, so they stay crisp and need no screenshots. The newest work carries a **New** badge; a project with no `domain` yet shows **Launching soon** and isn't a link.
