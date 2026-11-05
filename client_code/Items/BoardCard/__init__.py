from anvil import *

from ._anvil_designer import BoardCardTemplate
from ... import ui


class BoardCard(BoardCardTemplate):
    """A request card on the console's board (opens the request). item = a request dict."""

    def __init__(self, **properties):
        super().__init__(**properties)
        r = self.item
        card = self.dom_nodes["card"]
        card.setAttribute("href", "#r/" + r["id"])
        if r.get("unread"):
            card.classList.add("unread")
        c = r.get('client') or {}
        self.dom_nodes["ref"].textContent = r["ref"]
        self.dom_nodes["title"].textContent = r["title"]
        self.dom_nodes["who"].textContent = c.get("company") or c.get("name", "")
        if r["priority"] in ("high", "urgent"):
            ui.priority_chip(self.prio, r["priority"])
        else:
            self.prio.visible = False
        self.progress.value = r["progress"]
        self.progress.done = r["status"] == "delivered"
