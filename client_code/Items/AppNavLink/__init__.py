from anvil import *

from ._anvil_designer import AppNavLinkTemplate
from ... import state


class AppNavLink(AppNavLinkTemplate):
    """A workspace menu link in the header. item = {href, icon, label, count, sm_only, on} (Shell._draw_app_nav)."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        state.set_attr(self.link, "href", it["href"])
        self.icon.classes["ic-" + it["icon"]] = True
        n = it.get("count") or 0
        self.count_box.visible = bool(n)
        self.count.text = str(n)
        self.link.classes["active"] = bool(it.get("on"))
        self.link.classes["sm-only"] = bool(it.get("sm_only"))
