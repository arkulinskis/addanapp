from anvil import *

from ._anvil_designer import GuideLinkTemplate
from ... import i18n
from ...i18n import tp


class GuideLink(GuideLinkTemplate):
    """An unlocked guide in the "Your guides are ready" list. item = {slug, num, title, url}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        self.dom_nodes["num"].textContent = it['num']
        self.dom_nodes["title"].textContent = tp(it['title'])
        a = self.dom_nodes["link"]
        a.setAttribute("href", it['url'])
        a.setAttribute("download", 'Addanapp - ' + it['title'] + '.pdf')
        a.setAttribute("data-dl", it['slug'])
        i18n.apply(self)
