import json

from anvil import *
import anvil.js
from anvil.js import window

from ._anvil_designer import GuidesTemplate
from ... import i18n, state, ui
from ...i18n import tp
from ...content import GUIDES, GUIDE_SLUGS, GUIDE_SITUATIONS

STORE_KEY = 'aa.guides'  # this browser already unlocked the guides: {slug: url}


def _saved():
    try:
        raw = window.localStorage.getItem(STORE_KEY)
        links = json.loads(raw) if raw else {}
        return {k: v for k, v in links.items() if k in GUIDE_SLUGS and isinstance(v, str)} or None
    except Exception:
        return None


def _save(links):
    try:
        window.localStorage.setItem(STORE_KEY, json.dumps(links))
    except Exception:
        pass


class Guides(GuidesTemplate):
    """#guides[/slug]: the free guides. One email unlocks all five: the download links appear on the page and are
    emailed too (api_public.request_guides). The PDFs are theme assets, so this is a soft gate."""

    def __init__(self, focus=None, **properties):
        super().__init__(**properties)
        self.focus = focus if focus in GUIDE_SLUGS else ''
        self.links = _saved()
        self.lang_note.visible = i18n.lang != 'en'
        self.situation_dd.items = [(tp('Choose one'), '')] + [(tp(x), x) for x in GUIDE_SITUATIONS]
        self.cards.add_event_handler("x-want", self._want)
        state.set_control_attr(self.email_box, "autocomplete", "email")
        state.set_control_attr(self.name_box, "autocomplete", "given-name")
        i18n.apply(self)
        self.get_button.text = tp('Get the guides') + ' →'
        self._draw(just_sent=False)

    def _draw(self, just_sent):
        unlocked = bool(self.links)
        links = self.links or {}
        self.form_body.visible = not unlocked
        self.ok_box.visible = unlocked
        self.sent_note.visible = just_sent
        self.link_rows.items = [{"slug": s, "num": n, "title": title, "url": links[s]}
                                for s, n, title, _h, _i, _p in GUIDES if s in links]
        self.cards.items = [{"slug": s, "num": n, "title": title, "hook": hook, "inside": inside, "pages": pages,
                             "url": links.get(s), "focus": s == self.focus, "lone": i == len(GUIDES) - 1 and len(GUIDES) % 2 == 1}
                            for i, (s, n, title, hook, inside, pages) in enumerate(GUIDES)]
        ui.reveal(self)

    @handle("", "show")
    def form_show(self, **event_args):
        ui.reveal(self)
        if self.focus:
            card = window.document.getElementById('g-' + self.focus)
            if card:
                card.scrollIntoView({'behavior': 'smooth', 'block': 'center'})

    def _want(self, slug, **event_args):
        self.focus = slug if slug in GUIDE_SLUGS else self.focus
        self.dom_nodes["form_box"].scrollIntoView({'behavior': 'smooth', 'block': 'center'})
        state.control(self.email_box).focus({'preventScroll': True})

    @handle("get_button", "click")
    def get_button_click(self, **event_args):
        email = (self.email_box.text or '').strip()
        if '@' not in email or '.' not in email.split('@')[-1]:
            self.error.text = tp("Please enter a valid email address.")
            self.error.visible = True
            return
        self.error.visible = False
        v = {'email': email, 'name': (self.name_box.text or '').strip(), 'situation': self.situation_dd.selected_value or '',
             'website': self.dom_nodes["hp"].value or '', 'newsletter': bool(self.dom_nodes["news"].checked),
             'guide': self.focus, 'lang': i18n.lang}
        self.get_button.enabled = False
        self.get_button.text = tp('Sending…')
        res = ui.call('request_guides', v)
        self.get_button.enabled = True
        self.get_button.text = tp('Get the guides') + ' →'
        if res is ui.FAIL or not res:
            return
        self.links = {slug: url for slug, url in res.get('links', [])}
        _save(self.links)
        self._draw(just_sent=bool(res.get('emailed')))
        self.dom_nodes["form_box"].scrollIntoView({'behavior': 'smooth', 'block': 'center'})
