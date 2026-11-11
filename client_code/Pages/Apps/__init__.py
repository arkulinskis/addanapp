from anvil import *
from anvil.js import window

from ._anvil_designer import AppsTemplate
from ... import apps_data, apps_fmt, router, state, ui

BOOT_HINT = "Start it on the PC: double-click “Start App Board link.bat” in APP_MAKER\\board."


def make_view(view, arg):
    """The Form for one view of the board (Components/Ap*)."""
    if view == 'grid':
        from ...Components.ApGrid import ApGrid
        return ApGrid()
    if view == 'posts':
        from ...Components.ApPosts import ApPosts
        return ApPosts(arg=arg)
    if view == 'bizdev':
        from ...Components.ApBizdev import ApBizdev
        return ApBizdev(arg=arg)
    if view == 'money':
        from ...Components.ApMoney import ApMoney
        return ApMoney()
    if view == 'youtube':
        from ...Components.ApYoutube import ApYoutube
        return ApYoutube()
    if view == 'dossier':
        from ...Components.ApDossier import ApDossier
        return ApDossier(arg=arg)
    if view == 'notes':
        from ...Components.ApNotes import ApNotes
        return ApNotes()
    from ...Components.ApBoard import ApBoard
    return ApBoard()


class Apps(AppsTemplate):
    """#apps[/view[/arg]]: a client's app portfolio board (the App Board that ran on the user's PC until 2026-11-11).
    Views: board (a lane per stage), grid (every step as a tick square), posts, bizdev, money, youtube, dossier (one app
    per page), notes (what needs the user or Claude). The data loads once (apps_data) and is shared by the views; the
    router calls show_view() to switch without reloading. Jobs for the PC (refresh, links, ideas) are polled here."""

    def __init__(self, view=None, arg=None, **properties):
        super().__init__(**properties)
        self.view, self.arg, self.part = '', None, None
        self._seen_jobs: dict = {}
        state.set_control_attr(self.search_box, "type", "search")
        state.set_control_attr(self.search_box, "aria-label", "Search apps")
        state.set_control_attr(self.client_dd, "aria-label", "Whose portfolio")
        state.heading(self.title, 1)
        self.search_box.text = apps_data.query()
        apps_data.listen(self._changed)
        self.nothing.visible = False
        b = apps_data.load()
        if b is None or not b.get('projects'):
            self._empty()
            return
        self._head()
        self.show_view(view, arg)
        self._poll_plan()

    def _empty(self):
        self.title.text, self.sub.text = "Apps", ""
        for c in (self.pc_line, self.tabs, self.refresh_button, self.search_box, self.client_dd):
            c.visible = False
        self.nothing.visible = True

    # ---------------------------------------------------------------- drawing
    def _views(self):
        b = apps_data.board() or {}
        mods = b.get('modules') or apps_data.MODULE_VIEWS
        return [v for v in apps_data.VIEWS if v[0] not in apps_data.MODULE_VIEWS or v[0] in mods]

    def _head(self):
        b = apps_data.board() or {}
        c = b.get('client') or {}
        self.title.text = "Apps"
        when = b.get('refreshed_at')
        self.sub.text = "%s · %s%s" % (c.get('name') or 'Client', apps_fmt.plural(len(b.get('projects') or []), 'app'),
                                       (" · facts checked " + apps_fmt.ago(when)) if when else "")
        self.stats.items = [{"label": str(lbl), "value": str(val)} for lbl, val in b.get('stats') or []]
        clients = b.get('clients') or []
        self.client_dd.visible = len(clients) > 1
        if len(clients) > 1:
            self.client_dd.items = [("%s (%d)" % (x['name'], x['n']), x['id']) for x in clients]
            self.client_dd.selected_value = c.get('id')
        self._pc()

    def _pc(self):
        b = apps_data.board() or {}
        w = b.get('worker') or {}
        jobs = apps_data.pending()
        self.pc_dot.classes["on"] = bool(w.get('online'))
        if w.get('online'):
            txt = "Your PC is connected" + (" (%s)" % w['host'] if w.get('host') else "")
        elif w.get('seen'):
            txt = "Your PC link is off (last seen %s), so refreshes wait until it's on. %s" % (apps_fmt.ago(w['seen']), BOOT_HINT)
        else:
            txt = "Your PC hasn't connected yet. " + BOOT_HINT
        if jobs:
            names = ', '.join(apps_data.WHAT.get(j['kind'], j['kind']) + ((' ' + j['key']) if j.get('key') else '') for j in jobs[:3])
            txt += " · %s: %s" % (apps_fmt.plural(len(jobs), 'job') + (' running' if any(j['status'] == 'running' for j in jobs) else ' waiting'), names)
        self.pc_text.text = txt

    def _tabs(self):
        n_notes = len(apps_data.active_notes())
        self.tabs.items = [{"href": "#apps/" + key, "label": label, "on": key == self.view, "count": n_notes if key == 'notes' else 0}
                           for key, label, _ic in self._views()]

    def show_view(self, view, arg=None):
        """Open a view (the router calls this for #apps/<view>/<arg> while the page is open)."""
        avail = [v[0] for v in self._views()]
        if view not in avail:
            last = state.store_get('apps.view', 'board')
            view = last if last in avail else 'board'
            if router.current().split('/')[0] == 'apps':
                window.history.replaceState(None, '', '#apps/' + view)
        state.store_set('apps.view', view)
        same = view == self.view and self.part is not None
        self.view, self.arg = view, arg
        self._tabs()
        if same:
            if hasattr(self.part, 'set_arg'):
                self.part.set_arg(arg)
            return
        self.view_holder.clear()
        self.part = make_view(view, arg)
        self.view_holder.add_component(self.part)

    def _changed(self, key=None):
        """Something changed (a tick, a job finished, a dismissed note): redraw what shows it."""
        self._head()
        self._tabs()
        if self.part is not None and hasattr(self.part, 'redraw'):
            self.part.redraw(key)
        self._poll_plan()

    # ---------------------------------------------------------------- actions
    @handle("search_box", "change")
    def search_box_change(self, **event_args):
        apps_data.set_query(self.search_box.text)
        if self.part is not None and hasattr(self.part, 'redraw'):
            self.part.redraw(None)

    @handle("client_dd", "change")
    def client_dd_change(self, **event_args):
        apps_data.set_client(self.client_dd.selected_value)
        if apps_data.load(force=True) is not None:
            self.part = None
            self._head()
            self.show_view(self.view, None)

    @handle("refresh_button", "click")
    def refresh_button_click(self, **event_args):
        from ...Dialogs.ApRefresh import ApRefresh
        acts = alert(ApRefresh(key=None), buttons=[], large=False, role="aa-dialog", dismissible=True)
        if acts:
            apps_data.queue('refresh', None, {'actions': acts})

    # ---------------------------------------------------------------- jobs for the PC
    def _poll_plan(self):
        self.poll_timer.interval = 5 if apps_data.pending() else 60

    @handle("poll_timer", "tick")
    def poll_timer_tick(self, **event_args):
        if router.current().split('/')[0] != 'apps':
            self.poll_timer.interval = 0
            return
        before = [j['id'] for j in apps_data.pending()]
        res = apps_data.call('apps_jobs', before or None)
        if res is ui.FAIL or apps_data.board() is None:
            return
        b = apps_data.board()
        b['worker'] = res['worker']
        finished = [j for j in res['jobs'] if j['status'] not in ('queued', 'running')]
        still = [j for j in res['jobs'] if j['status'] in ('queued', 'running')]
        b['jobs'] = still
        if finished:
            for j in finished:
                what = apps_data.WHAT.get(j['kind'], 'Job') + ((' · ' + j['key']) if j.get('key') else '')
                if j['status'] == 'done':
                    errs = (j.get('result') or {}).get('errors') or []
                    state.toast(what + (": done, with problems (see Notifications)" if errs else ": done"), "ok")
                elif j['status'] == 'failed':
                    state.toast(what + " failed: " + (j.get('error') or 'no details'), "error")
            if apps_data.load(force=True) is not None:
                self._changed(None)
                return
        self._pc()
        self._poll_plan()
