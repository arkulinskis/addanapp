from anvil import *

from ._anvil_designer import ProofLinkTemplate
from ... import portfolio, state
from ...Components.Shot import BY_KEY


class ProofLink(ProofLinkTemplate):
    """One product in the "Built & running" marquee. item = {key, hidden}: the second copy (which makes the loop
    seamless) is hidden from screen readers and the keyboard."""

    def __init__(self, **properties):
        super().__init__(**properties)
        p = BY_KEY[self.item["key"]]
        self.name.text = p["name"]
        self.dot.style["background"] = p["color"]
        state.set_attr(self.link, "href", portfolio.url(p))
        if self.item.get("hidden"):
            state.set_attr(self.link, "aria-hidden", "true")
            state.set_attr(self.link, "tabindex", "-1")
