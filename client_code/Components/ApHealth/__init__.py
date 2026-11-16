import datetime

from anvil import *
import anvil.js
from anvil.js import window

from ._anvil_designer import ApHealthTemplate
from ... import apps_data, apps_fmt, ui

STATUS = {  # status -> (label, chip class, icon): never colour alone
    "ok": ("Reporting", "human", "ic-check-circle"),
    "not_installed": ("Not published", "warn", "ic-clock"),
    "signature": ("Not published", "warn", "ic-clock"),
    "forbidden": ("Refused", "bad", "ic-lock"),
    "app_error": ("App error", "bad", "ic-flag"),
    "unreachable": ("No answer", "bad", "ic-x"),
    "no_key": ("No signing key", "bad", "ic-key"),
    None: ("Not checked", "", "ic-minus-circle"),
}
TOP = 15


def _n(v):
    return apps_fmt.num(v) if isinstance(v, (int, float)) else "–"


class ApHealth(ApHealthTemplate):
    """#apps/health (consultants): every app's admin status report (AppHealth.py on the server, AppStatus.py in each
    app). "Check all apps" runs the checks BATCH apps at a time on a timer, so the page stays usable and shows progress;
    the results are stored, so opening the view shows the last check straight away."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.apps: list = []
        self.queue: list = []
        self.batch = 8
        self.total = 0
        res = ui.call("health_list")
        if res is not ui.FAIL:
            self.apps, self.batch = res["apps"], res.get("batch") or 8
            self.dom_nodes["key_warn"].hidden = bool(res.get("key_ok"))
        self.redraw()

    @handle("", "show")
    def form_show(self, **event_args):
        self._chart()

    # ---------------------------------------------------------------- checking
    @handle("check_button", "click")
    def check_button_click(self, **event_args):
        self.queue = [a["key"] for a in self.apps]
        self.total = len(self.queue)
        self.check_button.enabled = False
        self._progress()
        self.run_timer.interval = 0.05

    @handle("run_timer", "tick")
    def run_timer_tick(self, **event_args):
        self.run_timer.interval = 0
        if not self.queue:
            return self._done()
        part, self.queue = self.queue[:self.batch], self.queue[self.batch:]
        res = ui.call("health_check", part)
        if res is ui.FAIL:
            self.queue = []
            return self._done()
        by_key = {r["key"]: r for r in res}
        self.apps = [by_key.get(a["key"], a) for a in self.apps]
        self._progress()
        self.redraw()
        self.run_timer.interval = 0.05

    def _progress(self):
        done = self.total - len(self.queue)
        self.dom_nodes["progress"].textContent = ("Checking… %d of %d" % (done, self.total)) if self.queue else ""

    def _done(self):
        self.check_button.enabled = True
        self.dom_nodes["progress"].textContent = ""
        ok = sum(1 for a in self.apps if a.get("status") == "ok")
        Notification("%d of %d apps reporting" % (ok, len(self.apps)), timeout=3).show()

    # ---------------------------------------------------------------- drawing
    def _ok(self):
        return [a for a in self.apps if a.get("summary")]

    def _sum(self, field):
        vals = [a["summary"].get(field) for a in self._ok() if isinstance(a["summary"].get(field), (int, float))]
        return sum(vals) if vals else None

    def redraw(self, key=None):
        checked = [a["checked"] for a in self.apps if a.get("checked")]
        self.dom_nodes["when"].textContent = ("last check " + apps_fmt.ago(max(checked))) if checked else "not checked yet"
        reporting = sum(1 for a in self.apps if a.get("status") == "ok")
        self.tiles.items = [
            {"k": "Apps reporting", "v": "%d / %d" % (reporting, len(self.apps)), "d": "answering with their report"},
            {"k": "Users", "v": _n(self._sum("users")), "d": "accounts in every app"},
            {"k": "Active, 7 days", "v": _n(self._sum("active_7d")), "d": "people seen this week"},
            {"k": "Sign-ups, 30 days", "v": _n(self._sum("signups_30d")), "d": "new accounts"},
            {"k": "Database rows", "v": _n(self._sum("rows")), "d": "count towards the Anvil plan"},
            {"k": "Errors, 24 hours", "v": _n(self._sum("errors_24h")), "d": "uncaught, reported by browsers"},
        ]
        self._bars(self.user_bars, "users", "%s\n%s users\n%s active in 7 days", "active_7d")
        self._bars(self.row_bars, "rows", "%s\n%s rows\n%s tables", "tables")
        errs = self._bars(self.error_bars, "errors_7d", "%s\n%s errors in 7 days\n%s sessions affected", "error_sessions_7d")
        self.dom_nodes["no_errors"].hidden = errs > 0
        self._attention()
        self._table()
        self._chart()

    def _bars(self, panel, field, tip, extra):
        rows = sorted([a for a in self._ok() if (a["summary"].get(field) or 0) > 0],
                      key=lambda a: -a["summary"][field])
        top = max([1] + [a["summary"][field] for a in rows])
        panel.items = [{"key": a["key"], "label": a["name"], "val": _n(a["summary"][field]),
                        "parts": [{"w": a["summary"][field] * 100.0 / top, "color": "var(--ap-s1)"}],
                        "tip": tip % (a["name"], _n(a["summary"][field]), _n(a["summary"].get(extra)))}
                       for a in rows[:TOP]]
        return len(rows)

    def _chart(self):
        js = apps_data.js()
        if not js or not self.dom_nodes["signups_chart"].isConnected:
            return
        today = datetime.date.today()
        days = [(today - datetime.timedelta(days=29 - i)).isoformat() for i in range(30)]
        tot = {d: 0 for d in days}
        for a in self._ok():
            for d, n in (a["summary"].get("signups_by_day") or {}).items():
                if d in tot and isinstance(n, (int, float)):
                    tot[d] += n
        js.chart(self.dom_nodes["signups_chart"],
                 [{"x": apps_fmt.day_label(d), "y": tot[d], "tip": "%s\n%s sign-ups" % (apps_fmt.day_label(d), _n(tot[d]))}
                  for d in days], 'bars', 'var(--ap-s1)')

    def _el(self, tag, cls=None, text=None):
        e = window.document.createElement(tag)
        if cls:
            e.className = cls
        if text is not None:
            e.textContent = str(text)
        return e

    def _links(self, a, into):
        """The shortcuts: open the app (to sign in or look) and its Anvil editor (to publish / accept the schema)."""
        for label, href, title in (("Open app ↗", a["url"], "Open %s (sign in there)" % a["name"]),
                                   ("Anvil editor ↗", a.get("editor"), "Open %s in the Anvil editor" % a["name"])):
            if not href:
                continue
            link = self._el("a", "aa-btn sm ghost", label)
            link.href, link.target, link.rel, link.title = href, "_blank", "noopener", title
            into.appendChild(link)

    def _chip(self, status):
        label, cls, icon = STATUS.get(status, STATUS[None])
        chip = self._el("span", "chip " + cls)
        chip.appendChild(self._el("i", "ic " + icon))
        chip.appendChild(window.document.createTextNode(" " + label))
        return chip

    def _attention(self):
        """One line per thing to do ("publish the latest version", "add the App Secret"...), then the apps it applies
        to; each name opens that app in a new tab, the quick way to sign in or look."""
        box, ul = self.dom_nodes["attn_box"], self.dom_nodes["attn"]
        ul.replaceChildren()
        groups: dict = {}
        for a in self.apps:
            if a.get("status") and (a["status"] != "ok" or a.get("hint", "").startswith("Reporting. To")):
                groups.setdefault((a["status"], a.get("hint") or ""), []).append(a)
        for (status, hint), apps in sorted(groups.items(), key=lambda g: -len(g[1])):
            li = self._el("li")
            head = self._el("div", "ap-ah-ghead")
            head.appendChild(self._chip(status))
            head.appendChild(self._el("b", None, "%d %s" % (len(apps), "app" if len(apps) == 1 else "apps")))
            head.appendChild(self._el("span", None, hint))
            li.appendChild(head)
            names = self._el("div", "ap-ah-names")
            for a in apps:
                link = self._el("a", None, a["name"] + " ↗")
                link.href, link.target, link.rel = a["url"], "_blank", "noopener"
                link.title = "Open %s (sign in there)" % a["name"]
                names.appendChild(link)
            li.appendChild(names)
            ul.appendChild(li)
        box.hidden = not groups

    def _table(self):
        tb = self.dom_nodes["tbody"]
        tb.replaceChildren()
        for a in self.apps:
            s = a.get("summary") or {}
            tr = self._el("tr")
            th = self._el("th")
            th.scope = "row"
            th.textContent = a["name"]
            tr.appendChild(th)
            td = self._el("td")
            td.appendChild(self._chip(a.get("status")))
            tr.appendChild(td)
            for f in ("users", "active_7d", "signups_7d", "rows", "errors_24h"):
                tr.appendChild(self._el("td", "n", _n(s.get(f))))
            tr.appendChild(self._el("td", "muted", apps_fmt.ago(a["checked"]) if a.get("checked") else "–"))
            links = self._el("td", "ap-ah-links")
            self._links(a, links)
            tr.appendChild(links)
            tb.appendChild(tr)
