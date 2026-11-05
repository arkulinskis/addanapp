from anvil import *

from ._anvil_designer import WorkRowTemplate
from ... import i18n, portfolio
from ...i18n import tp
from ...Components.Shot import BY_KEY


class WorkRow(WorkRowTemplate):
    """One project in the Work index: a row that opens in place (native <details>). The opened part (Items/WorkDetail:
    preview, what we built, film, link) is made the first time it opens, so the 53-row index stays quick.
    item = {key, cat}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        p = BY_KEY[self.item["key"]]
        self.p = p
        self.dom_nodes["item"].setAttribute("data-cat", self.item["cat"])
        pic = self.dom_nodes["pic"]
        pic.textContent = p['name'][0]
        pic.style.background = p['color']
        self.dom_nodes["name"].textContent = p['name']
        self.new_badge.visible = bool(p.get('new'))
        self.dom_nodes["line"].textContent = portfolio.split_blurb(tp(p['blurb']))[0]
        self.dom_nodes["tags"].textContent = ' · '.join(tp(x) for x in p['tags'][:2])
        dm = self.dom_nodes["dm"]
        if p.get('domain'):
            dm.textContent = p['domain']
            dm.classList.add('live')
        else:
            dm.textContent = tp('Launching soon')
            dm.classList.add('soon')
        i18n.apply(self)

    def toggled(self, event):
        if getattr(self.dom_nodes["item"], "open") and not self.body_holder.get_components():
            from ..WorkDetail import WorkDetail
            self.body_holder.add_component(WorkDetail(project_key=self.p['key']))
