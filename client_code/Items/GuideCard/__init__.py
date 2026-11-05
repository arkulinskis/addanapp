from anvil import *

from ._anvil_designer import GuideCardTemplate
from ... import i18n, state
from ...i18n import tp
from ...content import guide_cover


class GuideCard(GuideCardTemplate):
    """A free guide: cover, what's inside, and either "Get it free" (asks for the email first) or its download.
    item = {slug, num, title, hook, inside, pages, url, focus, lone}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        card = self.dom_nodes["card"]
        card.id = 'g-' + it['slug']
        if it.get('focus'):
            card.classList.add('focus')
        if it.get('lone'):
            card.classList.add('lone')
        cover = self.dom_nodes["cover"]
        cover.src = guide_cover(it['slug'])
        cover.alt = tp('Cover of the guide {title}', title=tp(it['title']))
        self.dom_nodes["meta"].textContent = it['num'] + ' · ' + tp('PDF · {n} pages', n=it['pages'])
        self.dom_nodes["title"].textContent = tp(it['title'])
        self.dom_nodes["hook"].textContent = tp(it['hook'])
        self.inside.items = [{"text": tp(x)} for x in it['inside']]
        unlocked = bool(it.get('url'))
        self.want_button.visible = not unlocked
        self.download.visible = unlocked
        if unlocked:
            state.set_attr(self.download, "href", it['url'])
            state.set_attr(self.download, "download", 'Addanapp - ' + it['title'] + '.pdf')
            state.set_attr(self.download, "data-dl", it['slug'])
        i18n.apply(self)
        self.want_button.text = tp('Get it free') + ' →'

    @handle("want_button", "click")
    def want_button_click(self, **event_args):
        if self.parent is not None:
            self.parent.raise_event("x-want", slug=self.item['slug'])
