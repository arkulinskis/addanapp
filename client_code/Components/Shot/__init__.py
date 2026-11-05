from anvil import *

from ._anvil_designer import ShotTemplate
from ... import portfolio

BY_KEY = {p['key']: p for p in portfolio.PROJECTS}


class Shot(ShotTemplate):
    """A project's preview (portfolio.shot_html: the SVG "engine" or a framed screenshot), on the product's colour."""

    def __init__(self, **properties):
        self._key, self._ready = "", False
        super().__init__(**properties)
        self._ready = True
        self._draw()

    def _draw(self):
        if not self._ready:
            return
        p = BY_KEY.get(self._key)
        box = self.dom_nodes["box"]
        box.innerHTML = portfolio.shot_html(p) if p else ""
        box.style.background = p["bg"] if p else ""

    @property
    def project_key(self):
        return self._key

    @project_key.setter
    def project_key(self, value):
        self._key = value or ""
        self._draw()
