# Addanapp

**Apps built at AI speed. Signed off by senior engineers.**

Addanapp is the website and client platform for a Montréal software consultancy. It has three parts:

| Area | What it does |
| --- | --- |
| **Landing page** (`#home`) | The marketing site: hero with a live request mock, "hours vs outcomes" comparison, the 5-step AI + human method, capabilities, portfolio with category filters, client workspace preview, engagement models, commitments, a bilingual Montréal section, FAQ and a project-brief form. |
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
2. Accept the **data table schema** from `anvil.yaml` (4 tables: `users`, `requests`, `notes`, `leads`).
3. Run the app and create a workspace with **arkulinskis@gmail.com**. Emails listed in `ADMIN_EMAILS` (`server_code/common.py`) become consultants automatically. Other consultants can be promoted from **Console → Clients**.
4. Optional: **Console → Tools → Load demo data** adds 3 fictional clients and 8 requests at every stage. Demo clients can't sign in and never get email.

Services used: Data Tables, Users (email + password, sign-up on, no email confirmation), Email.

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
  content.py       landing page copy and markup
  portfolio.py     portfolio projects + illustrated SVG previews
  ui.py            constants, HTML helpers, formatting, form reading, server-call wrapper
  icons.py         inline SVG icons and the logo
  dialogs.py       sign in / create workspace, text prompts
  state.py         signed-in user, unread counts, navigation
server_code/
  common.py        users, ids, statuses, notes, email templates
  serial.py        rows → client-safe dicts (clients never see internal notes or other clients)
  api_client.py    profile, my requests, create, comment / approve / accept / request changes / withdraw
  api_admin.py     overview, update request + notes, clients, leads
  api_public.py    project-brief form, sitemap
  seed.py          demo data
theme/assets/      theme.css (design system), aa.js (scroll reveal, page meta), logo, icons, og-image
```

## Design

Ink navy and warm paper, editorial serif headlines (Instrument Serif), Inter for reading and JetBrains Mono for labels.
Violet means *AI draft* and green means *human-validated*, and that pairing runs through the site and the app.
Portfolio previews are hand-drawn SVG mini-UIs in each product's own colours, so they stay crisp and need no screenshots.
