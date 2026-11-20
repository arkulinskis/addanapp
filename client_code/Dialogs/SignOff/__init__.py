from anvil import *

from ._anvil_designer import SignOffTemplate
from ... import i18n, signoff_data, state, ui
from ...i18n import tp


class SignOff(SignOffTemplate):
    """Consultant: sign off a delivery (the 10 checks, each acceptance criterion, tests passing, a note for the client).
    A complete record (everything ticked) is posted to the client; an incomplete one is kept as a draft.
    alert() returns the request payload after saving, or None."""

    def __init__(self, request_id, acceptance, record, **properties):
        super().__init__(**properties)
        self.request_id = request_id
        rec = record or {}
        given = rec.get("checks") or {}
        self.checks.items = [{"key": k, "text": tp(label), "ok": bool(given.get(k))} for k, label in signoff_data.CHECKS]
        crit = rec.get("criteria") or [{"text": c, "ok": False} for c in signoff_data.criteria_of(acceptance)]
        self.criteria.items = [{"key": str(i), "text": c.get("text") or "", "ok": bool(c.get("ok"))} for i, c in enumerate(crit)]
        self.tests_box.text = str(rec.get("tests")) if rec.get("tests") else ""
        self.note_box.text = rec.get("note") or ""
        state.set_control_attr(self.tests_box, "min", 0)
        state.live(self.status_label)
        self.checks.add_event_handler("x-tick", self._status)
        self.criteria.add_event_handler("x-tick", self._status)
        i18n.apply(self)
        self._status()

    def _items(self, panel):
        return [dict(getattr(f, "item")) for f in panel.get_components()]

    def _status(self, **event_args):
        checks, crit = self._items(self.checks), self._items(self.criteria)
        n_ok, c_ok = len([c for c in checks if c["ok"]]), len([c for c in crit if c["ok"]])
        done = n_ok == len(checks) and c_ok == len(crit) and len(crit) > 0
        counts = tp("{ok}/{n} checks · {cok}/{cn} criteria", ok=n_ok, n=len(checks), cok=c_ok, cn=len(crit))
        self.status_label.text = counts + " · " + (tp("complete: saving posts it to the client.") if done
                                                     else tp("saved as a draft until everything is ticked."))
        self.save_button.text = tp("Sign off and notify client") if done else tp("Save draft")

    @handle("all_button", "click")
    def all_button_click(self, **event_args):
        for f in self.checks.get_components():
            getattr(f, "set_ok")(True)
        self._status()

    @handle("save_button", "click")
    def save_button_click(self, **event_args):
        tests = (self.tests_box.text or "") if not isinstance(self.tests_box.text, (int, float)) else self.tests_box.text
        data = {
            "checks": {c["key"]: c["ok"] for c in self._items(self.checks)},
            "criteria": [{"text": c["text"], "ok": c["ok"]} for c in self._items(self.criteria)],
            "tests": tests or 0, "note": (self.note_box.text or "").strip(),
        }
        self.save_button.enabled = False
        res = ui.call("admin_save_signoff", self.request_id, data)
        self.save_button.enabled = True
        if res is not ui.FAIL:
            self.raise_event("x-close-alert", value=res)

    @handle("cancel_button", "click")
    def cancel_button_click(self, **event_args):
        self.raise_event("x-close-alert", value=None)
