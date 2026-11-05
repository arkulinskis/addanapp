from anvil import *

from ._anvil_designer import BoardColumnTemplate
from ... import i18n, ui


class BoardColumn(BoardColumnTemplate):
    """A status column of the console's board. item = {status, requests}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        st, reqs = self.item["status"], self.item["requests"]
        label, _cls, color = ui.STATUS[st]
        self.dot.style["background"] = color
        self.dom_nodes["label"].textContent = label
        self.dom_nodes["n"].textContent = str(len(reqs))
        self.cards.items = reqs
        self.empty.visible = not reqs
        i18n.apply(self)
