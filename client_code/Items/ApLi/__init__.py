from anvil import *

from ._anvil_designer import ApLiTemplate


class ApLi(ApLiTemplate):
    """One line of a list (problems, checks, strategies). item = {text, cls?, href?} (plain text)."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        node = self.dom_nodes["li"]
        if it.get("href"):
            from anvil.js import window
            a = window.document.createElement("a")
            a.setAttribute("href", it["href"])
            if str(it["href"]).startswith("http"):
                a.setAttribute("target", "_blank")
                a.setAttribute("rel", "noopener")
            a.textContent = it["text"]
            node.appendChild(a)
        else:
            node.textContent = it["text"]
        for c in (it.get("cls") or "").split():
            node.classList.add(c)
