import datetime

from anvil import *
from anvil.js import window

from ._anvil_designer import SignoffCardTemplate
from ... import i18n, signoff_data, ui
from ...i18n import tp


class SignoffCard(SignoffCardTemplate):
    """A delivery's sign-off record, as the client sees it (RequestDetail) and on the public sample (#signoff/sample):
    who signed it off and when, the 10 checks from guide 03, the automated tests, each acceptance criterion (and the
    client's own tick once they decided), the reviewer's note, and Print (print CSS in trust.css keeps only the card)."""

    def __init__(self, **properties):
        self._record, self._ready = None, False
        super().__init__(**properties)
        i18n.apply(self)
        self._ready = True
        self._draw()

    @property
    def record(self):
        return self._record

    @record.setter
    def record(self, value):
        self._record = value
        self._draw()

    def _draw(self):
        if not self._ready:
            return
        rec = self._record or {}
        self.visible = bool(rec)
        if not rec:
            return
        checks = rec.get("checks") or {}
        crit = rec.get("criteria") or []
        client = rec.get("client_criteria") or []
        who = (rec.get("reviewer") or {}).get("name") or tp("An engineer")
        if rec.get("sample"):
            y, m, d = rec.get("date")
            when = ui.fmt_date(datetime.date(y, m, d), True)
            who = tp(who)
        else:
            when = ui.fmt_date(rec.get("created"), True) if rec.get("created") else ""
        self.by_label.text = tp("Signed off by {name}, {date}", name=who, date=when) if when else tp("Signed off by {name}", name=who)
        n_ok = len([k for k in signoff_data.CHECK_KEYS if checks.get(k)])
        self.dom_nodes["n_checks"].textContent = "%d/%d" % (n_ok, len(signoff_data.CHECK_KEYS))
        self.dom_nodes["n_tests"].textContent = str(int(rec.get("tests") or 0))
        c_ok = len([c for c in crit if c.get("ok")])
        self.dom_nodes["n_crit"].textContent = "%d/%d" % (c_ok, len(crit))
        self.checks.items = [{"text": tp(label), "ok": bool(checks.get(k)), "client": None}
                             for k, label in signoff_data.CHECKS]
        rows = []
        for i, c in enumerate(crit):
            mine = client[i].get("ok") if i < len(client) else None
            rows.append({"text": tp(c.get("text") or "") if rec.get("sample") else (c.get("text") or ""),
                         "ok": bool(c.get("ok")), "client": None if not client else bool(mine)})
        self.criteria.items = rows
        if client:
            passed = len([c for c in client if c.get("ok")])
            if rec.get("accepted"):
                self.client_label.text = tp("Accepted by the client on {date}: {ok}/{n} criteria passed.",
                                            date=ui.fmt_date(rec.get("accepted"), True), ok=passed, n=len(client))
            else:
                self.client_label.text = tp("The client asked for changes: {ok}/{n} criteria passed so far.", ok=passed, n=len(client))
        self.client_part.visible = bool(client)
        note = rec.get("note") or ""
        self.note_label.text = tp(note) if rec.get("sample") else note
        self.note_part.visible = bool(note)
        if rec.get("sample"):
            self.foot_label.text = tp("Sample from our demo workspace. A real record names the engineer who signed it off.")
        elif rec.get("complete"):
            self.foot_label.text = tp("The engineer named above is accountable for this delivery.")
        else:
            self.foot_label.text = tp("Draft: not every check and criterion is ticked yet, so it isn't signed off.")

    @handle("print_button", "click")
    def print_button_click(self, **event_args):
        body = window.document.body
        body.classList.add("so-printing")
        try:
            window.print()
        finally:
            window.setTimeout(lambda: body.classList.remove("so-printing"), 500)
