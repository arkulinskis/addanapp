from anvil import *

from ._anvil_designer import AvatarTemplate
from ... import state


class Avatar(AvatarTemplate):
    """A round avatar: initials in the person's colour; consultants get the ink circle with a green ring."""

    def __init__(self, **properties):
        self._person, self._size, self._ready = None, 32, False
        super().__init__(**properties)
        self._ready = True
        self._draw()

    def _draw(self):
        if not self._ready:
            return
        p = self._person or {}
        size = int(self._size or 32)
        self.visible = bool(p)
        self.letters.text = p.get("initials") or "?"
        admin = bool(p.get("is_admin"))
        self.circle.classes["admin"] = admin
        self.circle.style["width"] = "%dpx" % size
        self.circle.style["height"] = "%dpx" % size
        self.circle.style["font-size"] = "%dpx" % max(10, int(size * 0.38))
        self.circle.style["background"] = "" if admin else (p.get("color") or "#1D2840")
        state.set_attr(self.circle, "title", p.get("name") or "")

    @property
    def person(self):
        return self._person

    @person.setter
    def person(self, value):
        self._person = value
        self._draw()

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value
        self._draw()
