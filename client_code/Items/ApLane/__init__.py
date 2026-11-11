from anvil import *

from ._anvil_designer import ApLaneTemplate
from ... import apps_data


class ApLane(ApLaneTemplate):
    """One stage of the board with its apps. item = {id, name, desc, folded, cards}. Raises x-fold(lane)."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        lane = self.dom_nodes["lane"]
        lane.style.setProperty("--c", apps_data.color(it["id"]))
        if it["folded"]:
            lane.classList.add("collapsed")
        self.dom_nodes["name"].textContent = it["name"]
        self.dom_nodes["n"].textContent = str(len(it["cards"]))
        self.dom_nodes["desc"].textContent = it["desc"]
        head = self.dom_nodes["head"]
        head.setAttribute("aria-expanded", "false" if it["folded"] else "true")
        head.setAttribute("title", "Fold or unfold " + it["name"])
        self.none.visible = not it["cards"]
        if not it["folded"]:  # folded lanes don't build their cards at all
            self.cards.items = it["cards"]

    def head_click(self, event):
        if self.parent is not None:
            self.parent.raise_event("x-fold", lane=self.item["id"])
