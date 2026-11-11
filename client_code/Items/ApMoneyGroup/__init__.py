from anvil import *

from ._anvil_designer import ApMoneyGroupTemplate


class ApMoneyGroup(ApMoneyGroupTemplate):
    """A group of the Money view. item = {head, sub, color, projects, now}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        self.dom_nodes["head"].style.color = it["color"]
        self.dom_nodes["title"].textContent = it["head"]
        self.dom_nodes["sub"].textContent = it["sub"]
        self.cards.items = [{"project": p, "now": it["now"]} for p in it["projects"]]
