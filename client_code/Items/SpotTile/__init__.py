from anvil import *

from ._anvil_designer import SpotTileTemplate
from ... import i18n, portfolio, state
from ...i18n import tp
from ...Components.Shot import BY_KEY


class SpotTile(SpotTileTemplate):
    """One of the three side-by-side spotlight cards on the Work page: preview, name, the blurb's first sentence, tags,
    film + live link, and "Details", which opens the project's row in the index below (raises x-open on the panel).
    item = {key, i, n}: i = position in the shuffled deck (for the 01, 02... number), n = slot 0-2 (entrance stagger)."""

    def __init__(self, **properties):
        super().__init__(**properties)
        p = BY_KEY[self.item["key"]]
        self.p = p
        state.set_attr(self.card, "data-pf", p["key"])
        state.set_attr(self.card, "style", "--n:%d" % self.item.get("n", 0))
        self.shot.project_key = p["key"]
        self.dom_nodes["num"].textContent = "%02d" % (self.item.get("i", 0) + 1)
        self.dom_nodes["cat"].textContent = portfolio.CAT[p['cat']]
        self.dom_nodes["name"].textContent = p['name']
        self.dom_nodes["hook"].textContent = portfolio.split_blurb(tp(p['blurb']))[0]
        self.tags.items = [{"text": tp(x)} for x in p['tags'][:3]]
        film = portfolio.film(p)
        self.watch.visible = bool(film)
        if film:
            state.set_attr(self.watch, "href", film)
            state.set_attr(self.watch, "aria-label", tp('Watch the {name} film on YouTube', name=p['name']))
        live = bool(p.get('domain'))
        self.visit.visible = live
        if live:
            state.set_attr(self.visit, "href", portfolio.url(p))
            state.set_attr(self.visit, "aria-label", tp("Visit {domain}", domain=p["domain"]))
        i18n.apply(self)
        self.details_button.tooltip = tp('Show {name} in the full index', name=p['name'])

    @handle("details_button", "click")
    def details_button_click(self, **event_args):
        if self.parent:
            self.parent.raise_event("x-open", key=self.p["key"])
