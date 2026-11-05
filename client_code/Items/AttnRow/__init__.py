from anvil import *

from ._anvil_designer import AttnRowTemplate
from ... import ui
from ...i18n import tp


class AttnRow(AttnRowTemplate):
    """A request waiting for the client (a quote to approve or a delivery to accept). item = a request dict."""

    def __init__(self, **properties):
        super().__init__(**properties)
        r = self.item
        self.dom_nodes["link"].setAttribute("href", "#r/" + r["id"])
        self.dom_nodes["ref"].textContent = r["ref"]
        self.dom_nodes["title"].textContent = r["title"]
        self.dom_nodes["what"].textContent = (tp('Approve quote · {amount}', amount=ui.money(r.get('quote_amount')))
                                              if r['status'] == 'quoted' else tp('Review &amp; accept delivery'))
