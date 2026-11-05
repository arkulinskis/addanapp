from anvil import *

from ._anvil_designer import LangLinkTemplate
from ... import state


class LangLink(LangLinkTemplate):
    """One language in an "Other languages:" row (the film or the partner deck in another language).
    item = {code, name, first, href} for a film, or {code, name, first, deck: {href, download, ...}} for the deck."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        self.name.text = it["name"]
        self.sep.visible = not it.get("first")
        state.set_attr(self.link, "lang", it["code"])
        state.set_attr(self.link, "hreflang", it["code"])
        attrs = it.get("deck") or {"href": it.get("href"), "target": "_blank", "rel": "noopener"}
        for k, v in attrs.items():
            state.set_attr(self.link, k, v)
