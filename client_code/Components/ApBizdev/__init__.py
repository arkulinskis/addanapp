from anvil import *
from anvil.js import window

from ._anvil_designer import ApBizdevTemplate
from ... import apps_data, router, state, ui

RESULTS = ['no reply', 'no', 'yes', 'feedback', 'paid']
WAVES = ['1', '2', '3', 'H', 'Hub']
LOG_HEAD = [{"key": k, "label": k} for k in ('Date', 'App', 'Channel', 'Who', 'Type', 'Result', 'Next step', 'Notes')]


class ApBizdev(ApBizdevTemplate):
    """#apps/bizdev[/<doc>]: the go-to-market plans (APP_MAKER/bizdev): Start here, the playbook, the outreach log
    (add a row here; the PC copies it into outreach-log.csv) and every app's plan. doc = README | PLAYBOOK |
    outreach-log | apps.<key> (a dot instead of the slash, so it fits in one address part)."""

    def __init__(self, arg=None, **properties):
        super().__init__(**properties)
        self.doc = arg or state.store_get('apps.bizDoc', 'README')
        self.data: dict = {}
        self.docs.add_event_handler("x-pick", self._pick)
        state.date_box(self.date_box)
        self.result_dd.items = RESULTS
        for c, label in ((self.date_box, "Date"), (self.app_dd, "App"), (self.channel_box, "Channel"), (self.who_box, "Who"),
                         (self.type_box, "Message type"), (self.result_dd, "Result"), (self.next_box, "Next step"), (self.notes_box, "Notes")):
            state.set_control_attr(c, "aria-label", label)
        self._load()

    def set_arg(self, arg):
        if arg and arg != self.doc:
            self.doc = arg
            self._load()

    def _pick(self, key, **event_args):
        router.go("apps/bizdev/" + key)

    def _load(self):
        res = apps_data.call('apps_bizdev', self.doc)
        if res is ui.FAIL:
            return
        self.data = res
        self.doc = res['name'].replace('/', '.')
        state.store_set('apps.bizDoc', self.doc)
        self.redraw()

    def redraw(self, key=None):
        d = self.data
        if not d:
            return
        q = apps_data.query()
        apps = [a for a in d.get('apps') or [] if not q or q in (a.get('name', '') + ' ' + a.get('key', '')).lower()]
        items = [{"key": "README", "label": "📋 Start here: ranking + calendar", "on": self.doc == 'README'},
                 {"key": "PLAYBOOK", "label": "📘 Playbook: how to get users", "on": self.doc == 'PLAYBOOK'},
                 {"key": "outreach-log", "label": "✉️ Outreach log (%d)" % d.get('log_count', 0), "on": self.doc == 'outreach-log'}]
        for w in WAVES:
            group = [a for a in apps if str(a.get('wave')) == w]
            if group:
                items.append({"grp": group[0].get('wave_name') or ('Wave ' + w)})
                items += [{"key": "apps." + a['key'], "label": "%s. %s" % (a.get('rank'), a.get('name')), "cnt": str(a.get('score') if a.get('score') is not None else ''),
                           "on": self.doc == 'apps.' + a['key'], "title": "Keep bar: " + (a.get('keep') or '')} for a in group]
        self.docs.items = items
        log = d['name'] == 'outreach-log'
        self.log_part.visible = log
        md = self.dom_nodes["md"]
        js = apps_data.js()
        links = []
        if d['name'].startswith('apps/'):
            bk = d['name'][5:]
            p = apps_data.project_by_biz(bk)
            if p:
                links = apps_data.links(p) + [{"label": "Checklist", "href": "#app/" + window.encodeURIComponent(p['key'])}]
            links.append({"label": "Log outreach", "href": "#apps/bizdev/outreach-log"})
            state.store_set('apps.bizApp', bk)
        if js:
            js.links(self.dom_nodes["links"], links)
        if log:
            md.innerHTML = ''
            self._log()
        else:
            # the server renders the plan's markdown from escaped text (apps_core.markdown)
            md.innerHTML = d.get('html') or '<p class="muted">This plan isn’t on Addanapp yet. The PC link sends it with the next push.</p>'

    def _log(self):
        d = self.data
        rows = d.get('rows') or []
        res = [(r[5] if len(r) > 5 else '').strip().lower() for r in rows]
        nos = len([x for x in res if x in ('no', 'no reply')])
        wins = len([x for x in res if x in ('yes', 'feedback', 'paid')])
        self.dom_nodes["log_stats"].textContent = "%d sent · %d/100 no's (points!) · %d yes / feedback / paid" % (len(rows), nos, wins)
        names = [a.get('name') for a in d.get('apps') or []]
        last = state.store_get('apps.bizApp', '')
        pick = next((a.get('name') for a in d.get('apps') or [] if a.get('key') == last), '')
        self.app_dd.items = [("", "")] + [(n, n) for n in names] + [("Several / portfolio", "Several / portfolio")]
        self.app_dd.selected_value = pick
        if not self.date_box.text:
            self.date_box.text = ui.date_iso(ui.now_local())
        js = apps_data.js()
        if js:
            js.table(self.dom_nodes["log"], LOG_HEAD, [list(r) + [''] * (8 - len(r)) for r in reversed(rows)])
        self.dom_nodes["log_none"].textContent = "" if rows else "Nothing logged yet. Send one message, then add it here. A “no reply” still counts as a point."

    @handle("add_button", "click")
    def add_button_click(self, **event_args):
        row = {"date": self.date_box.text or '', "app": self.app_dd.selected_value or '', "channel": self.channel_box.text or '',
               "who": self.who_box.text or '', "message_type": self.type_box.text or '', "result": self.result_dd.selected_value or 'no reply',
               "next_step": self.next_box.text or '', "notes": self.notes_box.text or ''}
        res = apps_data.call('apps_add_outreach', row)
        if res is ui.FAIL:
            return
        self.data['rows'] = res['rows']
        self.data['log_count'] = len(res['rows'])
        for box in (self.channel_box, self.who_box, self.type_box, self.next_box, self.notes_box):
            box.text = ''
        state.toast("Logged: +1 point 💪" if row['result'] in ('no', 'no reply') else "Logged 🎉", "ok")
        self.redraw()
