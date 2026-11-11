from anvil import *

from ._anvil_designer import ApFactTemplate


class ApFact(ApFactTemplate):
    """A fact tile on a dossier. item = {k, v, cls (ok | bad | warn | merge | ''), title}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        box = self.dom_nodes["box"]
        if it.get("cls"):
            box.classList.add(it["cls"])
        box.setAttribute("title", it.get("title") or it["v"])
        self.dom_nodes["k"].textContent = it["k"]
        self.dom_nodes["v"].textContent = it["v"]
