from anvil import *

from ._anvil_designer import SoLineTemplate
from ...i18n import tp


class SoLine(SoLineTemplate):
    """One line of a sign-off record: a check or an acceptance criterion, ticked by the engineer, and (once the client
    decided) the client's own result. item = {text (translated), ok, client: None | True | False}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        ok = bool(it.get("ok"))
        row = self.dom_nodes["row"]
        row.classList.add("ok" if ok else "no")
        self.dom_nodes["ico"].classList.add("ic-check-circle" if ok else "ic-minus-circle")
        self.dom_nodes["sr"].textContent = (tp("Passed") if ok else tp("Not ticked")) + ": "
        self.dom_nodes["text"].textContent = it.get("text") or ""
        cl = it.get("client")
        node = self.dom_nodes["cl"]
        if cl is None:
            node.style.display = "none"
        else:
            node.textContent = tp("Client: passed") if cl else tp("Client: not yet")
            node.classList.add("ok" if cl else "no")
