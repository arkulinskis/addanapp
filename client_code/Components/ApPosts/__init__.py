from anvil import *
from anvil.js import window

from ._anvil_designer import ApPostsTemplate
from ... import apps_data, router, state, ui


def has_promo(p):
    c = p.get('promo') or {}
    return bool(p.get('video') or c.get('linkedin') or c.get('youtube'))


def counts(p):
    m = p.get('posted') or {}
    c = p.get('promo') or {}
    li = len([k for k, v in m.items() if k.startswith('li') and v])
    yt = len([k for k, v in m.items() if k.startswith('yt') and v])
    return li, c.get('linkedin') or 0, yt, (c.get('youtube') or 0) + (1 if p.get('video') else 0)


def full(key):
    """apps_project(key), kept for this visit (posts + video kit are the long texts)."""
    cache = apps_data._d.setdefault("full", {})
    if key not in cache:
        res = apps_data.call('apps_project', key)
        if res is ui.FAIL:
            return None
        cache[key] = res
    return cache[key]


class ApPosts(ApPostsTemplate):
    """#apps/posts[/<key>]: suggested LinkedIn posts, YouTube scripts and the pitch-video upload kit for every app,
    each with Copy and a Posted / Published tick. The list on the left picks the app."""

    def __init__(self, arg=None, **properties):
        super().__init__(**properties)
        self.key = arg or state.store_get('apps.postKey', '')
        self.apps.add_event_handler("x-pick", self._pick)
        self.redraw()

    def set_arg(self, arg):
        if arg and arg != self.key:
            self.key = arg
            self.redraw()

    def _pick(self, key, **event_args):
        router.go("apps/posts/" + window.encodeURIComponent(key))

    def redraw(self, key=None):
        vis = apps_data.visible()
        lst = sorted([p for p in vis if has_promo(p)], key=lambda p: p['name'].lower())
        none = [p['name'] for p in vis if not has_promo(p)]
        if not any(p['key'] == self.key for p in lst):
            self.key = lst[0]['key'] if lst else ''
        state.store_set('apps.postKey', self.key)
        tot = [0, 0, 0, 0]
        for p in [x for x in (apps_data.board() or {}).get('projects') or [] if has_promo(x)]:
            c = counts(p)
            tot = [tot[i] + c[i] for i in range(4)]
        self.dom_nodes["intro"].textContent = ("Suggested posts and video scripts for every app: %d/%d LinkedIn posts posted, %d/%d videos published. "
                                               "Copy a post, put it on LinkedIn, then tick Posted (the first tick also ticks the app's "
                                               "LinkedIn / YouTube step). Lines with 💡 are notes for you and aren't copied." % tuple(tot))
        items = []
        for p in lst:
            li, li_t, yt, yt_t = counts(p)
            lv = p.get('live') or {}
            items.append({"key": p['key'], "label": p['name'], "cnt": "in %d/%d · ▶ %d/%d" % (li, li_t, yt, yt_t), "on": p['key'] == self.key,
                          "done": li + yt == li_t + yt_t, "dot": ('ok' if lv.get('ok') else 'bad') if p.get('url') and p.get('live') else ''})
        self.apps.items = items
        self.dom_nodes["none_list"].textContent = ("No posts written yet: " + ", ".join(none)) if none else ""
        self._pane()

    def _pane(self):
        self.pane.clear()
        p = apps_data.project(self.key)
        if not p:
            self.name.text = "No posts written yet"
            self.warn.visible = False
            return
        self.name.text = p['name']
        js = apps_data.js()
        if js:
            js.links(self.dom_nodes["links"], apps_data.links(p) + [{"label": "Checklist", "href": "#app/" + window.encodeURIComponent(p['key'])}])
        lv = p.get('live') or {}
        warn = ""
        if not p.get('url'):
            warn = "⚠️ No live address yet: the posts say [link]. Publish first, then swap in the address."
        elif p.get('live') and not lv.get('ok'):
            warn = "⚠️ The live address isn't answering right now. Check the link works before you post."
        self.warn.visible = bool(warn)
        self.dom_nodes["warn_text"].textContent = warn
        li, li_t, yt, yt_t = counts(p)
        self.dom_nodes["count"].textContent = "%d/%d LinkedIn posted · %d/%d videos published" % (li, li_t, yt, yt_t)
        f = full(p['key'])
        if f is None:
            return
        from ..ApVideoKit import ApVideoKit
        from ..ApPostList import ApPostList
        if p.get('video'):
            self.pane.add_component(ApVideoKit(project=p, kit=f.get('video_kit')))
        self.pane.add_component(ApPostList(project=p, promo=f.get('promo')))
