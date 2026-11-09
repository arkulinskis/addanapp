"""Portfolio: projects we've shipped, with illustrated previews (inline SVG) or real screenshots ('art': 'shot').

The art_* functions are the drawing "engine": each returns one SVG (400 x 250) in the product's colours, and
Components/Shot puts it on the page. Cards and index rows are Forms (Items/ShowcaseCard, Items/WorkRow)."""
import random

from .i18n import tp

# Project text below is English; the cards and rows translate it (i18n.tp) when they are drawn.
CATEGORIES = [
  ('all', tp('All work')),
  ('business', tp('Working businesses')),
  ('tools', tp('Useful tools')),
  ('learn', tp('Learning & guides')),
  ('games', tp('Engaging games')),
  ('vr', tp('VR & mixed reality')),
  ('mobile', tp('Mobile-style apps')),
  ('sites', tp('Websites')),
]
CAT = dict(CATEGORIES)

PROJECTS: list = [  # each project: a dict of plain values (see the first one)
  {
    'key': 'planplate', 'name': 'PlanPlate', 'domain': 'planplate.com', 'cat': 'business',
    'blurb': 'A restaurant reservation and content API platform. Managers run bookings for every location from one portal, and guests book straight from the restaurant\'s own website.',
    'built': ['Multi-restaurant manager portal', 'Drag-and-drop floor plans and table joins',
              'Opening-hour rules, special days and auto-approval', 'Public reservation and content API'],
    'tags': ['SaaS', 'Public API', 'Admin portal'], 'color': '#1F6B63', 'bg': '#DCE7E8', 'art': 'planplate',
  },
  # 'new': True shows a "New" badge (none right now). The home page shows three live projects picked at random (picks()).
  # A project without a 'domain' shows "Launching soon" and isn't a link. The index groups projects by category.
  {
    'key': 'prepsto', 'name': 'Prepsto', 'domain': 'prepsto.com', 'cat': 'business',
    'blurb': 'A feedback inbox that turns what users say into user stories. Drop one script tag on any site, triage everything on a board, then export ready-to-build stories to Jira, Gherkin or an AI-ready bundle.',
    'built': ['Embeddable feedback widget, one script tag', 'Inbox and drag-and-drop board with sentiment and themes',
              'Story editor with exports to Jira, Gherkin, CSV and JSON'],
    'tags': ['SaaS', 'Embeddable widget', 'Rule engine'], 'color': '#2B59FF', 'bg': '#EBF0FF', 'art': 'feedback',
  },
  {
    'key': 'vitalrpa', 'name': 'VitalRPA', 'domain': 'vitalrpa.com', 'cat': 'business',
    'blurb': 'Robots that watch every website you run, around the clock. They check uptime, certificates, domains and security headers with no code on the site, a tiny optional beacon adds real visitors and JavaScript errors, and playbooks email, ping Slack or recheck the moment something breaks.',
    'built': ['Uptime, certificate, domain and security-header robots', 'Visitor beacon under 1 KB, with no cookies',
              'Incident playbooks, cron heartbeats and public status pages'],
    'tags': ['SaaS', 'Monitoring', 'Automation'], 'color': '#0A5CE6', 'bg': '#E6EEF8', 'art': 'monitor',
  },
  {
    'key': 'arvistay', 'name': 'ArviStay', 'domain': 'arvistay.com', 'cat': 'business',
    'blurb': 'Hotel websites that sell the stay, not just the room. An owner types the address, and ArviStay maps the neighbourhood, drafts the texts and builds a phone-first site with rooms, 360° tours, a 3D map and an hour-by-hour stay plan for each kind of guest.',
    'built': ['Neighbourhood scan from OpenStreetMap and Wikipedia', '3D neighbourhood map, 360° room tours and galleries',
              'Hour-by-hour stay plans for 30 kinds of guest'],
    'tags': ['SaaS', 'Website builder', '3D maps'], 'color': '#1F5C55', 'bg': '#F4EDE0', 'art': 'hotel',
  },
  {
    'key': 'subsudo', 'name': 'Subsudo', 'domain': 'subsudo.com', 'cat': 'games',
    'blurb': 'A virtual fight club. Shadow-box one round with your phone in your fist or in front of your laptop camera, send it as a sealed call-out to anyone in the world, and three automatic judges score the bout.',
    'built': ['Punch detection from phone motion sensors', 'In-browser hand tracking, the video never leaves the device',
              "Elo rankings by city and world, belts and judges' cards"],
    'tags': ['Game', 'Motion sensors', 'Computer vision'], 'color': '#8E1B1B', 'bg': '#EFE9DF', 'art': 'boxing',
  },
  {
    'key': 'quickybricks', 'name': 'QuickyBricks', 'domain': 'quickybricks.com', 'cat': 'games',
    'blurb': 'A silly 3D game for kids and their grown-ups. Every character is a squishy cube that does something different on each of its six sides, and cubes that hold hands in the shared World grow a family.',
    'built': ['Real-time 3D cubes built with three.js', 'Cube maker with colours, faces and a doodle pad',
              'Shared World where families grow across players'],
    'tags': ['3D', 'Multiplayer', 'Kids'], 'color': '#F0428C', 'bg': '#FFF4E0', 'art': 'cubes',
  },
  {
    'key': 'toonyloony', 'name': 'ToonyLoony', 'domain': 'toonyloony.com', 'cat': 'games',
    'blurb': 'A cartoon studio for kids, right in the browser. Build characters from parts on joints and sticks, animate them with keyframes, then hold and drag them across the stage to record a movie with voices, sound effects and music.',
    'built': ['Character builder on joints-and-sticks rigs', 'Keyframe animator with a library of moves',
              'Hold-to-record studio with voices, lip-sync and video export'],
    'tags': ['Kids', 'Animation', 'Creative tools'], 'color': '#4757FF', 'bg': '#EEF1FF', 'art': 'toon',
  },
  {
    'key': 'planfriday', 'name': 'Plan Friday', 'domain': 'planfriday.com', 'cat': 'tools',
    'blurb': 'The easy way to plan a weekend dinner with any group of friends. Send one link: friends pick the slots that suit them and say what they are bringing, with no account, and the host locks in the best night.',
    'built': ['Party pages guests open without an account', 'Who-is-free grid with a best-day pick',
              'Potluck menu with diet warnings and a printable sheet'],
    'tags': ['Social', 'Group planning', 'No account needed'], 'color': '#C62A1F', 'bg': '#F2E8D3', 'art': 'party',
  },
  {
    'key': 'topameal', 'name': 'Topameal', 'domain': 'topameal.com', 'cat': 'mobile',
    'blurb': 'A shop-and-cook planner built around one fancy sauce over the rice, pasta and potatoes you already have. It writes one merged shopping list, orders the week so nothing spoils, and counts the dishes you will wash.',
    'built': ['A week of one-pan toppers, picked for you', 'One merged shopping list in walking order',
              'Shared household lists that tick off live'],
    'tags': ['Mobile-first', 'Meal planning', 'Shared lists'], 'color': '#C4533A', 'bg': '#FBF3E6', 'art': 'pan',
  },
  {
    'key': 'oscreenplay', 'name': 'OScreenplay', 'domain': 'oscreenplay.com', 'cat': 'tools',
    'blurb': 'A screenwriting studio that takes you from a half-formed idea to properly formatted pages. Pull a story spark, build characters who react like real people, then write while a script doctor flags what is missing.',
    'built': ['Story-spark machine with 780 hand-built ideas', 'Character web and two timelines: what happened vs. how we tell it',
              'Real screenplay editor with Fountain and PDF export'],
    'tags': ['Creative tools', 'Rich editor', 'Rule engine'], 'color': '#C8102E', 'bg': '#F3EEE4', 'art': 'screenplay',
  },
  {
    'key': 'yabanana', 'name': 'Yabanana', 'domain': 'yabanana.com', 'cat': 'tools',
    'blurb': 'A song-writing community for rappers, poets and pop writers. Write lyrics over twelve beats with rhymes, similes and metaphors one click away, then share them to a stage where others upvote, review and remix.',
    'built': ['Lyric editor with a live rhyme map and syllable counts', 'Twelve beats, from boom bap to iambic pentameter',
              'Upvotes, reviews, weekly charts and remixes'],
    'tags': ['Community', 'Web Audio', 'Gamification'], 'color': '#E8A317', 'bg': '#FFF3CC', 'art': 'lyrics',
  },
  {
    'key': 'logsteps', 'name': 'Logsteps', 'domain': 'logsteps.com', 'cat': 'mobile',
    'blurb': 'Walk slowly around a room with your phone and get a 3D model of it. Step back inside, replay your walk, measure walls, pin notes and share the room with a link.',
    'built': ['Guided phone camera walk, video upload or 3D file import', 'GPU scan station that turns frames into a 3D room',
              '3D viewer with walk mode, measuring, pins and a desktop studio'],
    'tags': ['Mobile-first', '3D', 'GPU pipeline'], 'color': '#0E7C86', 'bg': '#DDF1F2', 'art': 'rooms',
  },
  {
    'key': 'robointern', 'name': 'RoboIntern', 'domain': 'robointern.com', 'cat': 'tools',
    'blurb': 'A field guide to machine-learning models, with the Python included. Paste your column headers, mark what you want to predict, and get the models that fit, ranked and explained, plus ready-to-run training code.',
    'built': ['Atlas of 43 models with the maths explained', 'Visible scoring that ranks the models for your data',
              'Writes train.py, predict.py and a Jupyter notebook'],
    'tags': ['Machine learning', 'Code generator', 'Reference'], 'color': '#2B4C9B', 'bg': '#E9ECF5', 'art': 'models',
  },
  {
    'key': 'monshop', 'name': 'MonShop', 'domain': 'monshop.ca', 'cat': 'business',
    'blurb': 'A two-way local marketplace. Vendors post their latest arrivals, specials and updates, and shoppers discover them on a live map of their neighbourhood.',
    'built': ['Separate vendor and shopper experiences', 'Live map of vendor updates', 'Posting, moderation and vendor profiles'],
    'tags': ['Marketplace', 'Maps', 'Two-sided'], 'color': '#1668C7', 'bg': '#E2EDFA', 'art': 'monshop',
  },
  {
    'key': 'adorablescience', 'name': 'Adorable Science', 'domain': 'adorablescience.com', 'cat': 'business',
    'blurb': 'A multi-user science blog with a real editorial workflow. Writers draft, editors review and nothing is published until it has been approved.',
    'built': ['Writer accounts and an editorial review queue', 'Citation meter and reviewer checklists',
              'Approve, or send back with notes'],
    'tags': ['CMS', 'Roles & moderation', 'Publishing'], 'color': '#D9487A', 'bg': '#FDECF2', 'art': 'blog',
  },
  {
    'key': 'citycrossers', 'name': 'CityCrossers', 'domain': 'citycrossers.com', 'cat': 'business',
    'blurb': 'Tinder for walking groups. Swipe on group walks, plan routes with snack stops on a live map, and meet people who would rather stroll 20 km than sprint 5.',
    'built': ['Swipe deck ranked by match score', 'Map route planner with break estimates',
              'Points, perks and a moderation admin'],
    'tags': ['Social', 'Maps', 'Gamification'], 'color': '#17A673', 'bg': '#E2F5EC', 'art': 'map',
  },
  {
    'key': 'varnote', 'name': 'Varnote', 'domain': 'varnote-offline.web.app', 'cat': 'tools',
    'blurb': 'A faster note-taking app built around inline tagging. Type #tags as you write, then slice thousands of notes down to the ones you need in a keystroke.',
    'built': ['Inline #tags while you type', 'Instant multi-tag filtering', 'Offline-first and installable'],
    'tags': ['Productivity', 'Offline-first', 'PWA'], 'color': '#3446D8', 'bg': '#E8EBFF', 'art': 'varnote',
  },
  {
    'key': 'funtoplan', 'name': 'FunToPlan', 'domain': 'funtoplan.com', 'cat': 'tools',
    'blurb': 'A family to-do list where chores earn brownie points. Parents set the tasks, kids tick them off, and everyone can see who is ahead this week.',
    'built': ['Shared family boards and roles', 'Brownie points for completed tasks', 'Weekly leaderboard and rewards'],
    'tags': ['Family', 'Gamification', 'Productivity'], 'color': '#A0582A', 'bg': '#F8EADD', 'art': 'family',
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
  # VR & mixed reality: WebXR apps for Meta Quest (and any WebXR headset), each with a flat-screen mode too.
  {
    'key': 'snackpuncher', 'name': 'Snackpuncher', 'domain': 'snackpuncher.anvil.app', 'cat': 'vr',
    'blurb': 'A VR boxing quest against an army of googly-eyed fast food. Punch, duck and block your way across ten lands in a Meta Quest headset, free 41 villagers and collect 100 treasures, while a workout log counts every muscle you used.',
    'built': ['WebXR battles with jabs, hooks, uppercuts, ducks and blocks', 'Ten story lands, a growing village and 100 treasures',
              'Passthrough mode, flat-screen play and a workout log'],
    'tags': ['VR', 'Fitness', 'Game'], 'color': '#2F6D3A', 'bg': '#F6ECD6', 'art': 'snacks',
  },
  {
    'key': 'walltracer', 'name': 'WallTracer', 'domain': 'walltracer.anvil.app', 'cat': 'vr',
    'blurb': 'A virtual projector for tracing pictures onto real walls. Pin a picture to your wall at its true size in a Meta Quest headset, lock it in place and trace it with a pencil, then pinch your free hand to hide it and check your lines.',
    'built': ['Passthrough placing with hit-testing and saved anchors', 'Picture editor with line, outline and tone looks, real size and a grid',
              'Stencil library, lettering maker and a showcase of finished walls'],
    'tags': ['Mixed reality', 'DIY', 'Image processing'], 'color': '#C4552D', 'bg': '#EFE9E1', 'art': 'wall',
  },
  {
    'key': 'mrbigstage', 'name': 'MrBigStage', 'domain': 'mrbigstage.anvil.app', 'cat': 'vr',
    'blurb': 'Rehearse your talk in front of a 3D audience that reacts to you. Speak in VR or on a screen and get coached on pace, pauses, filler words, projection and eye contact, all blended into one confidence score.',
    'built': ['Seven rooms, from a boardroom to a 5,000-seat arena', 'Voice analysis in the browser: pace, pauses, fillers and pitch',
              'An audience that leans in or checks its phones, plus Q&A and drills'],
    'tags': ['VR', 'Voice analysis', 'Coaching'], 'color': '#E0261B', 'bg': '#F5F2EC', 'art': 'stage',
  },
  {
    'key': 'poundfighter', 'name': 'PoundFighter', 'domain': 'poundfighter.com', 'cat': 'mobile',
    'blurb': 'A quick exercise motivator. Micro-workouts become monster fights, and the microphone counts your reps: grunt, clap or shout "HUP!".',
    'built': ['Voice rep counting through the mic', '36 collectible monsters in 4 rarities', 'Daily punch card, ranks and shop'],
    'tags': ['Mobile-first', 'Voice', 'Fitness'], 'color': '#E2452F', 'bg': '#FDE6E1', 'art': 'pound',
  },
  {
    'key': 'parapeet', 'name': 'Parapeet', 'domain': 'parapeet.com', 'cat': 'mobile',
    'blurb': "Everyday French, Spanish and Italian phrases in ten moods, from your boss to a sad friend. A live app from 2023 that we rebuilt from scratch in 2026: new mood cards, short lessons, and every player's progress carried over.",
    'built': ["Rebuilt from scratch, with players' progress carried over", 'Ten moods, each with its own colour, icon and highlighted words', 'Short lessons: guess the meaning, spot the mood, build and say the sentence'],
    'tags': ['Mobile-first', 'Language learning', 'App rebuild'], 'color': '#3F9A35', 'bg': '#E4F2DD', 'art': 'parrot',
  },
  {
    'key': 'dilettante', 'name': 'Dilettante', 'domain': 'dilettante.com', 'cat': 'sites',
    'blurb': 'A classic restaurant website with live PlanPlate reservations built in. Guests can browse the menu and book a table without leaving the page.',
    'built': ['Classic, fast restaurant website', 'Live PlanPlate reservation widget', 'Menus and events from the content API'],
    'tags': ['Website', 'API integration', 'Hospitality'], 'color': '#7C2D2D', 'bg': '#F3EAE1', 'art': 'resto',
  },
  {
    'key': 'arkvital', 'name': 'Arkvital', 'domain': 'arkvital.com', 'cat': 'sites',
    'blurb': 'A personal website for an engineer turned leadership coach. A bold editorial home page, four clear ways to work together and selected work, all built to turn a visit into a first call.',
    'built': ['Editorial home page with a portrait hero', 'Services, selected work and writing pages',
              'Fast static pages in light and dark themes'],
    'tags': ['Website', 'Personal brand', 'Consulting'], 'color': '#0B6F94', 'bg': '#F7F3EE', 'art': 'personal',
  },
  # Added 2026-11-02. 'art': 'shot' = the app's real landing page (theme/assets/pf/<key>.jpg, from the App Board
  # hero shots: APP_MAKER/board/heroes) in a browser frame instead of a hand-drawn SVG.
  {
    'key': 'healthbooker', 'name': 'Health Booker', 'domain': 'health-booker.anvil.app', 'cat': 'business',
    'blurb': 'One account for every yoga studio in the city. Students find and book classes, pick their mat and keep every pass in one wallet, while each studio runs its schedule, passes, subs and teacher pay with no commission.',
    'built': ['Marketplace search and booking across studios', 'Studio back office: schedule, passes, subs and teacher pay', 'Fair waitlists, a practice journal and a free data export'],
    'tags': ['Marketplace', 'Multi-tenant', 'Booking'], 'color': '#5E8263', 'bg': '#F6F1E9', 'art': 'shot',
  },
  {
    'key': 'autoagile', 'name': 'AutoAgile', 'domain': 'autoagile.anvil.app', 'cat': 'business',
    'blurb': 'An agile board for crews of people and AI developers. Teams start in Kanban and unlock sprints, forecasts and a roadmap as their data matures, while AI agents pull, claim and hand in cards through an API for human review.',
    'built': ['Kanban, sprints, forecasts and a year roadmap', 'Agent API: pull, claim, log and hand in for review', 'Complexity-gate estimates, D3 reports and Jira import'],
    'tags': ['SaaS', 'AI agents', 'Productivity'], 'color': '#0C061B', 'bg': '#EEEBE0', 'art': 'shot',
  },
  {
    'key': 'goodlandlord', 'name': 'Good Landlord', 'domain': 'good-landlord.anvil.app', 'cat': 'business',
    'blurb': 'Rental numbers and fair tenant records for small landlords. Track rent and every claimable expense, see cash flow, equity and long-term profit, and give each tenant a private, tamper-evident log of messages and repairs.',
    'built': ['Rent, expenses, mortgage and equity per property', 'Profit if sold today or in 20 years', 'Tamper-evident tenant record of messages and repairs'],
    'tags': ['SaaS', 'Finance', 'Property'], 'color': '#B4502A', 'bg': '#FBF4EA', 'art': 'shot',
  },
  {
    'key': 'servicerequest', 'name': 'Service Request', 'domain': 'service-request.anvil.app', 'cat': 'business',
    'blurb': 'A neighbourhood bounty board for small paid jobs. Post leaves, snow, junk or moving from $20, pick an offer from someone nearby, get photo proof, and pay them directly with an optional quality bonus.',
    'built': ['Bounty map with 40 kinds of jobs', 'Offers, photo proof and a quality checklist', 'Direct cash or Interac e-Transfer, plus a quality bonus'],
    'tags': ['Marketplace', 'Maps', 'Two-sided'], 'color': '#C2410C', 'bg': '#F4F2EC', 'art': 'shot',
  },
  {
    'key': 'betterthanmarketplace', 'name': 'Better Than Marketplace', 'domain': 'bettermart.anvil.app', 'cat': 'business',
    'blurb': "Sell what you don't need in thirty seconds. Snap a photo, give it a name, and it's listed for neighbours nearby: no categories, no forms and no fees, with chat, saved items and reserved or sold in one tap.",
    'built': ['Photo-first listing in about 30 seconds', 'Items sorted by distance from you', 'Buyer and seller chat, favourites and reserved or sold'],
    'tags': ['Marketplace', 'Mobile-first', 'Maps'], 'color': '#FF5A36', 'bg': '#FFF7EC', 'art': 'shot',
  },
  {
    'key': 'sheetsmith', 'name': 'Sheetsmith', 'domain': 'sheetsmith.anvil.app', 'cat': 'tools',
    'blurb': 'Turns an Excel workbook into a web app. Upload the file with its tables, formulas, validation rules and VBA macros, adjust the app in a studio, and download a one-file Python server the whole office can share over Wi-Fi.',
    'built': ['Formula engine and VBA runtime written from scratch', 'Studio with a live preview of the generated app', 'One-file Python server for the local network, no cloud needed'],
    'tags': ['Code generator', 'Spreadsheets', 'Automation'], 'color': '#1D7A4F', 'bg': '#F3F5F0', 'art': 'shot',
  },
  {
    'key': 'reelstuber', 'name': 'Reelstuber', 'domain': 'reelstuber.anvil.app', 'cat': 'tools',
    'blurb': 'One long video in, a week of reels out. Reelstuber finds the best moments, reframes them to 9:16, adds word-by-word captions and exports MP4s, all inside the browser, so the video is never uploaded.',
    'built': ['Moment finder that listens for peaks, pauses and scene changes', 'On-device speech-to-text captions with Whisper', 'Canvas editor and MP4 export, with nothing uploaded'],
    'tags': ['Video', 'On-device AI', 'Creative tools'], 'color': '#FF3D8B', 'bg': '#FFF7EC', 'art': 'shot',
  },
  {
    'key': 'videoblogbuddy', 'name': 'VideoBlog Buddy', 'domain': 'videoblog-buddy.anvil.app', 'cat': 'tools',
    'blurb': 'Record, edit and publish videos about what you build. Capture your screen and camera, trim pauses, zoom on clicks, add captions and music, then get a thumbnail, chapters and a direct YouTube upload, while recordings stay on your computer.',
    'built': ['Screen and camera recorder in the browser', 'Editor with pause removal, click zooms, captions and vertical layouts', 'Thumbnail, chapters, tags and direct YouTube upload'],
    'tags': ['Video', 'Creative tools', 'YouTube'], 'color': '#CC181E', 'bg': '#F1F1F1', 'art': 'shot',
  },
  {
    'key': 'imgnovella', 'name': 'ImgNovella', 'domain': 'imgnovella.anvil.app', 'cat': 'tools',
    'blurb': 'A visual novel maker with no scripting. Build branching stories with characters, expressions, choices and multiple endings, then share a link or download a standalone game to sell on itch.io.',
    'built': ['Scene editor with characters, choices, variables and conditions', 'Reader with saves, rollback, history and an endings gallery', 'Export to a standalone HTML game, plus ten mini-games'],
    'tags': ['Creative tools', 'Game', 'No-code'], 'color': '#FF4F8B', 'bg': '#FFF5F8', 'art': 'shot',
  },
  {
    'key': 'fillfox', 'name': 'Fillfox', 'domain': 'fillfox.anvil.app', 'cat': 'tools',
    'blurb': 'A free form builder you write like a document. Share one link or embed it, and see every answer plus exactly where people stopped, with logic, quizzes, signatures and teammates included at no cost.',
    'built': ['Document-style form editor with logic and quizzes', 'Drop-off by question and unfinished answers', 'Embeds, teammates, auto-deletion and answer copies by email'],
    'tags': ['Forms', 'Analytics', 'Productivity'], 'color': '#FF4F1F', 'bg': '#FFFFFF', 'art': 'shot',
  },
  {
    'key': 'hookline', 'name': 'Hookline', 'domain': 'hookline.anvil.app', 'cat': 'tools',
    'blurb': 'A free LinkedIn writing studio. Write in your own voice, get the hook past the see-more fold, plan a calm posting rhythm and learn from your own analytics, with optional AI on your own key.',
    'built': ['Hook checker for the see-more fold', 'Calendar and posting through the official API', 'Analytics from your export, plus optional bring-your-own-key AI'],
    'tags': ['Marketing', 'Social', 'AI'], 'color': '#C9A227', 'bg': '#F5F7FA', 'art': 'shot',
  },
  {
    'key': 'marguru', 'name': 'Marguru', 'domain': 'marguru.anvil.app', 'cat': 'tools',
    'blurb': 'Market your business the way an ad agency would. Describe the business in three minutes and get 25 to 35 copy-ready AI prompts, filled in and ordered stage by stage, from strategy and Google Maps to ads, content and measurement.',
    'built': ['Playbook of prompts across eight agency stages', 'Plain-words field guide to what agencies do and charge', 'Ad maths calculator and a wins board for owners'],
    'tags': ['Marketing', 'Prompt playbooks', 'Small business'], 'color': '#C93A20', 'bg': '#F6F1E7', 'art': 'shot',
  },
  {
    'key': 'favesbuddy', 'name': 'Faves Buddy', 'domain': 'faves-buddy.anvil.app', 'cat': 'tools',
    'blurb': "One home for the tabs, pins and screenshots you mean to come back to. Faves Buddy sorts them for you without AI, puts places on a map with what's open now, and finds more you will love.",
    'built': ['Rule-based sorting with a small learner, no AI', 'Map of saved places with open now', 'Chrome extension, phone share target and shareable lists'],
    'tags': ['Productivity', 'Maps', 'Browser extension'], 'color': '#5B5BF0', 'bg': '#F3F5FA', 'art': 'shot',
  },
  {
    'key': 'perfectcast', 'name': 'PerfectCast', 'domain': 'perfectcast.anvil.app', 'cat': 'tools',
    'blurb': "Fan-casting for romantasy readers. Every new book is listed with its characters, tropes and spice level; fans build celebrity collages for each role, swoon over each other's picks, and every character shows the fandom's favourite.",
    'built': ['Book pages with characters, tropes and spice levels', 'Collage maker for dream casts', 'Swoons, comments and a fandom pick for every character'],
    'tags': ['Community', 'Books', 'Social'], 'color': '#C026D3', 'bg': '#FBF2F6', 'art': 'shot',
  },
  {
    'key': 'makeyourownclothes', 'name': 'Make Your Own Clothes', 'domain': 'make-my-clothes.anvil.app', 'cat': 'tools',
    'blurb': "A tailor's shop for making your own clothes. It drafts real sewing patterns from your measurements, lets you redraw them, sews the pieces in 3D on a mannequin your size and writes a step-by-step making book.",
    'built': ['Made-to-measure pattern drafting and a redraw table', '3D cloth simulation on a mannequin built from your measurements', 'Fabric guide and a step-by-step making book'],
    'tags': ['3D', 'DIY', 'Simulations'], 'color': '#1F4D3A', 'bg': '#F3EEE3', 'art': 'shot',
  },
  {
    'key': 'robopresence', 'name': 'Robo Presence', 'domain': 'robo-presence.anvil.app', 'cat': 'tools',
    'blurb': 'Build a camera robot and drive it from any browser. Use a Raspberry Pi, an Arduino or an old phone, install it with one command, and steer with live peer-to-peer video, a joystick and a pan-tilt head.',
    'built': ['Parts builder and one-command installer', 'WebRTC cockpit with live video and controls', 'A simulator to practise driving before you build'],
    'tags': ['Robotics', 'Live video', 'Hardware'], 'color': '#E2611E', 'bg': '#ECE6D6', 'art': 'shot',
  },
  {
    'key': 'battletracker', 'name': 'Battle Tracker', 'domain': 'battletracker.anvil.app', 'cat': 'tools',
    'blurb': 'Every exercise feed on one live map. Battle Tracker reads NATO and common formats, from STANAG 4607 radar tracks and Cursor on Target to KML and AIS, and draws them in standard military symbols with trails and a replay timeline, for training and simulation data.',
    'built': ['Parsers for STANAG 4607, 4609, 4545 and 4676, CoT, NFFI, KML and AIS', 'MIL-STD-2525 and APP-6 symbols on a live map', 'Tracks, sensor footprints and a replay timeline'],
    'tags': ['Maps', 'Data feeds', 'Defence training'], 'color': '#FF7A2F', 'bg': '#E4E7EA', 'art': 'shot',
  },
  {
    'key': 'csuitecoach', 'name': 'C-Suite Coach', 'domain': 'csuite-coach.anvil.app', 'cat': 'learn',
    'blurb': 'Executive training for current and future C-suite leaders. Members study 24 real business cases, drill with spaced repetition, practise boardroom decisions in written challenges and earn certificates with public verification codes.',
    'built': ['Seven programs and a casebook of 24 sourced cases', 'Spaced-repetition drills and rubric-scored challenges', 'Final exams and verifiable certificates'],
    'tags': ['EdTech', 'Coaching', 'Certification'], 'color': '#B08D57', 'bg': '#F7F4EC', 'art': 'shot',
  },
  {
    'key': 'osinty', 'name': 'Osinty', 'domain': 'osinty.anvil.app', 'cat': 'learn',
    'blurb': "An open-source intelligence academy for private investigators. Twenty-four lessons in a noir detective's office, six fictional case files worked in a simulated search terminal, and a corkboard casebook of your own.",
    'built': ['24 lessons with quizzes in 8 modules', 'Interactive case files with a simulated search terminal', 'Corkboard casebook and a field kit of real tools'],
    'tags': ['EdTech', 'Simulations', 'Investigation'], 'color': '#C0392F', 'bg': '#ECE3D0', 'art': 'shot',
  },
  {
    'key': 'businessbuddy', 'name': 'Business Buddy', 'domain': 'business-buddy.anvil.app', 'cat': 'learn',
    'blurb': 'How to open a small business in Montréal, step by step. Guides for barbers, bakeries, cleaning services, food trucks and more cover permits, boroughs, taxes, real costs and the money maths, and members turn a guide into their own launch plan.',
    'built': ['Guides for one- and two-person businesses, with official sources', 'Permit, tax and cost breakdowns by kind of business', 'Private launch plan with a checklist, budget and opening date'],
    'tags': ['Reference', 'Small business', 'Planning'], 'color': '#1F7A6B', 'bg': '#FBF6EE', 'art': 'shot',
  },
  {
    'key': 'jevbuddy', 'name': 'Jev Buddy', 'domain': 'jev-buddy.anvil.app', 'cat': 'learn',
    'blurb': 'A friendly developer guide to an AI decision model. It explains typed questions and calibrated answers with code examples, twelve business use cases, a live playground and a cost calculator.',
    'built': ['Multipage guide with Python, TypeScript and curl examples', 'Playground with saved recipes and live runs', 'Use-case library with routing code and cost maths'],
    'tags': ['Developer docs', 'AI', 'Reference'], 'color': '#0A101D', 'bg': '#F6F8FB', 'art': 'shot',
  },
  {
    'key': 'taichiplease', 'name': 'Tai Chi Please', 'domain': 'tai-chi-please.anvil.app', 'cat': 'learn',
    'blurb': 'Gentle morning tai chi with a 3D teacher. Guided tai chi, qigong and lymph self-massage sessions in a bamboo forest, a path through the 24-step form and a practice journal, with no sign-up needed to start.',
    'built': ['Animated 3D teacher you can orbit, mirror and slow down', 'Guided sessions and a learning path through the 24-step form', 'Practice journal and streaks synced across devices'],
    'tags': ['Fitness', 'Animation', 'Wellness'], 'color': '#2E6A44', 'bg': '#F2F0E4', 'art': 'shot',
  },
  {
    'key': 'brainmechanic', 'name': 'Brain Mechanic', 'domain': 'brain-mechanic.anvil.app', 'cat': 'learn',
    'blurb': "An owner's manual for the mind, written like a car repair guide. Look up what you're going through in plain words, run free self-checks, and explore how upbringing wires people, with 41 tools to work on it. For reflection, not medical advice.",
    'built': ['Plain-words lookups and warning-light checklists', 'Four published screeners and clearly labelled pattern checks', 'Toolbox of 41 techniques with live breathing pacers'],
    'tags': ['Wellness', 'Reference', 'Self-checks'], 'color': '#A8792F', 'bg': '#F2EADC', 'art': 'shot',
  },
  {
    'key': 'littleherobooks', 'name': 'Little Hero Books', 'domain': 'littleheroapp.com', 'cat': 'learn',
    'blurb': 'Picture books that star your child. Parents design a cartoon look-alike, pick one of twelve classic fairy tales retold for ages 3 to 6, and the child is drawn into every page, ready to read aloud, colour in, repaint in six art styles or download as a print-ready PDF.',
    'built': ['Hero studio for a cartoon look-alike', 'Twelve public-domain tales with scenes drawn in code', 'Reader with read-aloud, colouring, painting and print-ready PDFs'],
    'tags': ['Kids', 'Books', 'PDF'], 'color': '#EF5A36', 'bg': '#FFF8EC', 'art': 'shot',
  },
  {
    'key': 'cityfuntime', 'name': 'City Fun Time', 'domain': 'city-fun-time.anvil.app', 'cat': 'games',
    'blurb': 'A life-sim game played on your real streets. Type your address and your neighbourhood is rebuilt in 3D from the map, then work your way up from $20 and a couch to friends, love, fifteen businesses and every block, across 153 missions.',
    'built': ['3D neighbourhood built live from OpenStreetMap', '153 missions at real places near the player', 'Shops, rides, homes, businesses, turf and a family'],
    'tags': ['3D', 'Game', 'Maps'], 'color': '#774CA0', 'bg': '#FFF6E9', 'art': 'shot',
  },
  {
    'key': 'mafiacamp', 'name': 'Mafia Camp', 'domain': 'mafia-camp-game.anvil.app', 'cat': 'games',
    'blurb': 'Mafia on a video call, for three to ten friends. Everyone joins from the browser with no account, gets a secret role at Camp Moonlake, and the call follows the game: at night only the Mafia can see and hear each other.',
    'built': ['Ten-way video call, peer to peer in the browser', 'Secret roles, night moves and day votes run by the server', 'Private night channels and a ghost chat for players who are out'],
    'tags': ['Game', 'Live video', 'Multiplayer'], 'color': '#FF8A3D', 'bg': '#0D1530', 'art': 'shot',
  },
  # Added 2026-11-08: Humbeat, CarChoice, PhotoHunt, Campfire, VRtoToon (screenshots from the App Board).
  {
    'key': 'humbeat', 'name': 'Humbeat', 'domain': 'humbeat.anvil.app', 'cat': 'tools',
    'blurb': 'Hum a tune and it becomes a song. Pick one of 18 styles from hopecore to heavy metal for a full arrangement, record your voice with auto-tune, and turn a hummed melody into any of 26 instruments, all in the browser.',
    'built': ['18 styles with full arrangements', 'Voice recording with auto-tune, harmonies and effects on the device', 'Hum-to-notes and beatbox-to-drums, with WAV and MIDI export'],
    'tags': ['Creative tools', 'Web Audio', 'Voice'], 'color': '#C40E54', 'bg': '#FBEFF3', 'art': 'shot',
  },
  {
    'key': 'carchoice', 'name': 'CarChoice', 'domain': 'carchoice.anvil.app', 'cat': 'tools',
    'blurb': 'Hundreds of cars narrowed down to your five. Filter 268 models from 52 brands by price, power, range, cargo, seats and towing, compare a shortlist side by side, then search the marketplaces and check whether a listing is priced fairly.',
    'built': ['268 models in one sortable table with 44 filters', 'A shortlist of five, compared side by side', 'Marketplace searches in six regions with a fair-price check'],
    'tags': ['Reference', 'Analytics', 'No account needed'], 'color': '#1F5F8B', 'bg': '#F4F5F2', 'art': 'shot',
  },
  {
    'key': 'photohunt', 'name': 'PhotoHunt', 'domain': 'photohunt.anvil.app', 'cat': 'games',
    'blurb': 'A birthday photo treasure hunt, set up in five minutes. Snap things around the house, the kids join by scanning a QR code and race to find and photograph them, with voice riddles, 100 party tasks and photo bingo for the little ones.',
    'built': ['Photo hunts, voice riddles, party tasks and photo bingo', 'Kids join with a QR code, with no app or account', 'Photo matching with a grown-up check, a live board and a party album'],
    'tags': ['Kids', 'Family', 'Image processing'], 'color': '#C2255C', 'bg': '#FFF4F6', 'art': 'shot',
  },
  {
    'key': 'campfire', 'name': 'Campfire', 'domain': 'campfire.anvil.app', 'cat': 'games',
    'blurb': 'A campfire that never burns the same way twice. The flames come from a live fluid simulation, logs dry, char and fall in, and every crackle is made on the spot, across three campsites with their own night sounds and a sleep timer.',
    'built': ['Live GPU fluid-simulated flames, never a loop', 'Nine woods that dry, catch, char and fall in', 'Crackles made live, three campsites and a sleep timer'],
    'tags': ['GPU pipeline', 'Web Audio', 'No account needed'], 'color': '#A8461A', 'bg': '#F3E7DA', 'art': 'shot',
  },
  {
    'key': 'vrtotoon', 'name': 'VRtoToon', 'domain': 'vrtotoon.anvil.app', 'cat': 'vr',
    'blurb': 'A cartoon studio where one actor plays every role. Perform each character yourself in a VR headset or with the mouse, direct the takes on your computer, and export video, subtitles or a Blender kit.',
    'built': ['25 toon characters with lip sync from your voice, in VR or as a desk puppet', 'A script-driven timeline with an auto-director and 10 sets', 'Export to 1080p or vertical video, subtitles and Blender'],
    'tags': ['VR', 'Animation', 'Creative tools'], 'color': '#B3182B', 'bg': '#F7F1E6', 'art': 'shot',
  },
  {
    'key': 'aiexpert', 'name': 'AI Expert', 'domain': 'aiexpert.anvil.app', 'cat': 'learn',
    'blurb': 'Free training for engineers who build AI that holds up in production. Seven programs cover context engineering, production RAG, agents, evals, security and LLMOps, with 252 drills, hands-on labs, 18 real incident files and certificates anyone can verify.',
    'built': ['Seven programs, 28 modules and 252 drills', 'Labs for token costs, chunking, hybrid retrieval and judge calibration', 'Certificates with public verification codes'],
    'tags': ['EdTech', 'AI', 'Certification'], 'color': '#0B6E5B', 'bg': '#F6F7F9', 'art': 'shot',
  },
  {
    'key': 'productexpert', 'name': 'Product Expert', 'domain': 'productexpert.anvil.app', 'cat': 'learn',
    'blurb': 'Free training for product managers ready to lead product. Eight programs cover strategy, discovery and experiments, metrics and pricing, the P&L, org design, executive influence and AI products, with 288 drills, in-browser labs, 22 real case files and certificates anyone can verify.',
    'built': ['Eight programs, 32 modules and 288 drills', 'Labs for experiment peeking, metric trees, cohorts and pricing', '22 sourced product leadership case files'],
    'tags': ['EdTech', 'Product leadership', 'Certification'], 'color': '#2340A8', 'bg': '#F4F5F7', 'art': 'shot',
  },
]

# One-minute films on the Addanapp YouTube channel (youtube.com/@addanapp); ids from APP_MAKER/youtube/manifest.json.
# Battle Tracker has none yet. Parapeet's is a before/after film of a rebuild (also in the YouTube section, content.py).
VIDEOS = {
  'parapeet': 'FW-j_xL_DWo',
  'citycrossers': 'iIDuAWF-BzI',
  'planplate': '4KcdhVtqgNQ',
  'prepsto': 'CehQC_0r93A',
  'vitalrpa': 'W0yKLujjtPk',
  'arvistay': '2Gm5T_OHFl0',
  'subsudo': 'ECTqEf17FOg',
  'quickybricks': '7AX1pujnTy0',
  'toonyloony': 'mfsUukKdXQY',
  'planfriday': 'd7Gj5GCfeOc',
  'topameal': 'Eex4sJbZDNg',
  'oscreenplay': 'niJntt5oVNU',
  'yabanana': 'TwZemZxbquE',
  'logsteps': 'tLUZzG1_Jz0',
  'robointern': '-ZsVXlSr6tI',
  'monshop': '7hR4RnsYm2M',
  'adorablescience': 'eoGeoGcAmg8',
  'funtoplan': 'qWP3bxxPTWE',
  'busybun': 'mFIuuENN_nI',
  'doremiroad': 'RXNcbqR-jRs',
  'snackpuncher': 'YsGjeRjVZMY',
  'walltracer': 'TavbKRtrFuw',
  'mrbigstage': 'UuQabze-btg',
  'poundfighter': 'X7OTOzRsGy8',
  'healthbooker': '4BjAXdLkvMY',
  'autoagile': 'iJ6mNTshQPg',
  'goodlandlord': 'qv8jRRY0KG0',
  'servicerequest': '_Qj7nniw9cw',
  'betterthanmarketplace': 'X374nwXR8Qs',
  'sheetsmith': 'KvFAg0fOglU',
  'reelstuber': 'pjALr5WpIvM',
  'videoblogbuddy': 'Olt2yMqA_TI',
  'imgnovella': 'TV4J74A9QkE',
  'fillfox': '1T24l_1OT_k',
  'hookline': 'rgkcyhKM1T8',
  'marguru': 'bTpH6t4KN2o',
  'favesbuddy': 'LKq6NHGjgdc',
  'perfectcast': '_pmaxTfTg38',
  'makeyourownclothes': 'KHZVGQ4Py7M',
  'robopresence': '-c7CiXm_WjE',
  'csuitecoach': 'Z5MC3w_B89A',
  'osinty': '3AZprKF2iH0',
  'businessbuddy': 'Yw346NsYCr0',
  'jevbuddy': 'pGgzeKsxuk0',
  'taichiplease': 'arxqoGf9PlM',
  'brainmechanic': '5BWx9DjbcDs',
  'littleherobooks': 'lpY_f2LUTdI',
  'cityfuntime': '-Eenu0iTZXI',
  'mafiacamp': 'gDPcBrwAhtI',
  'humbeat': 'YKVGdvY_VAk',
  'photohunt': 'FHK7txELJ58',
  'vrtotoon': 'wXfPmsZW_tA',
  'aiexpert': 'bZcM4sIz4kQ',
  'productexpert': 'wPLbvs9qoKU',
}

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


def _pin(x, y, color, big=False):
  s = 1.3 if big else 1
  return (f'<g transform="translate({x} {y}) scale({s})"><path d="M0 0c-6-8-9-12-9-16a9 9 0 0 1 18 0c0 4-3 8-9 16z" fill="{color}"/>'
          f'<circle cx="0" cy="-16" r="3.4" fill="#fff"/></g>')


def art_monshop(p):
  c = p['color']
  pins = (_pin(80, 120, '#E8A33D') + _pin(118, 196, '#0E9F6E') + _pin(196, 210, '#D9487A') + _pin(228, 128, '#7A5CFA') +
          _pin(70, 214, c) + _pin(150, 140, c, True))
  feed = ''
  items = [('#E8A33D', 'Boulangerie', 58, '2 min'), ('#0E9F6E', 'Fruiterie', 46, '9 min'), ('#D9487A', 'Fleuriste', 52, '1 h')]
  for i, (col, name, w, t) in enumerate(items):
    y = 78 + i * 52
    feed += (f'<rect x="262" y="{y}" width="100" height="44" rx="8" fill="#fff" stroke="#E4EAF2"/>'
             f'<rect x="270" y="{y + 8}" width="14" height="14" rx="4" fill="{col}"/>'
             f'<text x="289" y="{y + 18}" font-size="6.5" font-weight="700" fill="#182031" {FONT}>{name}</text>'
             f'<text x="354" y="{y + 18}" text-anchor="end" font-size="5.5" fill="#8C94A3" {FONT}>{t}</text>'
             f'<rect x="270" y="{y + 28}" width="{w + 20}" height="4.5" rx="2.25" fill="#C5C9D3"/>'
             f'<rect x="270" y="{y + 36}" width="{w}" height="4.5" rx="2.25" fill="#DDE1E8"/>')
  inner = f'''<rect x="28" y="42" width="226" height="216" fill="#EEF2F6"/>
  <g stroke="#fff" stroke-width="8" stroke-linecap="round" fill="none"><path d="M20 150 L260 120"/><path d="M90 40 L120 260"/><path d="M190 40 L176 260"/></g>
  <g stroke="#fff" stroke-width="3.5" stroke-linecap="round" fill="none"><path d="M20 210 L260 196"/><path d="M20 90 L260 70"/><path d="M140 40 L150 260"/></g>
  <path d="M28 246 C 80 226, 130 250, 254 222" stroke="#C6DDF4" stroke-width="12" fill="none"/>
  <ellipse cx="60" cy="168" rx="22" ry="13" fill="#D5EBDD"/>
  {pins}
  <g transform="translate(150 92)"><rect x="-58" y="-26" width="116" height="34" rx="9" fill="#fff" stroke="#DCE5F0"/>
    <path d="M-6 8 L0 15 L6 8z" fill="#fff"/>
    <text x="-48" y="-12" font-size="6.8" font-weight="700" fill="#182031" {FONT}>Fresh croissants, out now!</text>
    <text x="-48" y="-2" font-size="5.8" fill="#8C94A3" {FONT}>Boulangerie du Coin · 120 m</text></g>
  <g transform="translate(40 232)"><rect width="104" height="16" rx="8" fill="#fff" stroke="#DCE5F0"/>
    <rect x="2" y="2" width="52" height="12" rx="6" fill="{c}"/>
    <text x="28" y="10.4" text-anchor="middle" font-size="6" font-weight="700" fill="#fff" {FONT}>Shoppers</text>
    <text x="79" y="10.4" text-anchor="middle" font-size="6" font-weight="600" fill="#5D6778" {FONT}>Vendors</text></g>
  <text x="262" y="64" font-size="7" font-weight="800" fill="#182031" {FONT}>Latest updates</text>
  <circle cx="356" cy="61.5" r="3" fill="#0E9F6E"/>
  {feed}'''
  return _browser(inner, 'monshop.ca', p['bg'])


def _brownie(x, y, s=1.0):
  return (f'<g transform="translate({x} {y}) scale({s})"><rect x="-6" y="-5" width="12" height="10" rx="2" fill="#6B3A1F"/>'
          f'<rect x="-6" y="-5" width="12" height="3.4" rx="1.6" fill="#8A4F2B"/>'
          f'<circle cx="-2" cy="1.5" r=".9" fill="#C08A5B"/><circle cx="2.6" cy="2.4" r=".9" fill="#C08A5B"/></g>')


def art_family(p):
  c = p['color']
  people = [('M', '#D9487A'), ('D', '#2F5BFF'), ('L', '#0E9F6E'), ('S', '#E8A33D')]
  avs = ''
  for i, (ini, col) in enumerate(people):
    x = 60 + i * 26
    avs += (f'<circle cx="{x}" cy="88" r="10" fill="{col}"/>'
            f'<text x="{x}" y="91" text-anchor="middle" font-size="8" font-weight="700" fill="#fff" {FONT}>{ini}</text>')
  tasks = [('Empty the dishwasher', 1, '#0E9F6E', 20), ('Walk the dog', 1, '#E8A33D', 15),
           ('Homework: fractions', 0, '#0E9F6E', 30), ('Tidy bedroom', 0, '#2F5BFF', 25)]
  rows = ''
  for i, (t, done, col, pts) in enumerate(tasks):
    y = 110 + i * 32
    box = (f'<rect x="56" y="{y + 7}" width="12" height="12" rx="3.5" fill="{c}"/><path d="M59 {y + 13} l2.4 2.4 4.2-4.6" stroke="#fff" stroke-width="1.5" fill="none"/>'
           if done else f'<rect x="56" y="{y + 7}" width="12" height="12" rx="3.5" fill="#fff" stroke="#D4C7BA" stroke-width="1.3"/>')
    rows += (f'<rect x="46" y="{y}" width="196" height="26" rx="7" fill="#fff" stroke="#EFE5DA"/>{box}'
             f'<text x="76" y="{y + 16.5}" font-size="7" fill="{"#8C94A3" if done else "#182031"}" {FONT}>{t}</text>'
             f'<circle cx="208" cy="{y + 13}" r="5.5" fill="{col}"/>'
             f'<rect x="216" y="{y + 7}" width="22" height="12" rx="6" fill="#FBF1E6"/>'
             f'<text x="227" y="{y + 15.4}" text-anchor="middle" font-size="6" font-weight="700" fill="{c}" {FONT}>+{pts}</text>')
  board = ''
  for i, (ini, col, w, n) in enumerate([('L', '#0E9F6E', 70, 6), ('S', '#E8A33D', 54, 4), ('D', '#2F5BFF', 36, 3), ('M', '#D9487A', 22, 2)]):
    y = 104 + i * 26
    board += (f'<circle cx="270" cy="{y}" r="7" fill="{col}"/><text x="270" y="{y + 2.4}" text-anchor="middle" font-size="6.5" font-weight="700" fill="#fff" {FONT}>{ini}</text>'
              f'<rect x="282" y="{y - 4}" width="{w}" height="8" rx="4" fill="{col}" opacity=".85"/>')
  inner = f'''<rect x="28" y="42" width="344" height="216" fill="#FFFCF8"/>
  <text x="46" y="68" font-size="10" font-weight="800" fill="#182031" {FONT}>Family board</text>
  <g transform="translate(150 57)"><rect width="88" height="16" rx="8" fill="{c}"/>{_brownie(12, 8, .8)}
    <text x="52" y="11" text-anchor="middle" font-size="7" font-weight="800" fill="#fff" {FONT}>340 brownie pts</text></g>
  {avs}
  <rect x="160" y="80" width="82" height="16" rx="8" fill="#fff" stroke="#EFE5DA"/>
  <text x="201" y="90.6" text-anchor="middle" font-size="6.5" font-weight="600" fill="#5D6778" {FONT}>+ Add a task</text>
  {rows}
  <rect x="256" y="56" width="104" height="186" rx="10" fill="#fff" stroke="#EFE5DA"/>
  <text x="266" y="76" font-size="7.5" font-weight="800" fill="#182031" {FONT}>This week</text>
  {_brownie(346, 73, .9)}
  {board}
  <rect x="266" y="210" width="84" height="20" rx="10" fill="{p['bg']}"/>
  <text x="308" y="222.6" text-anchor="middle" font-size="6.5" font-weight="700" fill="{c}" {FONT}>Reward: movie night</text>'''
  return _browser(inner, 'funtoplan.com', p['bg'])


MONO = "font-family=\"'Courier Prime', 'Courier New', Courier, monospace\""


def art_screenplay(p):
  c, gold, night = p['color'], '#B7811A', '#17140F'
  tabs = ''
  for i, name in enumerate(['Overview', 'Cast', 'Web', 'Chronology', 'Storyline', 'Pages']):
    y = 80 + i * 22
    on = name == 'Pages'
    if on:
      tabs += f'<rect x="36" y="{y - 11}" width="64" height="16" rx="5" fill="{c}"/>'
    tabs += f'<text x="44" y="{y}" font-size="6.6" font-weight="{"700" if on else "500"}" fill="{"#fff" if on else "#AEA493"}" {FONT}>{name}</text>'
  bars = ''.join(f'<rect x="{x}" y="{y}" width="{w}" height="4" rx="2" fill="#C9C1B2"/>'
                 for x, y, w in [(132, 80, 118), (132, 88, 110), (132, 96, 64),
                                 (156, 142, 70), (162, 150, 58), (132, 166, 116), (132, 174, 92)])
  # The 8-step Story Circle: spoke ends and step dots on a radius-30 circle around (317, 108).
  spokes = ''.join(f'<line x1="317" y1="108" x2="{x}" y2="{y}" stroke="#DDD4C3" stroke-width="1"/>'
                   for x, y in [(317, 78), (338.2, 86.8), (347, 108), (338.2, 129.2),
                                (317, 138), (295.8, 129.2), (287, 108), (295.8, 86.8)])
  dots = ''
  for i, (x, y) in enumerate([(328.5, 80.3), (344.7, 96.5), (344.7, 119.5), (328.5, 135.7),
                              (305.5, 135.7), (289.3, 119.5), (289.3, 96.5), (305.5, 80.3)]):
    here = i == 4
    dots += (f'<circle cx="{x}" cy="{y}" r="{4.2 if here else 3}" '
             f'fill="{c if here else (night if i < 4 else "#fff")}" stroke="{night}" stroke-width="1"/>')
  inner = f'''<rect x="28" y="42" width="80" height="216" fill="{night}"/>
  <rect x="38" y="51" width="12" height="12" rx="3" fill="#EFE8DA"/><circle cx="44" cy="57" r="2.4" fill="{c}"/>
  <text x="55" y="60" font-size="6.8" font-weight="800" fill="#EFE8DA" {FONT}>Salt Debt</text>
  {tabs}
  <rect x="120" y="50" width="142" height="208" fill="#FFFDF6" stroke="#E6DECF"/>
  <text x="132" y="70" font-size="6.2" font-weight="700" fill="#1B1813" {MONO}>INT. PROJECTION BOOTH - NIGHT</text>
  <text x="191" y="116" text-anchor="middle" font-size="6.4" font-weight="700" fill="#1B1813" {MONO}>MARA</text>
  <text x="191" y="125" text-anchor="middle" font-size="5.6" fill="#5F574A" {MONO}>(barely a whisper)</text>
  <text x="191" y="135" text-anchor="middle" font-size="6.2" fill="#1B1813" {MONO}>The reel is still warm.</text>
  {bars}
  <text x="250" y="194" text-anchor="end" font-size="6.2" font-weight="700" fill="#1B1813" {MONO}>CUT TO:</text>
  <rect x="132" y="206" width="1.6" height="9" fill="{c}"/>
  <text x="317" y="64" text-anchor="middle" font-size="6.8" font-weight="800" fill="{night}" {FONT}>Story Circle</text>
  <circle cx="317" cy="108" r="30" fill="#F3EEE4" stroke="{night}" stroke-width="1.4"/>
  {spokes}{dots}
  <circle cx="317" cy="108" r="16" fill="#F3EEE4"/>
  <text x="317" y="107" text-anchor="middle" font-size="6" font-weight="700" fill="{c}" {FONT}>5 · Find</text>
  <text x="317" y="115" text-anchor="middle" font-size="5.4" fill="#5F574A" {FONT}>14 scenes</text>
  <rect x="272" y="152" width="90" height="94" rx="8" fill="#fff" stroke="#E6DECF"/>
  <text x="280" y="166" font-size="6.8" font-weight="800" fill="{night}" {FONT}>Script doctor</text>
  <text x="354" y="166" text-anchor="end" font-size="6" font-weight="700" fill="{gold}" {FONT}>82%</text>
  <rect x="280" y="172" width="74" height="4" rx="2" fill="#EBE4D6"/><rect x="280" y="172" width="61" height="4" rx="2" fill="{gold}"/>
  <rect x="280" y="184" width="74" height="22" rx="5" fill="#F8DFE1"/>
  <text x="285" y="194" font-size="5.6" font-weight="700" fill="{c}" {FONT}>No midpoint yet</text>
  <text x="285" y="201.5" font-size="5.2" fill="#5F574A" {FONT}>Act 2 needs a turn</text>
  <rect x="280" y="212" width="74" height="22" rx="5" fill="#E1EFE3"/>
  <text x="285" y="222" font-size="5.6" font-weight="700" fill="#2F7A4F" {FONT}>Setup paid off</text>
  <text x="285" y="229.5" font-size="5.2" fill="#5F574A" {FONT}>The key, scene 12</text>'''
  return _browser(inner, 'oscreenplay.com', p['bg'])


BANANA = 'M45 15C49 35 36 51 13 47C11.5 46.7 11.5 45 13 44.5C28 40 39 31 40.5 16Z'


def art_lyrics(p):
  ink, yel, pink, blue = '#1D1830', '#FFC21A', '#FF3D7F', '#3E5BD8'
  steps = ''
  for i in range(16):
    on = i in (0, 3, 4, 8, 10, 11, 14)
    steps += f'<rect x="{150 + i * 13}" y="60" width="10" height="14" rx="2.5" fill="{pink if i == 8 else (yel if on else "#3A3352")}"/>'
  lines = ''
  for i, (head, end, letter, col, syl) in enumerate([
      ('Late night ink on a paper ', 'plane', 'A', pink, 8),
      ('Every word is a drop of ', 'rain', 'A', pink, 8),
      ('Bass so low that the city ', 'knows', 'B', blue, 8),
      ('Bananas up when the chorus ', 'grows', 'B', blue, 9)]):
    y = 136 + i * 25
    ok = syl == 8
    lines += (f'<circle cx="58" cy="{y - 2.5}" r="6" fill="{col}"/>'
              f'<text x="58" y="{y}" text-anchor="middle" font-size="6.4" font-weight="800" fill="#fff" {FONT}>{letter}</text>'
              f'<text x="70" y="{y}" font-size="7.2" fill="{ink}" {FONT}>{head}<tspan font-weight="800" fill="{col}">{end}</tspan></text>'
              f'<text x="240" y="{y}" text-anchor="end" font-size="6.4" font-weight="700" fill="{"#1F8A5B" if ok else "#A86400"}" {FONT}>{syl}</text>'
              f'<rect x="70" y="{y + 6}" width="{140 if ok else 156}" height="2.5" rx="1.25" fill="{"#BFE6D0" if ok else "#F4D9A6"}"/>')
  chips = ''
  x, y = 270, 128
  for w in ['plane', 'chain', 'lane', 'again', 'champagne', 'remain']:
    cw = 12 + len(w) * 4.3
    if x + cw > 352:
      x, y = 270, y + 16
    chips += (f'<rect x="{round(x, 1)}" y="{y}" width="{round(cw, 1)}" height="12" rx="6" fill="#fff" stroke="{ink}" stroke-width="1"/>'
              f'<text x="{round(x + cw / 2, 1)}" y="{round(y + 8.3, 1)}" text-anchor="middle" font-size="6" font-weight="600" fill="{ink}" {FONT}>{w}</text>')
    x += cw + 4
  inner = f'''<rect x="40" y="52" width="320" height="30" rx="9" fill="{ink}"/>
  <circle cx="58" cy="67" r="9" fill="{yel}"/><path d="M55.5 62.5 L62.5 67 L55.5 71.5Z" fill="{ink}"/>
  <text x="74" y="65" font-size="7" font-weight="800" fill="#fff" {FONT}>Boom bap</text>
  <text x="74" y="74" font-size="6" fill="#B9B3CC" {FONT}>90 BPM · 8 a line</text>
  {steps}
  <rect x="42" y="94" width="210" height="152" rx="10" fill="{ink}"/>
  <rect x="40" y="92" width="210" height="152" rx="10" fill="#fff" stroke="{ink}" stroke-width="1.5"/>
  <rect x="52" y="102" width="42" height="13" rx="6.5" fill="{yel}" stroke="{ink}" stroke-width="1"/>
  <text x="73" y="111" text-anchor="middle" font-size="6" font-weight="800" fill="{ink}" {FONT}>VERSE 1</text>
  <text x="240" y="111" text-anchor="end" font-size="6" font-weight="600" fill="#958FA6" {FONT}>syllables</text>
  {lines}
  <rect x="262" y="94" width="98" height="104" rx="10" fill="{ink}"/>
  <rect x="260" y="92" width="98" height="104" rx="10" fill="#FFE9A6" stroke="{ink}" stroke-width="1.5"/>
  <text x="270" y="107" font-size="6.8" font-weight="800" fill="{ink}" {FONT}>Rhymes for <tspan fill="#C81D5C">rain</tspan></text>
  <text x="270" y="119" font-size="5.6" fill="#5E5872" {FONT}>Tap one to drop it in</text>
  {chips}
  <rect x="262" y="210" width="98" height="36" rx="18" fill="{ink}"/>
  <rect x="260" y="208" width="98" height="36" rx="18" fill="#fff" stroke="{ink}" stroke-width="1.5"/>
  <g transform="translate(268 211) scale(.55)"><path d="{BANANA}" fill="{yel}" stroke="{ink}" stroke-width="2.4"/></g>
  <text x="298" y="224" font-size="8.5" font-weight="800" fill="{ink}" {FONT}>128</text>
  <text x="298" y="233" font-size="5.8" fill="#5E5872" {FONT}>bananas</text>'''
  return _browser(inner, 'yabanana · studio', p['bg'])


def art_rooms(p):
  c, ink = p['color'], '#0B2A2E'

  def fl(u, v, h=0):
    # Isometric room: floor corners left (154,116), back (200,92), front (200,140); walls 40 high.
    return round(154 + u * 46 + v * 46, 1), round(116 - u * 24 + v * 24 - h * 40, 1)
  dots = ''
  for i in range(70):
    a, b = (i * 37 % 97) / 97, (i * 61 % 89) / 89
    if i % 3 == 0:
      x, y = fl(a, 0, b)   # left wall
    elif i % 3 == 1:
      x, y = fl(1, a, b)   # right wall
    else:
      x, y = fl(a, b)      # floor
    col = ['#7FB8BD', '#C9A27A', '#5E8F94', '#E0C9A6'][i % 4]
    dots += f'<circle cx="{x}" cy="{y}" r="1.5" fill="{col}"/>'
  path = ' '.join('%s,%s' % fl(u, v) for u, v in [(.15, .2), (.35, .3), (.55, .25), (.75, .45), (.7, .7), (.45, .8)])
  ex, ey = fl(.45, .8)
  chips = ''
  for i, name in enumerate(['Orbit', 'Walk', 'Plan']):
    x = 150 + i * 36
    on = name == 'Walk'
    chips += (f'<rect x="{x}" y="160" width="32" height="13" rx="6.5" fill="{c if on else "#EEF5F5"}"/>'
              f'<text x="{x + 16}" y="168.8" text-anchor="middle" font-size="6" font-weight="700" fill="{"#fff" if on else ink}" {FONT}>{name}</text>')
  extra = f"""<rect x="34" y="70" width="92" height="62" rx="10" fill="#fff" stroke="#C6E2E4"/>
  <text x="44" y="86" font-size="6.8" font-weight="800" fill="{ink}" {FONT}>New scan</text>
  <text x="44" y="98" font-size="5.8" fill="#5B7478" {FONT}>1,240 frames · Balanced</text>
  <rect x="44" y="106" width="72" height="5" rx="2.5" fill="#E2EEEF"/><rect x="44" y="106" width="60" height="5" rx="2.5" fill="{c}"/>
  <text x="44" y="122" font-size="5.8" font-weight="700" fill="{c}" {FONT}>Building the room · 84%</text>
  <rect x="276" y="120" width="92" height="56" rx="10" fill="#fff" stroke="#C6E2E4"/>
  <circle cx="290" cy="136" r="5" fill="#E8833A"/><circle cx="290" cy="136" r="2" fill="#fff"/>
  <text x="300" y="138.5" font-size="6.8" font-weight="800" fill="{ink}" {FONT}>Sofa</text>
  <text x="286" y="152" font-size="5.8" fill="#5B7478" {FONT}>2.1 m wide, fits</text>
  <text x="286" y="164" font-size="5.8" fill="#5B7478" {FONT}>under the window</text>"""
  inner = f"""<text x="152" y="48" font-size="7.4" font-weight="800" fill="{ink}" {FONT}>Living room</text>
  <text x="248" y="48" text-anchor="end" font-size="5.8" font-weight="700" fill="{c}" {FONT}>3D</text>
  <rect x="148" y="54" width="104" height="98" rx="8" fill="#F2F8F8"/>
  <polygon points="154,116 200,92 200,52 154,76" fill="#E4EFEF"/>
  <polygon points="200,92 246,116 246,76 200,52" fill="#D8E8E9"/>
  <polygon points="154,116 200,92 246,116 200,140" fill="#EAF3F3"/>
  {dots}
  <polyline points="{path}" fill="none" stroke="{c}" stroke-width="1.6" stroke-dasharray="3 2.5" stroke-linecap="round"/>
  <circle cx="{ex}" cy="{ey}" r="3.6" fill="{c}" stroke="#fff" stroke-width="1.2"/>
  <circle cx="214" cy="84" r="3.4" fill="#E8833A" stroke="#fff" stroke-width="1"/>
  {chips}
  <rect x="150" y="180" width="100" height="34" rx="7" fill="#F2F8F8"/>
  <text x="156" y="193" font-size="6" font-weight="700" fill="{ink}" {FONT}>4.2 × 3.6 × 2.5 m</text>
  <text x="156" y="205" font-size="5.6" fill="#5B7478" {FONT}>Floor area 15.1 m²</text>
  <rect x="150" y="222" width="100" height="18" rx="9" fill="{c}"/>
  <text x="200" y="233.5" text-anchor="middle" font-size="6.6" font-weight="800" fill="#fff" {FONT}>Share room</text>"""
  return _phone(inner, p['bg'], extra)


def art_models(p):
  c, ink, paper = p['color'], '#141B2D', '#FBFAF6'
  roles = {'t': '#8A5CC9', 'g': '#C2852B', 'x': '#2F8A63', 'y': '#C8463D'}
  rows = ''
  for i, (name, role, star) in enumerate([('date', 't', 0), ('store_id', 'g', 0), ('promo', 'x', 1),
                                          ('price', 'x', 0), ('sales', 'y', 0)]):
    y = 84 + i * 22
    rows += (f'<rect x="44" y="{y - 10}" width="118" height="17" rx="4" fill="#fff" stroke="#E3E0D6"/>'
             f'<text x="51" y="{y + 1.5}" font-size="6.6" fill="{ink}" {MONO}>{name}</text>'
             + (f'<text x="126" y="{y + 2}" font-size="7" fill="#D9A21B" {FONT}>★</text>' if star else '')
             + f'<rect x="138" y="{y - 6}" width="18" height="10" rx="3" fill="{roles[role]}"/>'
             f'<text x="147" y="{y + 1.2}" text-anchor="middle" font-size="6.2" font-weight="800" fill="#fff" {FONT}>{role}</text>')
  bars = ''
  for i, (name, score) in enumerate([('LightGBM', 87), ('Prophet', 74), ('Ridge', 61), ('ARIMA', 58)]):
    y = 88 + i * 15
    top = i == 0
    bars += (f'<text x="186" y="{y}" font-size="6.2" font-weight="{"800" if top else "500"}" fill="{ink}" {FONT}>{i + 1}. {name}</text>'
             f'<rect x="246" y="{y - 5}" width="90" height="5" rx="2.5" fill="#E8E6DE"/>'
             f'<rect x="246" y="{y - 5}" width="{round(score * .9, 1)}" height="5" rx="2.5" fill="{c if top else "#A9B4CF"}"/>'
             f'<text x="356" y="{y}" text-anchor="end" font-size="6" font-weight="700" fill="{c if top else "#6B7280"}" {FONT}>{score}</text>')
  code = ''
  lines = [('model = LGBMRegressor(', '#E6E9F2'), ('    n_estimators=400,', '#9FD0B4'),
           ('    learning_rate=0.05)', '#9FD0B4'), ('model.fit(X_train, y_train)', '#E6E9F2')]
  for i, (txt, col) in enumerate(lines):
    code += f'<text x="190" y="{204 + i * 10}" font-size="6" fill="{col}" xml:space="preserve" {MONO}>{txt}</text>'
  inner = f"""<rect x="28" y="42" width="344" height="216" fill="{paper}"/>
  <text x="44" y="62" font-size="7" font-weight="800" fill="{ink}" {FONT}>§1 Your columns</text>
  <text x="44" y="71" font-size="5.6" fill="#6B7280" {FONT}>Forecast · weekly · 8 ahead</text>
  {rows}
  <text x="44" y="210" font-size="6" fill="#4B5563" {FONT}>D = (t, g, x) → y</text>
  <text x="44" y="222" font-size="5.6" fill="#6B7280" {FONT}>12,400 rows · 40 series</text>
  <rect x="178" y="52" width="184" height="112" rx="8" fill="#fff" stroke="#E3E0D6"/>
  <text x="186" y="66" font-size="7" font-weight="800" fill="{ink}" {FONT}>§4 Ranking</text>
  <text x="354" y="66" text-anchor="end" font-size="5.6" fill="#6B7280" {FONT}>S(m) = 20·wᵀ(p,q,r) + Σδ</text>
  {bars}
  <text x="186" y="154" font-size="5.6" fill="#6B7280" {FONT}>+4 known-ahead promo  ·  −3 short history</text>
  <rect x="178" y="174" width="184" height="76" rx="8" fill="{ink}"/>
  <text x="188" y="188" font-size="6.2" font-weight="800" fill="#fff" {MONO}>train.py</text>
  <text x="236" y="188" font-size="6" fill="#7C869C" {MONO}>predict.py</text>
  <text x="290" y="188" font-size="6" fill="#7C869C" {MONO}>.ipynb</text>
  <rect x="188" y="192" width="38" height="1.4" fill="{c}"/>
  {code}"""
  return _browser(inner, 'robointern · the lab', p['bg'])


def art_feedback(p):
  c, ink, orange = p['color'], '#0C0E14', '#FF5A1F'
  kinds = [('Bug', '#D0342C', '#FDE8E6', 4, 92), ('Idea', c, p['bg'], 5, 118), ('Praise', '#0F8A5F', '#E3F5ED', 5, 80),
           ('Question', '#565D6D', '#F4F5F8', 3, 104)]
  rows = ''
  for i, (kind, col, soft, stars, w) in enumerate(kinds):
    y = 76 + i * 37
    on = i == 1
    kw = 10 + len(kind) * 4.2
    rows += (f'<rect x="40" y="{y}" width="190" height="31" rx="7" fill="#fff" stroke="{c if on else "#E3E6EC"}" stroke-width="{1.4 if on else 1}"/>'
             f'<rect x="48" y="{y + 7}" width="{kw}" height="9" rx="4.5" fill="{soft}"/>'
             f'<text x="{48 + kw / 2}" y="{y + 13.6}" text-anchor="middle" font-size="5.6" font-weight="700" fill="{col}" {FONT}>{kind}</text>'
             f'<text x="222" y="{y + 14}" text-anchor="end" font-size="6.4" fill="#E8A33D" letter-spacing=".5" {FONT}>{"★" * stars}{"☆" * (5 - stars)}</text>'
             f'<rect x="48" y="{y + 21}" width="{w}" height="4.5" rx="2.25" fill="#C5C9D3"/>')
    if i == 0:
      rows += f'<circle cx="{58 + kw}" cy="{y + 11.5}" r="2.6" fill="{orange}"/>'
  crit = ''.join(f'<circle cx="257" cy="{y}" r="3.6" fill="#0F8A5F"/><path d="M255.3 {y} l1.2 1.2 2.2-2.4" stroke="#fff" stroke-width="1" fill="none"/>'
                 f'<rect x="265" y="{y - 2}" width="{w}" height="4" rx="2" fill="#C5C9D3"/>'
                 for y, w in [(146, 74), (157, 62), (168, 80)])
  chips = ''
  x = 252
  for name in ['Jira', 'Gherkin', 'JSON']:
    cw = 10 + len(name) * 4.2
    chips += (f'<rect x="{x}" y="210" width="{cw}" height="11" rx="5.5" fill="#F4F5F8" stroke="#E3E6EC"/>'
              f'<text x="{x + cw / 2}" y="217.6" text-anchor="middle" font-size="5.6" font-weight="600" fill="{ink}" {FONT}>{name}</text>')
    x += cw + 4
  tabs = ''
  x = 98
  for name, n, on in [('Open', 24, 1), ('Planned', 6, 0), ('Done', 41, 0)]:
    tw = 18 + len(name) * 4.2
    tabs += (f'<rect x="{x}" y="52" width="{tw}" height="13" rx="6.5" fill="{c if on else "#fff"}" stroke="{c if on else "#E3E6EC"}"/>'
             f'<text x="{x + 6}" y="60.6" font-size="6" font-weight="600" fill="{"#fff" if on else "#565D6D"}" {FONT}>{name} {n}</text>')
    x += tw + 4
  inner = f'''<rect x="28" y="42" width="344" height="216" fill="#F7F8FB"/>
  <text x="42" y="62" font-size="9" font-weight="800" fill="{ink}" {FONT}>Inbox</text>
  {tabs}{rows}
  <g transform="translate(150 226)"><rect x="1" y="2" width="72" height="20" rx="10" fill="{ink}" opacity=".15"/>
    <rect width="72" height="20" rx="10" fill="{orange}"/>
    <path d="M12 7h10a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2h-6l-3 2.5V15h-1a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2z" fill="#fff"/>
    <text x="30" y="13.2" font-size="6.8" font-weight="700" fill="#fff" {FONT}>Feedback</text></g>
  <rect x="242" y="52" width="120" height="196" rx="9" fill="#fff" stroke="#E3E6EC"/>
  <text x="252" y="66" font-size="5.6" font-weight="700" fill="#8D93A1" letter-spacing=".8" {FONT}>USER STORY · 7 COMMENTS</text>
  <text x="252" y="80" font-size="7.6" font-weight="800" fill="{ink}" {FONT}>Save my cart for later</text>
  <text x="252" y="96" font-size="6" font-weight="700" fill="{c}" {FONT}>As a</text><rect x="276" y="92" width="58" height="4.5" rx="2.25" fill="#C5C9D3"/>
  <text x="252" y="108" font-size="6" font-weight="700" fill="{c}" {FONT}>I want</text><rect x="276" y="104" width="76" height="4.5" rx="2.25" fill="#C5C9D3"/>
  <text x="252" y="120" font-size="6" font-weight="700" fill="{c}" {FONT}>So that</text><rect x="280" y="116" width="66" height="4.5" rx="2.25" fill="#C5C9D3"/>
  <text x="252" y="136" font-size="5.6" font-weight="700" fill="#8D93A1" letter-spacing=".8" {FONT}>ACCEPTANCE</text>
  {crit}
  <rect x="252" y="178" width="100" height="22" rx="6" fill="{p['bg']}"/>
  <text x="257" y="190" font-size="12" font-weight="800" fill="{c}" font-family="Georgia, serif">&#8220;</text>
  <rect x="268" y="184" width="76" height="4" rx="2" fill="{c}" opacity=".35"/><rect x="268" y="192" width="52" height="4" rx="2" fill="{c}" opacity=".35"/>
  {chips}
  <rect x="252" y="228" width="100" height="14" rx="7" fill="{c}"/>
  <text x="302" y="237.4" text-anchor="middle" font-size="6.4" font-weight="700" fill="#fff" {FONT}>Export story</text>'''
  return _browser(inner, 'app.prepsto.com', p['bg'])


def art_boxing(p):
  c, gold, ink, cream = p['color'], '#B07A1F', '#1C1A18', '#F3ECE0'
  arc = 2 * 3.1416 * 28
  inner = f'''<rect x="144" y="22" width="112" height="240" rx="17" fill="{ink}"/>
  <text x="152" y="54" font-size="7" font-weight="800" fill="{cream}" letter-spacing=".8" {FONT}>ROUND 1</text>
  <text x="248" y="54" text-anchor="end" font-size="6.4" font-weight="700" fill="{gold}" {FONT}>60 s</text>
  <circle cx="200" cy="100" r="28" fill="none" stroke="#3A332C" stroke-width="6"/>
  <circle cx="200" cy="100" r="28" fill="none" stroke="{c}" stroke-width="6" stroke-linecap="round"
    stroke-dasharray="{round(arc * .7, 1)} {round(arc, 1)}" transform="rotate(-90 200 100)"/>
  <text x="200" y="103" text-anchor="middle" font-size="13" font-weight="800" fill="{cream}" {FONT}>0:42</text>
  <text x="200" y="113" text-anchor="middle" font-size="5.4" fill="#A89B88" {FONT}>left</text>
  <text x="200" y="158" text-anchor="middle" font-size="22" font-weight="800" fill="#fff" {FONT}>38</text>
  <text x="200" y="168" text-anchor="middle" font-size="5.6" font-weight="700" fill="#A89B88" letter-spacing="1" {FONT}>PUNCHES</text>
  <rect x="158" y="176" width="84" height="16" rx="8" fill="{c}"/>
  <text x="200" y="186.6" text-anchor="middle" font-size="6.4" font-weight="700" fill="#fff" {FONT}>Hook · 7.2 m/s</text>
  <text x="152" y="208" font-size="6" font-weight="800" fill="{cream}" {FONT}>L</text>
  <rect x="161" y="203" width="86" height="6" rx="3" fill="#3A332C"/><rect x="161" y="203" width="40" height="6" rx="3" fill="{gold}"/>
  <text x="152" y="222" font-size="6" font-weight="800" fill="{cream}" {FONT}>R</text>
  <rect x="161" y="217" width="86" height="6" rx="3" fill="#3A332C"/><rect x="161" y="217" width="58" height="6" rx="3" fill="{c}"/>
  <text x="200" y="242" text-anchor="middle" font-size="5.6" fill="#A89B88" {FONT}>Blocks 6 · Combos 4</text>'''
  judges = ''.join(f'<text x="10" y="{y}" font-size="6.2" fill="#5E564C" {FONT}>{name}</text>'
                   f'<text x="84" y="{y}" text-anchor="end" font-size="6.4" font-weight="800" fill="{ink}" {FONT}>{score}</text>'
                   for y, name, score in [(30, 'Power', '10-9'), (42, 'Volume', '10-9'), (54, 'Ring craft', '10-10')])
  extra = f'''<path d="M60 250 q30 -70 100 -96" stroke="{c}" stroke-width="10" fill="none" opacity=".08" stroke-linecap="round"/>
  <path d="M396 40 q-50 20 -120 70" stroke="{c}" stroke-width="10" fill="none" opacity=".08" stroke-linecap="round"/>
  <g transform="translate(26 60)"><rect width="94" height="86" rx="10" fill="#FBF8F2" stroke="#D6CCBC"/>
    <text x="10" y="16" font-size="5.8" font-weight="800" fill="{c}" letter-spacing="1" {FONT}>JUDGES' CARDS</text>{judges}
    <g transform="rotate(-6 30 70)"><rect x="10" y="63" width="40" height="15" rx="3" fill="#FBF8F2" stroke="{c}" stroke-width="1.4"/>
    <text x="30" y="73.5" text-anchor="middle" font-size="6.4" font-weight="800" fill="{c}" letter-spacing=".8" {FONT}>WIN</text></g></g>
  <g transform="translate(280 146)"><rect width="92" height="58" rx="10" fill="#FBF8F2" stroke="#D6CCBC"/>
    <text x="10" y="16" font-size="5.8" font-weight="700" fill="#5E564C" {FONT}>World rating</text>
    <text x="10" y="36" font-size="15" font-weight="800" fill="{ink}" {FONT}>1,184</text>
    <text x="10" y="49" font-size="5.8" font-weight="700" fill="#2F7A3E" {FONT}>&#9650; +24 · #3 in Montréal</text></g>'''
  return _phone(inner, p['bg'], extra)


def _cube(x, y, s, col, face=True):
  """A rounded cube in two-point view: front face at (x, y), size s."""
  d = s * .32
  top = f'{x},{y} {x + d},{y - d} {x + s + d},{y - d} {x + s},{y}'
  side = f'{x + s},{y} {x + s + d},{y - d} {x + s + d},{y + s - d} {x + s},{y + s}'
  out = (f'<polygon points="{top}" fill="{col}" stroke="#3B2A5A" stroke-width="1.6" stroke-linejoin="round"/>'
         f'<polygon points="{top}" fill="#fff" opacity=".35"/>'
         f'<polygon points="{side}" fill="{col}" stroke="#3B2A5A" stroke-width="1.6" stroke-linejoin="round"/>'
         f'<polygon points="{side}" fill="#3B2A5A" opacity=".16"/>'
         f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="{s * .16}" fill="{col}" stroke="#3B2A5A" stroke-width="1.6"/>')
  if face:
    e, r = s * .18, s * .09
    out += (f'<circle cx="{x + s * .32}" cy="{y + s * .4}" r="{r * 1.6}" fill="#fff"/><circle cx="{x + s * .68}" cy="{y + s * .4}" r="{r * 1.6}" fill="#fff"/>'
            f'<circle cx="{x + s * .34}" cy="{y + s * .42}" r="{r}" fill="#3B2A5A"/><circle cx="{x + s * .7}" cy="{y + s * .42}" r="{r}" fill="#3B2A5A"/>'
            f'<path d="M{x + s * .36} {y + s * .64} q{s * .14} {e} {s * .28} 0" stroke="#3B2A5A" stroke-width="{max(1.2, s * .05)}" fill="none" stroke-linecap="round"/>'
            f'<circle cx="{x + s * .18}" cy="{y + s * .62}" r="{r}" fill="#FF9EC6" opacity=".8"/><circle cx="{x + s * .82}" cy="{y + s * .62}" r="{r}" fill="#FF9EC6" opacity=".8"/>')
  return out


def art_cubes(p):
  c, teal, lemon, sky, ink = p['color'], '#19BFAE', '#FFD23F', '#6CC6FF', '#3B2A5A'
  inner = f'''<rect x="28" y="42" width="344" height="216" fill="#E4F5FF"/>
  <circle cx="330" cy="70" r="12" fill="{lemon}" opacity=".9"/>
  <ellipse cx="110" cy="74" rx="26" ry="9" fill="#fff"/><ellipse cx="128" cy="69" rx="16" ry="8" fill="#fff"/>
  <path d="M10 268 Q60 150 200 146 T392 268Z" fill="#C9F2E8" stroke="{ink}" stroke-width="1.6"/>
  <path d="M60 200 q8 -6 16 0 M290 190 q8 -6 16 0 M200 236 q8 -6 16 0" stroke="#9BDCCB" stroke-width="2" fill="none" stroke-linecap="round"/>
  <ellipse cx="312" cy="222" rx="34" ry="11" fill="#B9E7FF" stroke="{ink}" stroke-width="1.4"/>
  <line x1="70" y1="196" x2="70" y2="150" stroke="{ink}" stroke-width="2.4"/>
  <circle cx="70" cy="140" r="15" fill="{c}" stroke="{ink}" stroke-width="1.6"/>
  <path d="M70 140 m-9 0 a9 9 0 1 1 9 9 a5 5 0 1 1 -5 -5" stroke="#fff" stroke-width="2" fill="none" opacity=".8"/>
  {_cube(288, 128, 24, sky)}
  <path d="M168 178 q14 -10 30 0" stroke="{ink}" stroke-width="2.4" fill="none" stroke-linecap="round"/>
  {_cube(116, 150, 48, c)}{_cube(196, 158, 42, teal)}
  <path d="M182 136 c-3 -5 -10 -2 -7 3 l7 6 l7 -6 c3 -5 -4 -8 -7 -3z" fill="{c}" stroke="{ink}" stroke-width="1.2"/>
  {_cube(170, 214, 20, lemon)}
  <g transform="translate(40 52)"><rect width="66" height="16" rx="8" fill="#fff" stroke="{ink}" stroke-width="1.4"/>
    <text x="9" y="11" font-size="7" font-weight="800" fill="{ink}" {FONT}>&#10024; 1,240</text></g>
  <g transform="translate(112 52)"><rect width="74" height="16" rx="8" fill="#fff" stroke="{ink}" stroke-width="1.4"/>
    <path d="M10 6.5 c-1.6 -2.6 -5.6 -1 -3.8 1.8 l3.8 3.3 l3.8 -3.3 c1.8 -2.8 -2.2 -4.4 -3.8 -1.8z" fill="{c}"/>
    <rect x="18" y="5.5" width="48" height="5" rx="2.5" fill="#FFE0EE"/><rect x="18" y="5.5" width="40" height="5" rx="2.5" fill="{c}"/></g>
  <g transform="translate(258 94) rotate(-6)"><polygon points="0,-16 5,-7 16,-9 10,0 16,9 5,8 0,17 -5,8 -16,9 -10,0 -16,-9 -5,-7" fill="{lemon}" stroke="{ink}" stroke-width=".7" stroke-linejoin="round" transform="scale(2.3)"/>
    <text x="0" y="0" text-anchor="middle" font-size="8" font-weight="900" fill="{ink}" {FONT}>BOING!</text>
    <text x="0" y="9" text-anchor="middle" font-size="6.4" font-weight="900" fill="{ink}" {FONT}>+3 &#10024;</text></g>'''
  return _browser(inner, 'quickybricks.com · the world', p['bg'])


def art_party(p):
  c, mustard, navy, ink, paper = p['color'], '#E3A21A', '#23416D', '#1F1A14', '#FBF6EA'
  people = [('A', c), ('T', navy), ('M', mustard), ('J', '#2C7A3B')]
  slots = ''
  for i, (name, n, best) in enumerate([('Fri dinner', 4, True), ('Sat brunch', 2, False), ('Sun dinner', 1, False)]):
    y = 84 + i * 22
    slots += (f'<rect x="212" y="{y - 10}" width="148" height="18" rx="3" fill="#fff" stroke="#CDBD9C"/>'
              f'<text x="219" y="{y + 2}" font-size="6.6" font-weight="{"800" if best else "500"}" fill="{ink}" {FONT}>{name}</text>')
    for j in range(n):
      ini, col = people[j]
      slots += (f'<circle cx="{274 + j * 12}" cy="{y - 1}" r="5.4" fill="{col}"/>'
                f'<text x="{274 + j * 12}" y="{y + 1.4}" text-anchor="middle" font-size="5.6" font-weight="800" fill="#fff" {FONT}>{ini}</text>')
  ticks = ''.join(f'<rect x="{212 + i * 11}" y="170" width="8" height="8" rx="1.5" fill="{c if i < 6 else "#fff"}" stroke="{ink}" stroke-width=".9"/>'
                  for i in range(10))
  dishes = ''
  for i, (dish, who) in enumerate([('Soup', 'Ana'), ('Bread', 'Tom'), ('Dessert', '?')]):
    y = 196 + i * 13
    want = who == '?'
    dishes += (f'<text x="212" y="{y}" font-size="6.4" fill="{ink}" {FONT}>{dish}</text>'
               f'<line x1="{214 + len(dish) * 4}" y1="{y - 1}" x2="340" y2="{y - 1}" stroke="#8F816C" stroke-width=".9" stroke-dasharray="1 2"/>'
               f'<text x="360" y="{y}" text-anchor="end" font-size="6.4" font-weight="700" fill="{c if want else navy}" {FONT}>{"Still wanted" if want else who}</text>')
  inner = f'''<rect x="28" y="42" width="344" height="216" fill="{p['bg']}"/>
  <rect x="38" y="52" width="160" height="196" fill="{paper}" stroke="{ink}" stroke-width="1.2"/>
  <rect x="42" y="56" width="152" height="188" fill="none" stroke="{ink}" stroke-width=".6"/>
  <text x="52" y="72" font-size="6.2" font-weight="700" fill="{c}" letter-spacing="1.2" font-family="'Courier New', monospace">ITEM No. 07</text>
  <text x="52" y="94" font-size="19" font-style="italic" font-weight="700" fill="{ink}" font-family="Georgia, serif">Soup Night</text>
  <text x="52" y="108" font-size="9" font-style="italic" fill="{navy}" font-family="Georgia, serif">Supper for eight</text>
  <ellipse cx="118" cy="186" rx="54" ry="9" fill="{mustard}" opacity=".35"/>
  <path d="M82 152 h72 v22 a12 12 0 0 1 -12 12 h-48 a12 12 0 0 1 -12 -12z" fill="{c}" stroke="{ink}" stroke-width="1.4"/>
  <rect x="76" y="146" width="84" height="8" rx="4" fill="{navy}" stroke="{ink}" stroke-width="1.4"/>
  <path d="M100 140 q-5 -6 0 -11 q5 -5 0 -10 M118 140 q-5 -6 0 -11 q5 -5 0 -10 M136 140 q-5 -6 0 -11 q5 -5 0 -10" stroke="{navy}" stroke-width="1.6" fill="none" opacity=".55"/>
  <line x1="52" y1="200" x2="186" y2="200" stroke="{ink}" stroke-width=".6"/>
  <text x="52" y="214" font-size="6.2" fill="{ink}" {FONT}>Serves 8 · Easy · Cosy</text>
  <text x="52" y="230" font-size="6.2" fill="{ink}" {FONT}>Hosted by Mira · 6 seats left</text>
  <text x="212" y="64" font-size="8" font-weight="800" fill="{ink}" {FONT}>When are you free?</text>
  {slots}
  <g transform="translate(344 58) rotate(12)"><circle r="13" fill="{mustard}" stroke="{ink}" stroke-width="1.2"/>
    <text y="-1" text-anchor="middle" font-size="5.4" font-weight="900" fill="{ink}" {FONT}>BEST</text>
    <text y="6" text-anchor="middle" font-size="5.4" font-weight="900" fill="{ink}" {FONT}>BET</text></g>
  <text x="212" y="162" font-size="8" font-weight="800" fill="{ink}" {FONT}>The menu</text>
  <text x="360" y="162" text-anchor="end" font-size="6" font-weight="700" fill="#5F5446" {FONT}>6 of 10 filled</text>
  {ticks}{dishes}
  <rect x="212" y="232" width="148" height="16" rx="8" fill="{c}"/>
  <text x="286" y="242.6" text-anchor="middle" font-size="7" font-weight="800" fill="#FFF8EC" {FONT}>Count me in</text>'''
  return _browser(inner, 'planfriday.com/p/soup-night', p['bg'])


def art_pan(p):
  c, gold, ink, green = p['color'], '#E3A33B', '#3D2B22', '#4F7F4E'
  rows = ''
  for i, (name, base, mins, tier, keeps, col) in enumerate([('Creamy mushroom', 'rice', 25, '$$', 2, '#C9A27A'),
                                                            ('Chicken & peppers', 'pasta', 30, '$$', 3, gold),
                                                            ('Tomato beef ragù', 'potatoes', 35, '$', 4, c)]):
    y = 98 + i * 34
    rows += (f'<rect x="150" y="{y}" width="100" height="29" rx="8" fill="#FFFAF2" stroke="#ECDCC6"/>'
             f'<circle cx="163" cy="{y + 14.5}" r="7" fill="{col}" stroke="{ink}" stroke-width="1"/>'
             f'<text x="175" y="{y + 12}" font-size="6.2" font-weight="800" fill="{ink}" {FONT}>{name}</text>'
             f'<text x="175" y="{y + 22}" font-size="5.2" fill="#7B6152" {FONT}>over {base} · {mins} min · {tier}</text>')
    if i == 0:
      rows += (f'<rect x="216" y="{y - 5}" width="30" height="10" rx="5" fill="#E3EEDB"/>'
               f'<text x="231" y="{y + 1.8}" text-anchor="middle" font-size="5" font-weight="700" fill="{green}" {FONT}>Tonight</text>')
  inner = f'''<rect x="144" y="22" width="112" height="240" rx="17" fill="#FBF3E6"/>
  <rect x="182" y="27" width="36" height="8" rx="4" fill="#111827"/>
  <text x="152" y="52" font-size="7.6" font-weight="800" fill="{ink}" {FONT}>This week</text>
  <text x="248" y="52" text-anchor="end" font-size="5.8" fill="#7B6152" {FONT}>for 2</text>
  <g transform="rotate(-2 200 74)"><rect x="152" y="58" width="96" height="30" rx="3" fill="#FFF4D6" stroke="#ECDCC6"/>
    <text x="158" y="71" font-size="7" font-style="italic" fill="{ink}" font-family="Georgia, serif">You've got rice.</text>
    <text x="158" y="82" font-size="7" font-style="italic" fill="{ink}" font-family="Georgia, serif">I've got the rest. <tspan fill="{c}">&#9829;</tspan></text></g>
  {rows}
  <rect x="150" y="206" width="100" height="17" rx="8.5" fill="{c}"/>
  <text x="200" y="217.2" text-anchor="middle" font-size="6.6" font-weight="800" fill="#fff" {FONT}>Let's cook</text>
  <rect x="150" y="228" width="100" height="17" rx="8.5" fill="#fff" stroke="#ECDCC6"/>
  <text x="200" y="239.2" text-anchor="middle" font-size="6.4" font-weight="700" fill="{ink}" {FONT}>Too tired tonight</text>'''
  items = ''.join(f'<rect x="10" y="{y - 6}" width="7" height="7" rx="1.5" fill="{green if done else "#fff"}" stroke="{ink}" stroke-width=".9"/>'
                  + (f'<path d="M11.5 {y - 2.5} l1.6 1.6 2.6-2.9" stroke="#fff" stroke-width="1" fill="none"/>' if done else '')
                  + f'<text x="22" y="{y}" font-size="6.2" fill="{"#A8907E" if done else ink}" {FONT}>{name}</text>'
                  for y, name, done in [(34, 'Mushrooms', 1), (48, 'Cream', 1), (62, 'Peppers', 0), (76, 'Beef mince', 0), (90, 'Parmesan', 0)])
  extra = f'''<g transform="translate(70 134)"><rect x="-74" y="-5" width="40" height="10" rx="5" fill="{ink}" transform="rotate(-18)"/>
    <circle r="44" fill="{ink}"/><circle r="37" fill="#5A463B"/>
    <circle r="31" fill="{c}"/><circle cx="-10" cy="-8" r="6" fill="#E9C9A0"/><circle cx="12" cy="-4" r="5" fill="#E9C9A0"/>
    <circle cx="2" cy="12" r="6" fill="#E9C9A0"/><circle cx="-14" cy="12" r="3" fill="{green}"/><circle cx="16" cy="14" r="3" fill="{green}"/>
    <path d="M-18 -30 q-6 -10 0 -18 M0 -32 q-6 -10 0 -18 M18 -30 q-6 -10 0 -18" stroke="{ink}" stroke-width="1.6" fill="none" opacity=".25"/></g>
  <g transform="translate(280 70) rotate(4)"><rect width="94" height="104" rx="4" fill="#FFFAF2" stroke="#ECDCC6"/>
    <text x="10" y="18" font-size="7.4" font-weight="800" fill="{ink}" {FONT}>Shopping</text>{items}</g>'''
  return _phone(inner, p['bg'], extra)


def art_personal(p):
  c, ink, night, yel, brown = p['color'], '#1C1A18', '#2F2C29', '#F4BC4C', '#8A5A1E'
  nav = ''.join(f'<rect x="{x}" y="50" width="{w}" height="4" rx="2" fill="#E9E2D8" opacity="{.95 if i == 0 else .6}"/>'
                for i, (x, w) in enumerate([(206, 20), (234, 26), (268, 30), (306, 20)]))
  curtain = ''.join(f'<rect x="{x}" y="62" width="5" height="196" fill="#fff" opacity="{.5 if i % 2 else .28}"/>'
                    for i, x in enumerate(range(232, 372, 9)))
  inner = f'''<rect x="28" y="42" width="344" height="216" fill="{p['bg']}"/>
  <rect x="228" y="62" width="144" height="196" fill="#EFE6DA"/>{curtain}
  <rect x="28" y="42" width="344" height="20" fill="{night}"/>
  <circle cx="44" cy="52" r="5" fill="#fff"/><path d="M44 47 l-4 6 h4 v4 l4 -6 h-4z" fill="{c}"/>
  <rect x="54" y="48" width="40" height="4" rx="2" fill="#F3ECE0"/><rect x="54" y="55" width="30" height="2.6" rx="1.3" fill="#A89B88"/>
  {nav}
  <rect x="332" y="46" width="32" height="12" rx="2.5" fill="{yel}"/>
  <text x="348" y="54.2" text-anchor="middle" font-size="5.4" font-weight="700" fill="{ink}" {FONT}>Talk &#8599;</text>
  <text x="48" y="90" font-size="5.2" font-weight="700" fill="{brown}" letter-spacing="1" {FONT}>PEOPLE AND TECHNOLOGY</text>
  <text x="48" y="106" font-size="10" fill="#4A4540" {FONT}>Let&#8217;s talk about</text>
  <text x="46" y="134" font-size="27" font-weight="800" fill="{ink}" letter-spacing="-1.4" {FONT}>Choosing the</text>
  <text x="46" y="162" font-size="27" font-weight="800" fill="{ink}" letter-spacing="-1.4" {FONT}>right tools</text>
  <rect x="48" y="176" width="130" height="4.5" rx="2.25" fill="#B9AFA3"/><rect x="48" y="185" width="84" height="4.5" rx="2.25" fill="#B9AFA3"/>
  <rect x="48" y="198" width="70" height="17" rx="2.5" fill="{yel}"/>
  <text x="83" y="209" text-anchor="middle" font-size="6.2" font-weight="700" fill="{ink}" {FONT}>Set up a call &#8599;</text>
  <rect x="124" y="198" width="66" height="17" rx="2.5" fill="none" stroke="#B9AFA3"/>
  <text x="157" y="209" text-anchor="middle" font-size="6.2" font-weight="600" fill="{ink}" {FONT}>Explore work &#8594;</text>
  <circle cx="51" cy="231" r="2.2" fill="{brown}"/><rect x="58" y="229.5" width="110" height="3.4" rx="1.7" fill="#C9C0B4"/>
  <rect x="236" y="196" width="136" height="44" rx="10" fill="#F6F1EA"/><rect x="236" y="232" width="136" height="26" fill="#EDE5DA"/>
  <path d="M270 258 L274 200 Q276 184 296 180 L304 178 L320 178 L328 180 Q348 184 350 200 L354 258 Z" fill="{night}"/>
  <path d="M304 178 L312 206 L320 178 Z" fill="#FBF8F3"/>
  <path d="M304 178 L312 206 L306 214 L298 182 Z M320 178 L312 206 L318 214 L326 182 Z" fill="#24211E"/>
  <rect x="306" y="166" width="12" height="14" rx="4" fill="#E2BE9C"/>
  <ellipse cx="312" cy="152" rx="15" ry="18" fill="#EAC9A7"/>
  <path d="M296 150 Q294 128 312 128 Q331 128 329 148 Q324 138 312 139 Q301 139 296 150 Z" fill="#5A3B26"/>
  <path d="M286 236 Q300 224 312 230 Q324 224 338 236" stroke="#3D3934" stroke-width="7" fill="none" stroke-linecap="round"/>'''
  return _browser(inner, 'arkvital.com', p['bg'])


def art_monitor(p):
  c, ink, muted, line = p['color'], '#14181F', '#566170', '#DDE2E8'
  good, warn, bad, pulse = '#11803A', '#B86E00', '#CF2330', '#00A46A'
  code = "font-family=\"'JetBrains Mono', 'IBM Plex Mono', ui-monospace, monospace\""
  nav = ''.join(f'<text x="{x}" y="53.4" font-size="5.6" font-weight="{600 if on else 500}" fill="{ink if on else muted}" {FONT}>{name}</text>'
                for x, name, on in [(104, 'Console', 1), (138, 'Incidents', 0), (178, 'Robots', 0), (210, 'Status page', 0)])
  kpis = ''
  for i, (label, value, col) in enumerate([('SITES UP', '7/8', good), ('OPEN INCIDENTS', '1', bad),
                                           ('AVG RESPONSE', '212 ms', ink), ('CERTS EXPIRING', '1', warn)]):
    x = 38 + i * 82
    kpis += (f'<rect x="{x}" y="64" width="76" height="25" rx="4" fill="#fff" stroke="{line}"/>'
             f'<text x="{x + 6}" y="72.6" font-size="4.4" fill="{muted}" letter-spacing=".4" {code}>{label}</text>'
             f'<text x="{x + 6}" y="84.4" font-size="9" font-weight="700" fill="{col}" {code}>{value}</text>')
  sites = [('northwind.example', good, 'g' * 24, '184 ms', '100%'),
           ('shop.example', bad, 'g' * 22 + 'bb', '503', '99.2%'),
           ('blog.example', warn, 'g' * 13 + 'wwww' + 'g' * 7, '1.9 s', '99.9%'),
           ('docs.example', good, 'g' * 24, '96 ms', '100%')]
  fills = {'g': '#3FBF6F', 'w': '#E9A63A', 'b': bad}
  rows = ''
  for i, (name, led, cells, ms, up) in enumerate(sites):
    y = 104 + i * 18
    if led == bad:
      rows += f'<rect x="38" y="{y}" width="324" height="18" fill="#FFF1F1"/>'
    rows += (f'<circle cx="45" cy="{y + 9}" r="2.6" fill="{led}"/>'
             f'<text x="52" y="{y + 11.2}" font-size="6.2" font-weight="600" fill="{ink}" {FONT}>{name}</text>'
             + ''.join(f'<rect x="{round(146 + k * 6, 1)}" y="{y + 4.5}" width="4.8" height="9" rx="1" fill="{fills[ch]}"/>'
                       for k, ch in enumerate(cells))
             + f'<text x="318" y="{y + 11}" text-anchor="end" font-size="5.6" fill="{bad if led == bad else muted}" {code}>{ms}</text>'
             f'<text x="358" y="{y + 11}" text-anchor="end" font-size="5.6" font-weight="700" fill="{ink}" {code}>{up}</text>'
             f'<rect x="38" y="{y + 17.5}" width="324" height=".6" fill="{line}"/>')
  log = ''
  for i, (stamp, txt, col) in enumerate([('14:05', '&#10007; shop.example 503 &#183; incident opened', bad),
                                         ('14:05', '&#8594; playbook: email + Slack webhook', c),
                                         ('14:07', '&#8635; second robot recheck &#183; still down', warn),
                                         ('06:00', '&#10003; certificate inspector &#183; 8 sites checked', good)]):
    y = 203.5 + i * 9.6
    log += (f'<text x="46" y="{y}" font-size="5.4" fill="#8A94A1" {code}>{stamp}</text>'
            f'<text x="70" y="{y}" font-size="5.4" fill="{col}" {code}>{txt}</text>')
  inner = f'''<rect x="28" y="42" width="344" height="216" fill="#F4F6F8"/>
  <rect x="28" y="42" width="344" height="16" fill="#fff"/><rect x="28" y="57.4" width="344" height=".6" fill="{line}"/>
  <g transform="translate(37 44.5) scale(.17)"><rect width="64" height="64" rx="15" fill="#10161D"/>
    <path d="M9 35h11l4.5-10 7 21 7.5-30 5 19H55" fill="none" stroke="#2BD38A" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="51" cy="13" r="5" fill="#5C9DFF"/></g>
  <text x="52" y="53.6" font-size="7" font-weight="700" fill="{ink}" {FONT}>VitalRPA</text>
  {nav}<rect x="104" y="56" width="22" height="1.6" fill="{c}"/>
  <circle cx="167.5" cy="47.6" r="2.6" fill="{bad}"/><text x="167.5" y="48.8" text-anchor="middle" font-size="3.4" font-weight="700" fill="#fff" {FONT}>1</text>
  <circle cx="318" cy="50" r="1.8" fill="{pulse}"/>
  <text x="362" y="52" text-anchor="end" font-size="5.4" fill="{muted}" {code}>14:07 UTC</text>
  {kpis}
  <rect x="38" y="93" width="324" height="11" fill="#fff"/>
  <text x="44" y="100.4" font-size="4.4" fill="{muted}" letter-spacing=".4" {code}>SITE</text>
  <text x="146" y="100.4" font-size="4.4" fill="{muted}" letter-spacing=".4" {code}>LAST 24 HOURS</text>
  <text x="318" y="100.4" text-anchor="end" font-size="4.4" fill="{muted}" letter-spacing=".4" {code}>RESP</text>
  <text x="358" y="100.4" text-anchor="end" font-size="4.4" fill="{muted}" letter-spacing=".4" {code}>30 D</text>
  <rect x="38" y="104" width="324" height="72" fill="#fff"/>{rows}
  <rect x="38" y="93" width="324" height="83" fill="none" stroke="{line}"/>
  <rect x="38" y="182" width="324" height="56" rx="4" fill="#fff" stroke="{line}"/>
  <text x="46" y="192" font-size="4.4" fill="{muted}" letter-spacing=".4" {code}>ROBOT LOG</text>
  <circle cx="354" cy="190.4" r="1.8" fill="{pulse}"/>
  {log}'''
  return _browser(inner, 'vitalrpa.com', p['bg'])


def art_hotel(p):
  """A hotel site: arched-window hero, 'who is coming?' chips and the hour-by-hour stay plan."""
  c, gilt, ink, paper, muted = p['color'], '#B4832C', '#1D2B28', '#FBF6EC', '#6B6F66'
  serif = "font-family=\"'Cormorant Garamond', 'Instrument Serif', Georgia, serif\""
  nav = ''.join(f'<text x="{x}" y="53.6" font-size="5.2" font-weight="500" fill="{ink}" letter-spacing=".8" {FONT}>{name}</text>'
                for x, name in [(250, 'ROOMS'), (278, 'STAY'), (302, 'MAP')])
  chips, x = '', 166
  for name, on in [('Foodie', 1), ('Couple', 0), ('Art lover', 0), ('Family', 0)]:
    w = round(len(name) * 3.5 + 14, 1)
    chips += (f'<rect x="{x}" y="80" width="{w}" height="14" rx="7" fill="{c if on else paper}" stroke="{c}" stroke-width=".9"/>'
              f'<text x="{round(x + w / 2, 1)}" y="89.2" text-anchor="middle" font-size="6" font-weight="{600 if on else 500}" '
              f'fill="{paper if on else c}" {FONT}>{name}</text>')
    x = round(x + w + 5, 1)
  plan = ''
  for i, (time, what, walk) in enumerate([('15:00', 'Check-in and a welcome tea', ''),
                                         ('16:30', 'Art Nouveau facades walk', '6 min'),
                                         ('19:30', 'Dinner at the market hall', '9 min'),
                                         ('22:00', 'Nightcap with a rooftop view', '2 min')]):
    y = 136 + i * 19
    plan += (f'<circle cx="172" cy="{y - 2}" r="3" fill="{paper}" stroke="{gilt}" stroke-width="1.3"/>'
             f'<text x="181" y="{y}" font-size="5.8" font-weight="700" fill="{gilt}" {FONT}>{time}</text>'
             f'<text x="202" y="{y}" font-size="6.4" fill="{ink}" {FONT}>{what}</text>')
    if walk:
      plan += f'<text x="360" y="{y}" text-anchor="end" font-size="5.4" fill="{muted}" {FONT}>{walk} on foot</text>'
  arch = 'M40 250 V122 A56 56 0 0 1 152 122 V250 Z'
  roofs = ('M40 250 V178 L50 172 V164 L60 156 L70 164 V176 H80 V152 L90 140 L100 152 V170 H110 V160 '
           'Q118 144 126 160 V176 H136 V166 L144 160 L152 164 V250 Z')
  windows = ''.join(f'<rect x="{wx}" y="{wy}" width="3" height="5" rx="1.5" fill="{gilt}" opacity=".85"/>'
                    for wx, wy in [(56, 182), (64, 182), (86, 160), (94, 160), (86, 176), (116, 178), (124, 186), (140, 180)])
  inner = f'''<rect x="28" y="42" width="344" height="216" fill="{p['bg']}"/>
  <rect x="28" y="42" width="344" height="18" fill="{paper}"/><rect x="28" y="59.6" width="344" height=".6" fill="{gilt}"/>
  <text x="40" y="54" font-size="7.2" font-weight="600" fill="{c}" letter-spacing="1.8" {serif}>HOTEL AURELIA</text>
  {nav}
  <rect x="326" y="46.5" width="36" height="10.5" rx="5.25" fill="{c}"/>
  <text x="344" y="53.7" text-anchor="middle" font-size="5.4" font-weight="600" fill="{paper}" {FONT}>Book</text>
  <path d="{arch}" fill="#E9D6B4"/>
  <circle cx="118" cy="104" r="10" fill="#F2C46B"/>
  <path d="M62 112 q8 -5 16 0 q6 -4 12 0" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round" opacity=".8"/>
  <path d="{roofs}" fill="{c}"/><line x1="90" y1="140" x2="90" y2="128" stroke="{c}" stroke-width="1.6"/>
  {windows}
  <path d="{arch}" fill="none" stroke="{gilt}" stroke-width="1.6"/>
  <path d="M46 250 V123 A50 50 0 0 1 146 123 V250" fill="none" stroke="{gilt}" stroke-width=".6"/>
  <rect x="58" y="224" width="76" height="16" rx="8" fill="{paper}"/>
  <text x="96" y="234.6" text-anchor="middle" font-size="6" font-weight="600" fill="{ink}" {FONT}>&#9733; 9.4 &#183; Superb</text>
  <text x="166" y="74" font-size="5.2" font-weight="600" fill="{gilt}" letter-spacing="1.2" {FONT}>WHO IS COMING?</text>
  {chips}
  <text x="166" y="116" font-size="13" font-style="italic" fill="{ink}" {serif}>Your stay, hour by hour</text>
  <path d="M166 123 q10 -5 20 0 t20 0 t20 0" stroke="{gilt}" stroke-width=".9" fill="none"/>
  <line x1="172" y1="134" x2="172" y2="191" stroke="{gilt}" stroke-width=".8" stroke-dasharray="2 2"/>
  {plan}
  <rect x="166" y="210" width="108" height="18" rx="9" fill="{c}"/>
  <text x="220" y="221.4" text-anchor="middle" font-size="6.2" font-weight="600" fill="{paper}" {FONT}>Check dates on Booking</text>
  <rect x="280" y="210" width="82" height="18" rx="9" fill="none" stroke="{c}"/>
  <text x="321" y="221.4" text-anchor="middle" font-size="6.2" font-weight="600" fill="{c}" {FONT}>Walk it on the map</text>
  <text x="166" y="244" font-size="5.6" fill="{muted}" {FONT}>Booking and payment, explained in three steps</text>'''
  return _browser(inner, 'arvistay.com/s/aurelia', p['bg'])


def _toon(x, y, col, ink, wave=False):
  """A joints-and-sticks cartoon kid with its head at (x, y)."""
  hand = (x + 16, y - 4) if wave else (x + 14, y + 27)
  bones = [((x, y + 11), (x, y + 34)), ((x, y + 17), (x - 14, y + 28)), ((x, y + 17), hand),
           ((x, y + 34), (x - 9, y + 51)), ((x, y + 34), (x + 9, y + 51))]
  out = ''.join(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{ink}" stroke-width="6.5" stroke-linecap="round"/>'
                for a, b in bones)
  out += ''.join(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{col}" stroke-width="3.2" stroke-linecap="round"/>'
                 for a, b in bones)
  out += ''.join(f'<circle cx="{jx}" cy="{jy}" r="2.3" fill="#fff" stroke="{ink}" stroke-width="1.1"/>'
                 for jx, jy in [(x, y + 17), (x, y + 34)])
  out += (f'<circle cx="{x}" cy="{y}" r="11" fill="{col}" stroke="{ink}" stroke-width="2"/>'
          f'<circle cx="{x - 4}" cy="{y - 1}" r="2.8" fill="#fff"/><circle cx="{x + 4}" cy="{y - 1}" r="2.8" fill="#fff"/>'
          f'<circle cx="{x - 3.4}" cy="{y - .6}" r="1.4" fill="{ink}"/><circle cx="{x + 4.6}" cy="{y - .6}" r="1.4" fill="{ink}"/>'
          f'<path d="M{x - 4} {y + 4} q4 3.6 8 0" stroke="{ink}" stroke-width="1.4" fill="none" stroke-linecap="round"/>')
  return out


def art_toon(p):
  """The ToonyLoony studio: hold an actor and drag it to record its path while the clock runs."""
  c, ink, yel, pink, green, red = p['color'], '#1A1D3A', '#FFC532', '#FF4FA3', '#1FBF63', '#FF3048'

  def block(x, y, w, h, fill, r=6):
    return (f'<rect x="{x}" y="{y + 3}" width="{w}" height="{h}" rx="{r}" fill="{ink}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{ink}" stroke-width="1.6"/>')

  studs = ''.join(f'<circle cx="{sx}" cy="{sy}" r="1.3" fill="#D6DBFF"/>' for sx in range(36, 372, 16) for sy in range(66, 258, 16))
  tabs = ''
  for x, name, on in [(150, 'Cast', 0), (178, 'Animate', 0), (218, 'Studio', 1)]:
    w = len(name) * 4 + 10
    if on:
      tabs += f'<rect x="{x - 5}" y="45.5" width="{w}" height="11" rx="3" fill="{yel}" stroke="{ink}" stroke-width="1.2"/>'
    tabs += f'<text x="{x}" y="53.6" font-size="6.2" font-weight="800" fill="{ink}" {FONT}>{name}</text>'
  moves = ''
  for i, (name, on) in enumerate([('Wave', 0), ('Jump', 1), ('Spin', 0), ('Dance', 0)]):
    y = 88 + i * 19
    moves += (f'<rect x="306" y="{y}" width="48" height="14" rx="4" fill="{yel if on else "#fff"}" stroke="{ink}" stroke-width="1.2"/>'
              f'<text x="313" y="{y + 9.6}" font-size="6.2" font-weight="{800 if on else 600}" fill="{ink}" {FONT}>{name}</text>')
  keys = ''.join(f'<rect x="{kx - 3}" y="{ky - 3}" width="6" height="6" fill="{col}" stroke="{ink}" stroke-width="1" transform="rotate(45 {kx} {ky})"/>'
                 for kx, ky, col in [(84, 214, pink), (128, 214, pink), (196, 214, pink), (110, 228, c), (176, 228, c)])
  wave = ''.join(f'<rect x="{62 + i * 5}" y="{242 - h / 2}" width="2.6" height="{h}" rx="1.3" fill="{green}"/>'
                 for i, h in enumerate([3, 5, 7, 4, 6, 8, 5, 3, 6, 7, 4, 5, 8, 6, 3, 5, 7, 4, 6, 5, 3, 6, 8, 5, 4, 6, 7, 3, 5, 6,
                                        4, 7, 5, 3, 6, 8, 4, 5, 6, 3, 7, 5, 4, 6, 3, 5, 7, 6, 4, 5, 3, 6, 8, 5, 4, 6]))
  inner = f'''<rect x="28" y="42" width="344" height="216" fill="{p['bg']}"/>{studs}
  <rect x="28" y="42" width="344" height="18" fill="#fff"/><rect x="28" y="59.4" width="344" height="1" fill="{ink}"/>
  <text x="38" y="55" font-size="9.5" font-weight="900" fill="{c}" letter-spacing="-.2" {FONT}>ToonyLoony</text>
  {tabs}
  <rect x="326" y="45.5" width="36" height="11" rx="3" fill="{c}" stroke="{ink}" stroke-width="1.2"/>
  <text x="344" y="53.6" text-anchor="middle" font-size="6" font-weight="800" fill="#fff" {FONT}>Share</text>
  {block(38, 68, 252, 126, '#BFE6FF', 8)}
  <circle cx="262" cy="92" r="10" fill="{yel}" stroke="{ink}" stroke-width="1.4"/>
  <ellipse cx="140" cy="84" rx="14" ry="5" fill="#fff"/><ellipse cx="148" cy="80" rx="8" ry="4.5" fill="#fff"/>
  <path d="M39 170 Q100 146 166 164 T289 154 V186 Q289 193 282 193 H45 Q39 193 39 186 Z" fill="{green}"/>
  <rect x="38" y="68" width="252" height="126" rx="8" fill="none" stroke="{ink}" stroke-width="1.6"/>
  <path d="M136 182 C156 192 172 158 196 146 S210 134 212 134" stroke="{red}" stroke-width="2" fill="none" stroke-dasharray="3 3" stroke-linecap="round"/>
  {_toon(92, 110, pink, ink)}{_toon(212, 104, c, ink, wave=True)}
  <circle cx="212" cy="128" r="8" fill="none" stroke="{red}" stroke-width="1.6"/><circle cx="212" cy="128" r="3.2" fill="{red}" opacity=".6"/>
  <g transform="translate(228 122)"><rect width="52" height="13" rx="6.5" fill="#fff" stroke="{ink}" stroke-width="1.2"/>
    <text x="26" y="9" text-anchor="middle" font-size="5.8" font-weight="800" fill="{ink}" {FONT}>Hold &amp; drag</text></g>
  <rect x="52" y="74" width="50" height="16" rx="8" fill="#fff" stroke="{ink}" stroke-width="1.2"/>
  <path d="M80 89.4 L86 97 L88 89.4" fill="#fff" stroke="{ink}" stroke-width="1.2" stroke-linejoin="round"/>
  <rect x="80.6" y="88" width="7" height="2" fill="#fff"/>
  <text x="77" y="84.6" text-anchor="middle" font-size="6" font-weight="800" fill="{ink}" {FONT}>Watch this!</text>
  <g transform="translate(176 73)"><rect width="56" height="14" rx="7" fill="{red}" stroke="{ink}" stroke-width="1.2"/>
    <circle cx="9" cy="7" r="2.6" fill="#fff"/><text x="15" y="9.8" font-size="6.4" font-weight="900" fill="#fff" {FONT}>REC 0:07</text></g>
  {block(298, 68, 64, 126, '#fff')}
  <text x="306" y="81" font-size="6.8" font-weight="900" fill="{ink}" {FONT}>Moves</text>
  {moves}
  <text x="306" y="173" font-size="5.6" font-weight="700" fill="#5A5F86" {FONT}>Speed</text>
  <rect x="306" y="178" width="48" height="4" rx="2" fill="#E2E6FF"/><rect x="306" y="178" width="30" height="4" rx="2" fill="{c}"/>
  <circle cx="336" cy="180" r="4" fill="{yel}" stroke="{ink}" stroke-width="1.2"/>
  {block(38, 202, 324, 48, '#fff')}
  <circle cx="50" cy="214" r="4.6" fill="{pink}" stroke="{ink}" stroke-width="1.1"/>
  <rect x="62" y="210.5" width="190" height="7" rx="3.5" fill="#FFD3E8"/>
  <circle cx="50" cy="228" r="4.6" fill="{c}" stroke="{ink}" stroke-width="1.1"/>
  <rect x="62" y="224.5" width="150" height="7" rx="3.5" fill="#D9DCFF"/><rect x="150" y="224.5" width="62" height="7" rx="3.5" fill="{red}" opacity=".55"/>
  <path d="M48 240 v4 l3 -2 z M53 239.6 v5" stroke="{green}" stroke-width="1.2" fill="{green}"/>
  {wave}{keys}
  <line x1="212" y1="207" x2="212" y2="248" stroke="{red}" stroke-width="1.4"/>
  <path d="M207.5 205 h9 l-4.5 5 z" fill="{red}"/>
  <text x="356" y="216" text-anchor="end" font-size="5.6" font-weight="800" fill="{ink}" {FONT}>0:07</text>'''
  return _browser(inner, 'toonyloony.com · studio', p['bg'])


# ---- VR & mixed reality: the scene is seen through a headset visor (nose cut-out at the bottom).
VISOR = ('M64 34h272a32 32 0 0 1 32 32v116a32 32 0 0 1 -32 32h-80q-14 0 -21 -12l-6 -10q-7 -12 -29 -12'
         't-29 12l-6 10q-7 12 -21 12h-80a32 32 0 0 1 -32 -32v-116a32 32 0 0 1 32 -32z')


def _visor(inner, bg, cid, extra=''):
  """inner is drawn in 400x250 space and clipped to the visor (x 32-368, y 34-214)."""
  return f'''<svg viewBox="0 0 400 250" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
  <rect width="400" height="250" fill="{bg}"/>{extra}
  <defs><clipPath id="{cid}"><path d="{VISOR}"/></clipPath></defs>
  <path d="{VISOR}" fill="#0B1220" opacity=".12" transform="translate(4 7)"/>
  <g clip-path="url(#{cid})">{inner}</g>
  <path d="{VISOR}" fill="none" stroke="#111827" stroke-width="7" stroke-linejoin="round"/>
  <path d="M50 70 q2 -18 18 -22" stroke="#fff" stroke-width="3" fill="none" opacity=".45" stroke-linecap="round"/></svg>'''


def _chip(x, y, w, text, fill, ink, size=6.4, anchor_end=False):
  """A rounded HUD label; x is the left edge (or the right edge with anchor_end)."""
  x0 = x - w if anchor_end else x
  return (f'<rect x="{x0}" y="{y}" width="{w}" height="15" rx="7.5" fill="{fill}"/>'
          f'<text x="{x0 + w / 2}" y="{y + 10.2}" text-anchor="middle" font-size="{size}" font-weight="800" fill="{ink}" {FONT}>{text}</text>')


def _googly(x, y, r, ink):
  """Two googly eyes looking different ways."""
  return (f'<circle cx="{x - r * 1.05}" cy="{y}" r="{r}" fill="#fff" stroke="{ink}" stroke-width=".9"/>'
          f'<circle cx="{x + r * 1.05}" cy="{y}" r="{r}" fill="#fff" stroke="{ink}" stroke-width=".9"/>'
          f'<circle cx="{x - r * .75}" cy="{y + r * .35}" r="{r * .5}" fill="{ink}"/>'
          f'<circle cx="{x + r * .8}" cy="{y - r * .3}" r="{r * .5}" fill="{ink}"/>')


def _burger(x, y, s, ink):
  h = s / 2
  return (f'<path d="M{x - h} {y - s * .45} a{h} {s * .42} 0 0 1 {s} 0z" fill="#E2A04A" stroke="{ink}" stroke-width="1.2"/>'
          f'<rect x="{x - h - 2}" y="{y - s * .48}" width="{s + 4}" height="{s * .1}" rx="{s * .05}" fill="#6DB24A" stroke="{ink}" stroke-width=".8"/>'
          f'<rect x="{x - h}" y="{y - s * .38}" width="{s}" height="{s * .17}" rx="{s * .08}" fill="#7A4424" stroke="{ink}" stroke-width="1"/>'
          f'<rect x="{x - h}" y="{y - s * .22}" width="{s}" height="{s * .22}" rx="{s * .1}" fill="#E2A04A" stroke="{ink}" stroke-width="1.2"/>'
          + _googly(x, y - s * .66, s * .12, ink))


def _fries(x, y, s, red, ink):
  sticks = ''.join(f'<rect x="{x + dx * s - s * .05}" y="{y - s * (.98 - abs(dx) * .3)}" width="{s * .1}" height="{s * .5}" rx="{s * .03}" fill="#F2C53D" stroke="{ink}" stroke-width=".8"/>'
                   for dx in (-.26, -.13, 0, .13, .26))
  return (sticks + f'<polygon points="{x - s * .4},{y - s * .62} {x + s * .4},{y - s * .62} {x + s * .32},{y} {x - s * .32},{y}" fill="{red}" stroke="{ink}" stroke-width="1.2" stroke-linejoin="round"/>'
          + _googly(x, y - s * .36, s * .11, ink))


def _soda(x, y, s, red, ink):
  return (f'<line x1="{x + s * .06}" y1="{y - s * .88}" x2="{x + s * .2}" y2="{y - s * 1.15}" stroke="{ink}" stroke-width="2.2" stroke-linecap="round"/>'
          f'<polygon points="{x - s * .3},{y - s * .84} {x + s * .3},{y - s * .84} {x + s * .24},{y} {x - s * .24},{y}" fill="#FFFAF0" stroke="{ink}" stroke-width="1.2" stroke-linejoin="round"/>'
          f'<polygon points="{x - s * .28},{y - s * .62} {x + s * .28},{y - s * .62} {x + s * .26},{y - s * .4} {x - s * .26},{y - s * .4}" fill="{red}"/>'
          f'<rect x="{x - s * .34}" y="{y - s * .92}" width="{s * .68}" height="{s * .1}" rx="{s * .05}" fill="{red}" stroke="{ink}" stroke-width="1"/>'
          + _googly(x, y - s * .26, s * .1, ink))


def _glove(x, y, col, ink, flip=1):
  return f'''<g transform="translate({x} {y}) scale({flip} 1)">
    <rect x="-20" y="14" width="40" height="22" rx="4" fill="#FFFAF0" stroke="{ink}" stroke-width="1.6"/>
    <rect x="-27" y="-24" width="54" height="42" rx="19" fill="{col}" stroke="{ink}" stroke-width="1.6"/>
    <path d="M-27 -2 q-11 -3 -9 -15 q3 -9 13 -6" fill="{col}" stroke="{ink}" stroke-width="1.6"/>
    <path d="M-14 -15 q9 -6 21 -2" stroke="#fff" stroke-width="3" fill="none" opacity=".35" stroke-linecap="round"/></g>'''


def art_snacks(p):
  c, red, gold, ink, cream = p['color'], '#D23A2A', '#B9862A', '#2B1D12', '#FFFAF0'
  inner = f'''<rect width="400" height="250" fill="#CFE6F2"/>
  <circle cx="262" cy="74" r="14" fill="#FFE08A"/>
  <ellipse cx="160" cy="76" rx="24" ry="8" fill="#fff"/><ellipse cx="176" cy="71" rx="14" ry="7" fill="#fff"/>
  <path d="M0 128 Q90 100 190 118 T400 108 V250 H0Z" fill="#B7D894"/>
  <path d="M0 150 Q120 128 210 140 T400 136 V250 H0Z" fill="#9CC779"/>
  <path d="M58 112 l7 -16 l7 16z M300 108 l8 -18 l8 18z M330 114 l6 -13 l6 13z" fill="{c}"/>
  <polygon points="192,118 208,118 300,250 100,250" fill="#E7C98E"/>
  <path d="M200 124 V140 M200 152 V176 M200 192 V230" stroke="#F6E3B4" stroke-width="3" stroke-dasharray="6 7"/>
  {_burger(200, 136, 18, ink)}
  {_soda(232, 170, 30, red, ink)}
  <circle cx="232" cy="156" r="25" fill="none" stroke="{red}" stroke-width="3"/>
  {_fries(164, 178, 34, red, ink)}
  <circle cx="164" cy="162" r="27" fill="none" stroke="{c}" stroke-width="3"/>
  <g transform="translate(118 136) rotate(-10)"><polygon points="0,-12 4,-5 12,-7 7,0 12,7 4,6 0,13 -4,6 -12,7 -7,0 -12,-7 -4,-5" fill="{gold}" stroke="{ink}" stroke-width=".6" stroke-linejoin="round" transform="scale(1.9)"/>
    <text x="0" y="3" text-anchor="middle" font-size="8" font-weight="900" fill="{ink}" {FONT}>POW!</text></g>
  {_glove(88, 192, c, ink, -1)}{_glove(312, 192, red, ink)}
  {_chip(56, 50, 62, '12,480', ink, cream, 7)}
  {_chip(344, 50, 64, 'COMBO x4', gold, ink, 6.4, True)}
  <rect x="56" y="70" width="62" height="5" rx="2.5" fill="{ink}" opacity=".25"/><rect x="56" y="70" width="44" height="5" rx="2.5" fill="{c}"/>'''
  return _visor(inner, p['bg'], 'vz-snacks')


def art_wall(p):
  c, teal, ink, neon = p['color'], '#2F8F83', '#2A2522', '#26E3CF'
  # The projected picture: a monstera leaf in neon lines; the left half is already traced in pencil.
  leaf = 'M210 64 C168 70 150 112 160 150 C166 170 186 178 210 176 C236 178 256 166 262 146 C272 110 252 70 210 64Z'
  veins = 'M210 176 L210 74 M210 150 L176 130 M210 128 L170 104 M210 108 L180 84 M210 150 L246 128 M210 128 L250 104 M210 108 L240 84'
  cuts = 'M163 120 q14 2 22 -6 M166 146 q14 -2 22 -12 M257 120 q-14 2 -22 -6 M254 146 q-14 -2 -22 -12'
  crosses = ''.join(f'<path d="M{x - 6} {y} h12 M{x} {y - 6} v12" stroke="{neon}" stroke-width="1.6"/>'
                    for x, y in ((142, 56), (278, 56), (142, 186), (278, 186)))
  inner = f'''<rect width="400" height="250" fill="#E8DCC9"/>
  <rect x="44" y="40" width="58" height="80" fill="#D6E6EE" stroke="#BCA88C" stroke-width="5"/>
  <path d="M73 40 V120 M44 80 H102" stroke="#BCA88C" stroke-width="3"/>
  <rect x="0" y="196" width="400" height="60" fill="#C7AE8C"/><rect x="0" y="190" width="400" height="7" fill="#F4ECDF"/>
  <rect x="320" y="166" width="26" height="30" rx="3" fill="#7E9CB5" stroke="{ink}" stroke-width="1.2"/>
  <ellipse cx="333" cy="166" rx="13" ry="3.5" fill="#AFC6D8" stroke="{ink}" stroke-width="1.2"/>
  <rect x="142" y="56" width="136" height="130" fill="none" stroke="{neon}" stroke-width="1" stroke-dasharray="4 4" opacity=".7"/>
  {crosses}
  <path d="{leaf}" fill="{neon}" opacity=".08"/>
  <g fill="none" stroke="{neon}" stroke-width="2.2" stroke-linecap="round" opacity=".95"><path d="{leaf}"/><path d="{veins}"/><path d="{cuts}"/></g>
  <g clip-path="url(#vz-wall-half)"><g fill="none" stroke="#4A4440" stroke-width="1.3" stroke-linecap="round"><path d="{leaf}"/><path d="{veins}"/><path d="{cuts}"/></g></g>
  <defs><clipPath id="vz-wall-half"><rect x="140" y="60" width="72" height="120"/></clipPath></defs>
  <g transform="translate(212 118) rotate(-34)">
    <rect x="-4" y="12" width="8" height="74" fill="#F2B33D" stroke="{ink}" stroke-width="1.1"/>
    <path d="M-4 12 L0 0 L4 12Z" fill="#F3D9B5" stroke="{ink}" stroke-width="1.1" stroke-linejoin="round"/>
    <path d="M-1.4 4 L0 0 L1.4 4Z" fill="{ink}"/>
    <rect x="-15" y="50" width="30" height="40" rx="12" fill="#E9B48F" stroke="{ink}" stroke-width="1.3"/>
    <path d="M-15 60 h10 M-15 70 h11 M-15 80 h10" stroke="{ink}" stroke-width="1" stroke-linecap="round" opacity=".55"/>
    <path d="M6 54 q8 2 7 12" stroke="{ink}" stroke-width="1" fill="none" stroke-linecap="round" opacity=".55"/>
    <rect x="-11" y="88" width="22" height="30" fill="#5B6B7A" stroke="{ink}" stroke-width="1.3"/></g>
  {_chip(50, 170, 96, '&#128274; Locked · 120 × 115 cm', c, '#FFFAF4', 6)}
  {_chip(348, 50, 66, 'Square B3 · 7/12', '#FAF7F2', ink, 6, True)}
  {_chip(348, 70, 66, 'A/X or pinch: hide', teal, '#fff', 5.6, True)}'''
  return _visor(inner, p['bg'], 'vz-wall')


def art_stage(p):
  c, amber, dark, cream = p['color'], '#C27400', '#0B0B0D', '#F3EFE8'
  heads = ''
  for row, (y, r, gap) in enumerate(((104, 4.2, 14), (122, 5.4, 17), (143, 6.8, 21), (168, 8.6, 26))):
    x, i = 22 + (row % 2) * gap / 2, 0
    while x < 380:
      bright = (i * 7 + row * 3) % 5
      tone = '#3A3640' if bright else '#6A5E52'
      heads += (f'<rect x="{x - r * 1.25}" y="{y + r * .6}" width="{r * 2.5}" height="{r * 2.2}" rx="{r}" fill="{tone}"/>'
                f'<circle cx="{x}" cy="{y}" r="{r}" fill="{tone}"/>')
      if (i + row) % 9 == 4:
        heads += f'<rect x="{x + r * .3}" y="{y + r * 1.2}" width="{r * .9}" height="{r * 1.3}" rx="1" fill="#9FD3FF"/>'
      x, i = x + gap, i + 1
  arc = 2 * 3.1416 * 14
  inner = f'''<rect width="400" height="250" fill="{dark}"/>
  <polygon points="168,34 232,34 330,214 70,214" fill="#FFF3D6" opacity=".07"/>
  <rect x="138" y="46" width="124" height="40" rx="3" fill="#17161A" stroke="#2C2A30"/>
  <text x="200" y="64" text-anchor="middle" font-size="9" font-weight="800" fill="{c}" letter-spacing=".4" {FONT}>WHY SMALL</text>
  <text x="200" y="77" text-anchor="middle" font-size="9" font-weight="800" fill="{c}" letter-spacing=".4" {FONT}>TEAMS WIN</text>
  {heads}
  <ellipse cx="200" cy="222" rx="120" ry="30" fill="{c}"/>
  <ellipse cx="200" cy="222" rx="120" ry="30" fill="none" stroke="#FF6A5C" stroke-width="1.4" opacity=".6"/>
  <g transform="translate(62 160) rotate(-8)"><rect width="62" height="40" rx="4" fill="{cream}" stroke="#C9C1B4"/>
    <text x="7" y="12" font-size="5.2" font-weight="800" fill="{amber}" letter-spacing=".6" {FONT}>CARD 3 / 8</text>
    <rect x="7" y="18" width="46" height="3.4" rx="1.7" fill="#9B958D"/><rect x="7" y="25" width="38" height="3.4" rx="1.7" fill="#9B958D"/>
    <rect x="7" y="32" width="28" height="3.4" rx="1.7" fill="#9B958D"/></g>
  <g transform="translate(56 48)"><rect width="66" height="40" rx="8" fill="#17161A" stroke="#2C2A30"/>
    <text x="8" y="12" font-size="5" font-weight="800" fill="#9B958D" letter-spacing=".8" {FONT}>PACE</text>
    <path d="M14 33 a19 19 0 0 1 38 0" fill="none" stroke="#2C2A30" stroke-width="4"/>
    <path d="M14 33 a19 19 0 0 1 30 -15" fill="none" stroke="#18845A" stroke-width="4"/>
    <line x1="33" y1="33" x2="42" y2="19" stroke="{cream}" stroke-width="1.6" stroke-linecap="round"/>
    <text x="62" y="12" text-anchor="end" font-size="5.6" font-weight="800" fill="{cream}" {FONT}>142 wpm</text></g>
  <g transform="translate(304 68)"><circle r="18" fill="#17161A" stroke="#2C2A30"/>
    <circle r="14" fill="none" stroke="#2C2A30" stroke-width="4"/>
    <circle r="14" fill="none" stroke="{c}" stroke-width="4" stroke-linecap="round" stroke-dasharray="{round(arc * .84, 1)} {round(arc, 1)}" transform="rotate(-90)"/>
    <text y="3.4" text-anchor="middle" font-size="9" font-weight="800" fill="{cream}" {FONT}>84</text></g>
  {_chip(244, 92, 100, 'Nice pause &#10003;', '#18845A', '#fff', 6)}'''
  return _visor(inner, p['bg'], 'vz-stage')


ARTS = {'monshop': art_monshop, 'family': art_family, 'planplate': art_planplate,'varnote': art_varnote, 'blog': art_blog, 'map': art_map, 'bun': art_bun,
        'piano': art_piano, 'pound': art_pound, 'parrot': art_parrot, 'resto': art_resto,
        'screenplay': art_screenplay, 'lyrics': art_lyrics, 'rooms': art_rooms, 'models': art_models,
        'feedback': art_feedback, 'boxing': art_boxing, 'cubes': art_cubes, 'party': art_party, 'pan': art_pan,
        'personal': art_personal, 'monitor': art_monitor, 'hotel': art_hotel, 'toon': art_toon,
        'snacks': art_snacks, 'wall': art_wall, 'stage': art_stage}


def art(p):
  return ARTS[p['art']](p)


def url(p):
  """Live address, or the Work page while a project is still launching."""
  return 'https://' + p['domain'] if p.get('domain') else '#work'


# ------------------------------------------------------------------ case studies + index

def esc(s):
  return (str(s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;'))


def split_blurb(text):
  """(first sentence, the rest). The first sentence doubles as the one-line summary in the index."""
  for i in range(len(text) - 1):
    if text[i] in '.!?' and text[i + 1] == ' ':
      return text[:i + 1], text[i + 2:]
  return text, ''


def picks(n=3, exclude=()):
  """n live projects picked at random: the home page shows three, different on every visit (and on Shuffle)."""
  pool = [p for p in PROJECTS if p.get('domain') and p['key'] not in exclude]
  if len(pool) < n:
    pool = [p for p in PROJECTS if p.get('domain')]
  out = []
  while pool and len(out) < n:
    out.append(pool.pop(int(random.random() * len(pool))))
  return out


def in_category(key):
  return [p for p in PROJECTS if p['cat'] == key]


def live_count():
  return len([p for p in PROJECTS if p.get('domain')])


def film(p):
  """The project's one-minute film on the Addanapp YouTube channel, or ''."""
  vid = VIDEOS.get(p['key'])
  return 'https://www.youtube.com/watch?v=' + vid if vid else ''


def shot_html(p):
  """The preview: an SVG mini-UI in the product's colours, or a real screenshot in a browser frame ('art': 'shot').
  Static markup made here from fixed data (no visitor input), drawn into Components/Shot."""
  if p['art'] != 'shot':
    return art(p)
  return (f'<div class="pf-screen" aria-hidden="true"><div class="win">'
          f'<div class="bar"><i></i><i></i><i></i><span>{esc(p["domain"])}</span></div>'
          f'<img src="_/theme/pf/{p["key"]}.jpg" alt="" loading="lazy" decoding="async" width="720" height="450"></div></div>')
