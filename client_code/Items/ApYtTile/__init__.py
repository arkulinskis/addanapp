from anvil import *

from ._anvil_designer import ApYtTileTemplate


class ApYtTile(ApYtTileTemplate):
    """A number tile on the YouTube view. item = {k (label), v (value), d (detail)}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        for k in ("k", "v", "d"):
            self.dom_nodes[k].textContent = self.item.get(k) or ''
