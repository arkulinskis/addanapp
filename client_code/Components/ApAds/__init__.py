from anvil import *
from anvil.js import window

from ._anvil_designer import ApAdsTemplate
from ... import apps_data, router, state, ui

PRIORITY = {1: '🚀 Run first', 2: '⏭ Next', 3: '🕒 Later'}


class ApAds(ApAdsTemplate):
    """#apps/ads[/<doc>]: ready-to-run ads per app (APP_MAKER/ads, pushed by the PC). doc = GUIDE | <app key>.
    The server renders each page (api_ads.app_html, escaped); this view adds Copy buttons and the comment box, which
    files a "Changes for Claude" request on the app (apps_add_change), like every other change."""

    def __init__(self, arg=None, **properties):
        super().__init__(**properties)
        self.doc = arg or state.store_get('apps.adsDoc', 'GUIDE')
        self.data: dict = {}
        self.docs.add_event_handler("x-pick", self._pick)
        state.set_control_attr(self.concept_dd, "aria-label", "Which ad")
        state.set_control_attr(self.comment_box, "aria-label", "What to change")
        self.dom_nodes["md"].addEventListener("click", self._click)
        self._load()

    def set_arg(self, arg):
        if arg and arg != self.doc:
            self.doc = arg
            self._load()

    def _pick(self, key, **event_args):
        router.go("apps/ads/" + key)

    def _load(self):
        res = apps_data.call('apps_ads', self.doc)
        if res is ui.FAIL:
            return
        self.data = res
        self.doc = res['name']
        state.store_set('apps.adsDoc', self.doc)
        self.redraw()

    def redraw(self, key=None):
        d = self.data
        if not d:
            return
        q = apps_data.query()
        apps = [a for a in d.get('apps') or [] if not q or q in (a.get('name', '') + ' ' + a.get('key', '')).lower()]
        items = [{"key": "GUIDE", "label": "📘 How to run your ads", "on": self.doc == 'GUIDE'}]
        for pr in (1, 2, 3):
            group = [a for a in apps if (a.get('priority') or 3) == pr]
            if group:
                items.append({"grp": PRIORITY[pr]})
                items += [{"key": a['key'], "label": a.get('name') or a['key'], "cnt": a.get('price') or '',
                           "on": self.doc == a['key'], "title": a.get('offer') or ''} for a in group]
        self.docs.items = items
        app = self.doc != 'GUIDE'
        self.comment_part.visible = app and not d.get('missing')
        self.concept_dd.items = [("All ads", "all")] + [(lbl, cid) for cid, lbl in d.get('concepts') or []]
        links = []
        if app:
            p = apps_data.project(self.doc) if hasattr(apps_data, 'project') else None
            if p:
                links = apps_data.links(p) + [{"label": "Checklist", "href": "#app/" + window.encodeURIComponent(p['key'])}]
        links.append({"label": "Meta Ads Manager ↗", "href": "https://adsmanager.facebook.com/"})
        js = apps_data.js()
        if js:
            js.links(self.dom_nodes["links"], links)
        # the server builds this HTML from escaped text (server_code/api_ads.py)
        self.dom_nodes["md"].innerHTML = d.get('html') or (
            '<p class="muted">These ads aren’t on Addanapp yet. The PC sends them with the next push (python ads/publish.py).</p>')

    def _click(self, ev):
        b = ev.target.closest(".ad-copy") if ev.target and hasattr(ev.target, 'closest') else None
        if not b:
            return
        text = b.getAttribute("data-copy") or ''
        try:
            window.navigator.clipboard.writeText(text)
            b.textContent = "Copied ✓"
            window.setTimeout(lambda: setattr(b, 'textContent', 'Copy'), 1400)
        except Exception:
            state.toast("Copy didn't work here: select the text instead.", "error")

    @handle("send_button", "click")
    def send_button_click(self, **event_args):
        text = (self.comment_box.text or '').strip()
        if not text or self.doc == 'GUIDE':
            state.toast("Write what to change first.", "error")
            return
        which = self.concept_dd.selected_value or 'all'
        msg = "Ads (%s): %s" % ("all ads" if which == 'all' else "ad " + which, text)
        if apps_data.add_change(self.doc, msg) is not ui.FAIL:
            self.comment_box.text = ''
