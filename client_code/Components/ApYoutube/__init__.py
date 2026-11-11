import datetime

from anvil import *
import anvil.js
from anvil.js import window

from ._anvil_designer import ApYoutubeTemplate
from ... import apps_data, apps_fmt, state, ui

SRC = {'YT_SEARCH': 'YouTube search', 'SHORTS': 'Shorts feed', 'SUBSCRIBER': 'Subscribers', 'RELATED_VIDEO': 'Suggested videos',
       'EXT_URL': 'Other websites', 'NO_LINK_OTHER': 'Direct / unknown', 'PLAYLIST': 'Playlists', 'YT_CHANNEL': 'Channel page',
       'YT_OTHER_PAGE': 'Other YouTube pages', 'NOTIFICATION': 'Notifications', 'END_SCREEN': 'End screens', 'ANNOTATION': 'Cards',
       'ADVERTISING': 'Ads', 'HASHTAGS': 'Hashtags'}
DEV = {'MOBILE': 'Phone', 'DESKTOP': 'Computer', 'TABLET': 'Tablet', 'TV': 'TV', 'GAME_CONSOLE': 'Game console', 'UNKNOWN_PLATFORM': 'Unknown'}
KIND = {'pitch': 'Pitch', 'reel': 'Reel'}


def country(code):
    try:
        return window.Intl.DisplayNames(None, {"type": "region"}).of(code)
    except Exception:
        return code


