---
name: addanapp
description: Context, workflow and recipes for Addanapp (addanapp.com), the user's Anvil site for their Montréal software consultancy: a marketing landing page with portfolio, a client workspace for feature requests, and a consultant console; English, French, Russian and Latvian. Load this before any content change, portfolio update, translation, feature request, bug fix or deploy for Addanapp.
---

# Addanapp: working on the app

**What it is:** the website and client platform of the user's consultancy ("Apps built at AI speed. Signed off by senior engineers.").
- **Landing page** (`#home`): hero with a live request mock, hours vs outcomes, the 5-step AI + human method, capabilities, a **portfolio** with category filters (the user's own apps: Working businesses / Useful tools…), client workspace preview, engagement models, commitments, a bilingual Montréal section, FAQ, project-brief form (→ leads).
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
- **Recent / not-yet-live projects:** `'new': True` shows a "New" badge (OScreenplay and Yabanana, added 2026-10-26, sit right after PlanPlate). `'domain': ''` shows "Launching soon" with no link: when Yabanana goes live, set its domain, add it to the JSON-LD ItemList, and later drop the `new` flags.
- **New portfolio project:** an entry in portfolio.py (category, url, description) + an `art_<name>()` SVG mini-UI in its own colours; keep the JSON-LD ItemList in the head in step. The user's apps and their live URLs are in `APP_MAKER/apps.json`.
- **SEO:** title/meta/OG/JSON-LD live in `anvil.yaml → native_deps.head_html` and `metadata`; each route sets its own `<title>`; private pages are `noindex`.

## Gotchas

- Russian and Latvian visitors see the Privacy & Terms page in English (the legal kit has EN/FR only).
- Placeholder business facts to confirm with the user before relying on them: hello@addanapp.com, 2-day quotes, 1–3 week features, 24-month lead retention.
- `python -I` hides PyYAML: run gitapp_check/gitapp_test without `-I`.
- The header's frosted glass lives on `.aa-header::before`, not on `.aa-header`: a `backdrop-filter` (or filter/transform) on the header traps the full-screen burger menu (`position: fixed`) inside the 60px bar. Fixed 2026-10-26.

## Privacy & Terms (legal kit)

From `C:/Users/arkvi/Documents/CLAUDE/APP_MAKER/legal-kit`. Don't edit `theme/assets/legal-kit.js`, `client_code/legal.py` or `server_code/legal_server.py` here: change `apps/addanapp.json` there, run `python -I build.py addanapp && python -I install.py addanapp`, then commit and push here.
- Sign-up keeps the consent tick box (dialogs.auth); `legal.refresh_soon()` after sign-in, `legal.signed_out()` after sign-out.
