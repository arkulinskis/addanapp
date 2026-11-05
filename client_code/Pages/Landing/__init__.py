from anvil import *
import anvil.js
from anvil.js import window

from ._anvil_designer import LandingTemplate
from ... import content, i18n, portfolio, state, ui
from ...i18n import tp

FAQ_FILM = 'https://www.youtube.com/watch?v=' + content.YT_REBUILD


def spot_items(projects):
    return [{"key": p["key"], "i": i} for i, p in enumerate(projects)]


class Landing(LandingTemplate):
    """#home: the marketing page. Copy is in the template (translated by i18n.apply); three random case studies
    (Shuffle picks three others), the films (click-to-play), the partner deck per language and the project-brief form."""

    def __init__(self, **properties):
        super().__init__(**properties)
        proof = [{"key": p["key"], "hidden": False} for p in portfolio.PROJECTS]
        self.proof_a.items = proof
        self.proof_b.items = [dict(it, hidden=True) for it in proof]  # the marquee's second copy (for the loop)
        self.spots.items = spot_items(portfolio.picks(3))
        # films
        state.set_attr(self.yt_cover_img, "src", "_/theme/" + content.YT_COVER)
        self.dom_nodes["yt_len"].textContent = content.YT_FILM_LENGTH
        self.film_langs.items = [{"code": c, "name": n, "href": content.film_url(c), "first": i == 0}
                                 for i, (c, n) in enumerate(content.other_languages())]
        # partner deck
        for link in (self.deck_cover_link, self.deck_link):
            for k, v in content.deck().items():
                state.set_attr(link, k, v)
        state.set_attr(self.deck_cover_img, "src", content.DECK_COVER)
        self.dom_nodes["deck_meta"].textContent = (tp('PDF · {n} slides · {size}', n=content.DECK_SLIDES,
                                                      size=tp(content.DECKS[content.DECK_LANG][2]))
                                                   + ' · ' + i18n.NAMES[content.DECK_LANG])
        self.deck_langs.items = [{"code": c, "name": n, "deck": content.deck(c), "first": i == 0}
                                 for i, (c, n) in enumerate(content.other_languages())]
        # the project brief
        self.lead_budget.items = [(tp(x), x) for x in content.LEAD_BUDGETS]
        self.lead_kind.items = [(tp(x), x) for x in content.LEAD_TYPES]
        self.lead_ok.visible = False
        faq_link = ('<a href="%s" target="_blank" rel="noopener">%s <span class="arr">&#8599;</span></a>'
                    % (FAQ_FILM, i18n.t("Parapeet’s before-and-after film")))
        i18n.apply(self, products=len(portfolio.PROJECTS), faq_link=faq_link)
        self.lead_send.text = tp('Send brief') + ' →'
        for box, auto in ((self.lead_name, "name"), (self.lead_email, "email"), (self.lead_company, "organization")):
            state.set_control_attr(box, "autocomplete", auto)
        state.set_control_attr(self.lead_budget, "aria-label", tp("Budget"))
        state.set_control_attr(self.lead_kind, "aria-label", tp("What do you need?"))

    @handle("", "show")
    def form_show(self, **event_args):
        ui.reveal(self)
        ui.spy()

    # ---------------------------------------------------------------- case studies
    @handle("shuffle_button", "click")
    def shuffle_button_click(self, **event_args):
        shown = [it["key"] for it in self.spots.items]
        self.spots.items = spot_items(portfolio.picks(3, exclude=shown))
        ui.reveal(self)

    # ---------------------------------------------------------------- films
    def play_click(self, event):
        window.aa.playFilm(self.dom_nodes["yt_frame"], content.YT_FILM,
                           tp('Addanapp: apps built at AI speed, signed off by senior engineers'))

    def rebuild_click(self, event):
        self.yt_more.visible = False
        frame = self.dom_nodes["yt_frame"]
        window.aa.playFilm(frame, content.YT_REBUILD, tp('Parapeet, before and after'))
        frame.scrollIntoView({'behavior': 'smooth', 'block': 'center'})

    # ---------------------------------------------------------------- workspace preview tabs
    def _ws_tab(self, which):
        for name, tab, panel in (("client", self.ws_client_tab, self.ws_client_panel), ("admin", self.ws_admin_tab, self.ws_admin_panel)):
            tab.classes["on"] = name == which
            panel.classes["on"] = name == which
            state.set_attr(tab, "aria-pressed", "true" if name == which else "false")

    def ws_client_click(self, event):
        self._ws_tab("client")

    def ws_admin_click(self, event):
        self._ws_tab("admin")

    # ---------------------------------------------------------------- project brief
    def _lead_fail(self, msg):
        self.lead_error.text = msg
        self.lead_error.visible = True

    @handle("lead_send", "click")
    def lead_send_click(self, **event_args):
        v = {
            "name": (self.lead_name.text or "").strip(), "email": (self.lead_email.text or "").strip(),
            "company": (self.lead_company.text or "").strip(), "budget": self.lead_budget.selected_value or "",
            "kind": self.lead_kind.selected_value or "", "message": (self.lead_message.text or "").strip(),
            "website": self.dom_nodes["lead_hp"].value or "", "consent": bool(self.dom_nodes["lead_consent"].checked),
        }
        if len(v["name"]) < 2:
            return self._lead_fail(tp("Please tell us your name."))
        if '@' not in v["email"] or '.' not in v["email"]:
            return self._lead_fail(tp("Please enter a valid email address."))
        if len(v["message"]) < 10:
            return self._lead_fail(tp("A sentence or two about the outcome you're after helps us reply with something useful."))
        if not v["consent"]:
            return self._lead_fail(tp("Please confirm we may contact you about this request."))
        self.lead_error.visible = False
        self.lead_send.enabled = False
        self.lead_send.text = tp('Sending…')
        res = ui.call('submit_lead', v)
        self.lead_send.enabled = True
        self.lead_send.text = tp('Send brief') + ' →'
        if res is ui.FAIL:
            return
        self.lead_body.visible = False
        self.lead_ok.visible = True
