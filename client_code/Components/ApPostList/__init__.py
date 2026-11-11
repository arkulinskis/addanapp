from anvil import *

from ._anvil_designer import ApPostListTemplate


class ApPostList(ApPostListTemplate):
    """An app's suggested LinkedIn posts and YouTube scripts, each with Copy and a Posted / Published tick.
    project = the app; promo = {intro, items}; closed = YouTube scripts start folded."""

    def __init__(self, project=None, promo=None, closed=False, **properties):
        super().__init__(**properties)
        p = project or {}
        d = promo or {}
        posted = p.get('posted') or {}
        items = d.get('items') or []
        li = [x for x in items if x.get('kind') == 'linkedin']
        yt = [x for x in items if x.get('kind') == 'youtube']
        self.intro.visible = bool(d.get('intro'))
        self.dom_nodes["intro_text"].textContent = d.get('intro') or ''
        self.li_h.visible = bool(li)
        self.yt_h.visible = bool(yt)
        self.none.visible = not items
        self.li.items = [{"key": p.get('key'), "post": x, "on": posted.get(x['id']) or '', "closed": closed} for x in li]
        self.yt.items = [{"key": p.get('key'), "post": x, "on": posted.get(x['id']) or '', "closed": closed} for x in yt]
