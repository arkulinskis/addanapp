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
        co = r.get('pending_change')
        if co:
            d = int(round(co.get('delta') or 0))
            what = tp('Approve change · {delta}', delta=('+' if d >= 0 else '-') + ui.money(abs(d)))
        elif r['status'] == 'quoted':
            what = tp('Approve quote · {amount}', amount=ui.money(r.get('quote_amount')))
        else:
            what = tp('Review &amp; accept delivery')
        self.dom_nodes["what"].textContent = what