class ApYoutube(ApYoutubeTemplate):
    """#apps/youtube: the channel's numbers (the PC fetches them with youtube/stats.py): subscribers, views, watch time
    over time, views by app, traffic sources, countries, devices and every video. Update asks the PC for fresh numbers."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.ui: dict = dict({'days': 28, 'kind': 'all', 'app': None, 'sort': 'views', 'dir': -1}, **(apps_data.sget('apps.yt', None) or {}))
        self.all_apps = self.all_vids = False
        self.y: dict = {}
        self.shown = False
        self.days.add_event_handler("x-pick", self._days)
        self.kinds.add_event_handler("x-pick", self._kind)
        self.app_bars.add_event_handler("x-pick", self._app)
        res = apps_data.call('apps_youtube')
        self.y = res if res is not ui.FAIL else {}
        self.redraw()

    @handle("", "show")
    def form_show(self, **event_args):
        self.shown = True
        self._charts()

    def _save(self):
        apps_data.sset('apps.yt', {k: self.ui[k] for k in ('days', 'kind', 'sort', 'dir')})

    def name_of(self, k):
        if not k:
            return 'Other'
        p = apps_data.project(k) or apps_data.project_by_biz(k)
        return p['name'] if p else k

    def _daily(self):
        a = self.y.get('analytics') or {}
        start = ui.date_iso(ui.now_local().date() - datetime.timedelta(days=int(self.ui['days'])))
        if a.get('daily'):
            return 'analytics', [r for r in a['daily'] if r.get('day', '') >= start]
        h = self.y.get('history') or {}
        days = sorted(h.keys())
        rows = []
        for i in range(1, len(days)):
            if days[i] < start:
                continue
            a0, a1 = h[days[i - 1]], h[days[i]]
            rows.append({'day': days[i], 'views': max(0, (a1.get('views') or 0) - (a0.get('views') or 0)), 'subscribers': a1.get('subscribers')})
        return 'snapshots', rows

    def redraw(self, key=None):
        L = self.y.get('latest')
        self.none.visible = not L
        self.body.visible = bool(L)
        self.days.items = [{"key": d, "label": "1 year" if d == 365 else "%d days" % d, "on": self.ui['days'] == d} for d in (7, 28, 90, 365)]
        if not L:
            self.dom_nodes["channel"].textContent = "YouTube"
            return
        A = self.y.get('analytics') if (self.y.get('analytics') or {}).get('daily') else None
        ch = L.get('channel') or {}
        self.dom_nodes["channel"].textContent = "▶ " + (ch.get('title') or 'YouTube')
        self.dom_nodes["when"].textContent = "numbers from " + apps_fmt.ago(L.get('updated'))
        self.dom_nodes["studio"].setAttribute("href", "https://studio.youtube.com/channel/%s/analytics" % ch.get('id', ''))
        err = (self.y.get('analytics') or {}).get('error')
        self.dom_nodes["conn"].textContent = (("YouTube Analytics is connected." if A else "YouTube Analytics isn't connected: daily views come from the PC's daily snapshots. "
                                               "To connect it, on the PC run: python youtube/ytrun.py youtube/stats.py --connect")
                                              + ((" Last Analytics fetch failed: " + err) if err else ""))
        vids = L.get('videos') or []
        pub = [v for v in vids if v.get('privacy') == 'public']
        src, D = self._daily()
        hist = sorted((self.y.get('history') or {}).keys())
        first = (self.y.get('history') or {}).get(hist[0]) if hist else None
        period = "last %d days" % int(self.ui['days'])

        def ssum(k):
            return sum(r.get(k) or 0 for r in D)

        def avg(a):
            return round(sum(v.get('views') or 0 for v in a) / len(a)) if a else 0
        pitch = [v for v in pub if v.get('kind') == 'pitch']
        reels = [v for v in pub if v.get('kind') == 'reel']
        subs = ch.get('subscribers') or 0
        tiles = [{"k": "Subscribers", "v": apps_fmt.num(subs),
                  "d": ("%+d since %s" % (subs - (first.get('subscribers') or 0), apps_fmt.day_label(hist[0]))) if first and len(hist) > 1 else ""},
                 {"k": "Total views", "v": apps_fmt.num(ch.get('views')), "d": "%d public videos" % len(pub)},
                 {"k": "Views, " + period, "v": apps_fmt.num(ssum('views')) if (src == 'analytics' or D) else "–",
                  "d": "from YouTube Analytics" if src == 'analytics' else ("from %d day(s) of snapshots" % len(D) if D else "needs 2 days of snapshots")}]
        if A:
            tiles.append({"k": "Watch time, " + period, "v": apps_fmt.num(round(ssum('estimatedMinutesWatched') / 60)) + " h",
                          "d": "%s subscribers gained" % apps_fmt.num(ssum('subscribersGained'))})
        tiles += [{"k": "Avg views per pitch", "v": apps_fmt.num(avg(pitch)), "d": "%d pitch videos" % len(pitch)},
                  {"k": "Avg views per reel", "v": apps_fmt.num(avg(reels)), "d": "%d reels" % len(reels)},
                  {"k": "Likes", "v": apps_fmt.num(sum(v.get('likes') or 0 for v in pub)), "d": "%s comments" % apps_fmt.num(sum(v.get('comments') or 0 for v in pub))}]
        self.tiles.items = tiles
        self.dom_nodes["views_sub"].textContent = ("YouTube Analytics, " + period) if src == 'analytics' else \
            "From the PC's daily snapshots (%d so far)." % len(hist)
        self.dom_nodes["subs_h"].textContent = "Subscribers gained per day" if A else "Subscribers"
        self.dom_nodes["subs_sub"].textContent = ("Gained minus lost, " + period) if A else "Total at each daily snapshot"
        self.watch_card.visible = bool(A)
        self.dom_nodes["watch_sub"].textContent = "Hours watched, " + period
        self.D, self.A, self.hist, self.src = D, A, hist, src
        # views by app, pitch + reels stacked
        q = apps_data.query()
        by: dict = {}
        for v in pub:
            k = v.get('app') or ''
            b = by.setdefault(k, {'app': k, 'pitch': 0, 'reel': 0, 'other': 0, 'n': 0})
            kind = v.get('kind') if v.get('kind') in ('pitch', 'reel') else 'other'
            b[kind] += v.get('views') or 0
            b['n'] += 1
        apps = sorted(by.values(), key=lambda b: -(b['pitch'] + b['reel'] + b['other']))
        amax = max([1] + [b['pitch'] + b['reel'] + b['other'] for b in apps])
        show = [b for b in apps if not q or q in self.name_of(b['app']).lower()]
        self.app_bars.items = [{"key": b['app'], "label": self.name_of(b['app']), "val": apps_fmt.num(b['pitch'] + b['reel'] + b['other']),
                                "parts": [{"w": b[k] * 100.0 / amax, "color": c} for k, c in (('pitch', 'var(--ap-s1)'), ('reel', 'var(--ap-s2)'), ('other', 'var(--ap-s3)')) if b[k]],
                                "tip": "%s\nPitch: %s\nReels: %s%s\n%d videos" % (self.name_of(b['app']), apps_fmt.num(b['pitch']), apps_fmt.num(b['reel']),
                                                                                 ("\nOther: " + apps_fmt.num(b['other'])) if b['other'] else '', b['n']),
                                "on": self.ui['app'] == b['app'], "pick": True}
                               for b in show[:999 if self.all_apps else 15]]
        self.all_apps_button.visible = len(show) > 15
        self.all_apps_button.text = "Show top 15" if self.all_apps else "Show all %d" % len(show)
        for card, panel, rows, k, namer in ((self.src_card, self.src_bars, (A or {}).get('sources'), 'insightTrafficSourceType', lambda x: SRC.get(x, x)),
                                            (self.country_card, self.country_bars, (A or {}).get('countries'), 'country', country),
                                            (self.device_card, self.device_bars, (A or {}).get('devices'), 'deviceType', lambda x: DEV.get(x, x))):
            card.visible = bool(A)
            rows = rows or []
            mx = max([1] + [r.get('views') or 0 for r in rows])
            tot = sum(r.get('views') or 0 for r in rows) or 1
            panel.items = [{"key": str(r.get(k)), "label": namer(r.get(k)), "val": window.apps.short(r.get('views') or 0) if window.apps else str(r.get('views')),
                            "parts": [{"w": (r.get('views') or 0) * 100.0 / mx, "color": "var(--ap-s1)"}],
                            "tip": "%s\n%s views (%d%%)" % (namer(r.get(k)), apps_fmt.num(r.get('views')), round((r.get('views') or 0) * 100.0 / tot))}
                           for r in rows[:10]]
        self._videos(vids, A)
        if self.shown:
            self._charts()

    def _videos(self, vids, A):
        q = apps_data.query()
        per = {r.get('video'): r for r in (A or {}).get('per_video') or []}
        k, app = self.ui['kind'], self.ui['app']
        self.kinds.items = [{"key": x, "label": label, "on": k == x} for x, label in (('all', 'All'), ('pitch', 'Pitch videos'), ('reel', 'Reels'), ('other', 'Other'))]
        self.app_filter_button.visible = app is not None
        self.app_filter_button.text = "✕ " + self.name_of(app) if app is not None else ""
        rows: list = []
        for v in vids:
            kind = v.get('kind') if v.get('kind') in ('pitch', 'reel') else 'other'
            if k != 'all' and kind != k:
                continue
            if app is not None and (v.get('app') or '') != app:
                continue
            if q and q not in (v.get('title', '') + ' ' + self.name_of(v.get('app'))).lower():
                continue
            r = per.get(v.get('id')) or {}
            rows.append(dict(v, _app=self.name_of(v.get('app')), _kind=kind, _pct=r.get('averageViewPercentage')))
        s, d = str(self.ui['sort']), int(self.ui['dir'])
        text_cols = ('title', '_app', '_kind', 'published')

        def vkey(v):
            x = v.get(s)
            if s in text_cols:
                return (str(x or '').lower(), 0.0)
            try:
                return ('', float(x))
            except (TypeError, ValueError):
                return ('', -1.0)
        rows.sort(key=vkey, reverse=d < 0)
        hist = self.y.get('history') or {}
        days = sorted(hist.keys())[-30:]
        self.dom_nodes["vid_count"].textContent = "%d videos" % len(rows) + (" · % watched = average share of the video people watched (12 months)" if A else "")
        cols: list = [{"key": "thumb", "label": ""}, {"key": "title", "label": "Title", "sort": 1}, {"key": "_app", "label": "App", "sort": 1},
                {"key": "_kind", "label": "Type", "sort": 1}, {"key": "published", "label": "Published", "num": 1, "sort": 1},
                {"key": "views", "label": "Views", "num": 1, "sort": 1}, {"key": "trend", "label": "Trend"},
                {"key": "likes", "label": "Likes", "num": 1, "sort": 1}, {"key": "comments", "label": "Comments", "num": 1, "sort": 1}]
        if A:
            cols.append({"key": "_pct", "label": "% watched", "num": 1, "sort": 1})
        for c in cols:
            if c['key'] == s:
                c['on'] = d
        out = []
        for v in rows[:9999 if self.all_vids else 50]:
            p = apps_data.project(v.get('app') or '') or apps_data.project_by_biz(v.get('app') or '')
            trend = [((hist[dd].get('videos') or {}).get(v.get('id')) or [None])[0] for dd in days]
            row = [{"img": v.get('thumb') or '', "alt": ""},
                   {"text": v.get('title'), "href": "https://youtu.be/" + str(v.get('id')), "tag": "" if v.get('privacy') == 'public' else v.get('privacy')},
                   {"text": v['_app'], "href": "#app/" + window.encodeURIComponent(p['key'])} if p else (v['_app'] if v.get('app') else '–'),
                   KIND.get(v['_kind'], 'Other'), v.get('published') or '', {"text": apps_fmt.num(v.get('views')), "bold": True},
                   {"spark": [x for x in trend if x is not None]}, apps_fmt.num(v.get('likes')), apps_fmt.num(v.get('comments'))]
            if A:
                row.append(("%d%%" % round(float(v['_pct']))) if v.get('_pct') is not None else '–')
            out.append(row)
        js = apps_data.js()
        if js:
            js.table(self.dom_nodes["table"], cols, out, {"sort": anvil.js.report_exceptions(self._sort)}, "ap-yt-table")
        self.all_vids_button.visible = len(rows) > 50
        self.all_vids_button.text = "Show top 50" if self.all_vids else "Show all %d" % len(rows)

    def _charts(self):
        js = apps_data.js()
        if not js or not self.y.get('latest'):
            return
        D, A, hist = self.D, self.A, self.hist
        h = self.y.get('history') or {}
        big = int(self.ui['days']) > 28 or len(D) > 31
        js.chart(self.dom_nodes["views_chart"], [{"x": apps_fmt.day_label(r['day']), "y": r.get('views') or 0,
                                                 "tip": "%s\n%s views" % (apps_fmt.day_label(r['day']), apps_fmt.num(r.get('views')))} for r in D],
                 'area' if big else 'bars', 'var(--ap-s1)')
        if A:
            js.chart(self.dom_nodes["subs_chart"], [{"x": apps_fmt.day_label(r['day']), "y": max(0, (r.get('subscribersGained') or 0) - (r.get('subscribersLost') or 0)),
                                                    "tip": "%s\n+%s gained, %s lost" % (apps_fmt.day_label(r['day']), apps_fmt.num(r.get('subscribersGained')), apps_fmt.num(r.get('subscribersLost')))}
                                                   for r in D], 'bars', 'var(--ap-s1)')
            js.chart(self.dom_nodes["watch_chart"], [{"x": apps_fmt.day_label(r['day']), "y": (r.get('estimatedMinutesWatched') or 0) / 60.0,
                                                     "tip": "%s\n%.1f hours watched" % (apps_fmt.day_label(r['day']), (r.get('estimatedMinutesWatched') or 0) / 60.0)}
                                                    for r in D], 'area' if int(self.ui['days']) > 28 else 'bars', 'var(--ap-s1)')
        else:
            js.chart(self.dom_nodes["subs_chart"], [{"x": apps_fmt.day_label(d), "y": h[d].get('subscribers') or 0,
                                                    "tip": "%s\n%s subscribers" % (apps_fmt.day_label(d), apps_fmt.num(h[d].get('subscribers')))} for d in hist],
                     'area', 'var(--ap-s1)')

    def _days(self, key, **event_args):
        self.ui['days'] = key
        self._save()
        self.redraw()

    def _kind(self, key, **event_args):
        self.ui['kind'] = key
        self._save()
        self.redraw()

    def _app(self, key, **event_args):
        self.ui['app'] = None if self.ui['app'] == key else key
        self.redraw()

    def _sort(self, key):
        self.ui['dir'] = -int(self.ui['dir']) if self.ui['sort'] == key else (1 if key in ('title', '_app', '_kind') else -1)
        self.ui['sort'] = key
        self._save()
        self.redraw()

    @handle("app_filter_button", "click")
    def app_filter_button_click(self, **event_args):
        self.ui['app'] = None
        self.redraw()

    @handle("all_apps_button", "click")
    def all_apps_button_click(self, **event_args):
        self.all_apps = not self.all_apps
        self.redraw()

    @handle("all_vids_button", "click")
    def all_vids_button_click(self, **event_args):
        self.all_vids = not self.all_vids
        self.redraw()

    @handle("update_button", "click")
    def update_button_click(self, **event_args):
        apps_data.queue('yt')
