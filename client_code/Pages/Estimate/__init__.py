from anvil import *
from anvil.js import window

from ._anvil_designer import EstimateTemplate
from ... import estimate, i18n, state, ui
from ...i18n import tp


class Estimate(EstimateTemplate):
    """#estimate[/<code>]: the 60-second ballpark estimator. Seven one-tap questions (client_code/estimate.py); the result
    updates live from the published milestone prices: milestone, cumulative price, the path, why, what's included.
    The address follows the answers (#estimate/<code>, without reloading), so Copy link reopens the same result in any
    language. "Send as a brief" sends a lead with source 'estimate' (the server recomputes the estimate from the code)."""

    def __init__(self, code=None, **properties):
        super().__init__(**properties)
        self.answers = estimate.decode(code) if code else estimate.defaults()
        self.qs.items = [{"key": k, "n": i + 1, "q": q, "choices": choices, "value": self.answers[k]}
                         for i, (k, q, choices) in enumerate(estimate.QUESTIONS)]
        self.qs.add_event_handler("x-answer", self._answer)
        self.brief_part.visible = False
        self.brief_ok.visible = False
        for box, auto in ((self.b_name, "name"), (self.b_email, "email"), (self.b_company, "organization")):
            state.set_control_attr(box, "autocomplete", auto)
        state.set_control_attr(self.b_message, "aria-label", tp("In one sentence, what should it do?"))
        state.live(self.res_price)
        i18n.apply(self)
        self.b_send.text = tp("Send brief") + " →"
        self._draw()

    # ---------------------------------------------------------------- answers -> result
    def _answer(self, key, value, **event_args):
        self.answers[key] = value
        self._draw()
        try:  # keep the address in step without a hashchange (that would rebuild the page)
            window.history.replaceState(None, "", "#estimate/" + estimate.encode(self.answers))
        except Exception:
            pass

    def _draw(self):
        a = self.answers
        res = estimate.result(a)
        new = a["need"] == "new"
        for f in self.qs.get_components():
            item = getattr(f, "item")
            getattr(f, "set_shown")(new or item["key"] == "need")
        milestone = res["price"] is not None
        self.res_name.text = tp(res["name"])
        if milestone:
            self.res_price.text = ui.money(res["price"])
            steps = [tp(m["name"]) for m in res["path"] if m["on"]]
            self.res_sub.text = (tp("{milestones}, in fixed-price milestones", milestones=" + ".join(steps))
                                 if len(steps) > 1 else tp("One fixed-price milestone, about 6 to 8 weeks"))
            peek = tp(res["name"]) + " · " + ui.money(res["price"])
        elif res["key"] == "request":
            self.res_price.text = tp("Quoted per request")
            self.res_sub.text = tp("A change to an app we run gets its own fixed quote.")
            peek = tp("Quoted per request")
        else:
            self.res_price.text = tp("Audit first")
            self.res_sub.text = tp("Before we quote work on an app someone else built, we read the code.")
            peek = tp("Audit first")
        self.res_name.visible = milestone
        self.dom_nodes["peek_val"].textContent = peek
        self.path_part.visible = milestone
        for i, m in enumerate(res["path"]):
            node = self.dom_nodes["p%d" % i]
            if m["on"]:
                node.classList.add("on")
            else:
                node.classList.remove("on")
            if i == res["level"]:
                node.classList.add("cur")
            else:
                node.classList.remove("cur")
            self.dom_nodes["p%dn" % i].textContent = tp(m["name"])
            self.dom_nodes["p%dp" % i].textContent = ui.money(m["price"])
        self.why_part.visible = milestone
        self.why.items = [{"text": tp("{why} → {milestone}", why=tp(w["text"]), milestone=tp(w["milestone"]))}
                          for w in res["why"]]
        self.stop_part.visible = milestone
        if milestone:
            names = " + ".join(tp(g["milestone"]) for g in res["included"])
            self.inc_title.text = tp("What {milestones} include", milestones=names) if len(res["included"]) > 1 \
                else tp("What {milestones} includes", milestones=names)
            self.included.items = [{"text": tp(x)} for g in res["included"] for x in g["items"]]
        else:
            self.inc_title.text = tp("How it works")
            self.included.items = [{"text": tp(x)} for x in res["notes"]]

    # ---------------------------------------------------------------- actions
    def peek_click(self, event):
        event.preventDefault()
        window.document.getElementById("est-result").scrollIntoView({"behavior": "smooth", "block": "start"})

    @handle("copy_button", "click")
    def copy_button_click(self, **event_args):
        url = window.location.origin + window.location.pathname + "#estimate/" + estimate.encode(self.answers)
        if window.aa.copy(url):
            state.toast(tp("Link copied. It opens this same estimate."), "ok")
        else:
            alert(url, title=tp("Copy this link"))

    @handle("brief_button", "click")
    def brief_button_click(self, **event_args):
        self.brief_part.visible = True
        ui.scroll_into_view(self.brief_part, "start")
        window.setTimeout(lambda: state.focus(self.b_name), 350)

    def _fail(self, msg):
        self.brief_error.text = msg
        self.brief_error.visible = True

    @handle("b_send", "click")
    def b_send_click(self, **event_args):
        v = {
            "name": (self.b_name.text or "").strip(), "email": (self.b_email.text or "").strip(),
            "company": (self.b_company.text or "").strip(), "message": (self.b_message.text or "").strip(),
            "website": self.dom_nodes["b_hp"].value or "", "consent": bool(self.dom_nodes["b_consent"].checked),
            "source": "estimate", "estimate": estimate.encode(self.answers),
        }
        if len(v["name"]) < 2:
            return self._fail(tp("Please tell us your name."))
        if '@' not in v["email"] or '.' not in v["email"]:
            return self._fail(tp("Please enter a valid email address."))
        if len(v["message"]) < 10:
            return self._fail(tp("A sentence or two about the outcome you're after helps us reply with something useful."))
        if not v["consent"]:
            return self._fail(tp("Please confirm we may contact you about this request."))
        self.brief_error.visible = False
        self.b_send.enabled = False
        self.b_send.text = tp("Sending…")
        res = ui.call("submit_lead", v)
        self.b_send.enabled = True
        self.b_send.text = tp("Send brief") + " →"
        if res is ui.FAIL:
            return
        self.brief_body.visible = False
        self.brief_ok.visible = True
