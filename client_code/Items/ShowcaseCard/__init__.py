from anvil import *

from ._anvil_designer import ShowcaseCardTemplate
from ... import i18n, portfolio, state
from ...i18n import tp
from ...Components.Shot import BY_KEY


def fill_project(form, p):
    """What a case-study card and an opened index row share: the rest of the blurb, what we built, tags, film, link."""
    rest = portfolio.split_blurb(tp(p['blurb']))[1]
    form.rest.text = rest
    form.rest_box.visible = bool(rest)
    form.built.items = [{"text": tp(b)} for b in p['built']]
    form.tags.items = [{"text": tp(x)} for x in p['tags']]
    film = portfolio.film(p)
    form.watch.visible = bool(film)
    if film:
        state.set_attr(form.watch, "href", film)
        state.set_attr(form.watch, "aria-label", tp('Watch the {name} film on YouTube', name=p['name']))
    live = bool(p.get('domain'))
    form.visit.visible = live
    form.soon.visible = not live
    if live:
        state.set_attr(form.visit, "href", portfolio.url(p))
        form.visit_label.text = tp("Visit {domain}", domain=p["domain"])


class ShowcaseCard(ShowcaseCardTemplate):
    """A home-page case study. item = {key, i}: alternate cards put the preview on the other side."""

    def __init__(self, **properties):
        super().__init__(**properties)
        p = BY_KEY[self.item["key"]]
        i = self.item.get("i", 0)
        self.card.classes["flip"] = bool(i % 2)
        state.set_attr(self.card, "data-pf", p["key"])
        self.shot.project_key = p["key"]
        self.dom_nodes["cat"].textContent = "%02d · %s" % (i + 1, portfolio.CAT[p['cat']])
        self.new_badge.visible = bool(p.get('new'))
        self.dom_nodes["name"].textContent = p['name']
        self.dom_nodes["hook"].textContent = portfolio.split_blurb(tp(p['blurb']))[0]
        fill_project(self, p)
        i18n.apply(self)
