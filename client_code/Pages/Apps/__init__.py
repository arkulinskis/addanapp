from anvil import *
from anvil.js import window

from ._anvil_designer import AppsTemplate
from ... import apps_data, apps_fmt, router, state, ui

PC_HINT = "Audit, legal, screenshots, posts and new apps come from the PC: double-click Update Addanapp.bat in APP_MAKER\\board."


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
    if view == 'ads':
        from ...Components.ApAds import ApAds
        return ApAds(arg=arg)
    if view == 'youtube':
        from ...Components.ApYoutube import ApYoutube
        return ApYoutube()
    if view == 'dossier':
        from ...Components.ApDossier import ApDossier
        return ApDossier(arg=arg)
    if view == 'health':
        from ...Components.ApHealth import ApHealth
        return ApHealth()
    if view == 'notes':
        from ...Components.ApNotes import ApNotes
        return ApNotes()
    from ...Components.ApBoard import ApBoard
    return ApBoard()


class Apps(AppsTemplate):
    """#apps[/view[/arg]]: a client's app portfolio board (the App Board that ran on the user's PC until 2026-11-11).
    Views: board (a lane per stage), grid (every step as a tick square), posts, bizdev, money, ads, youtube, dossier (one app
    per page), notes (what needs the user or Claude), health (every app's status report; consultants only). The data loads once (apps_data) and is shared by the views; the
    router calls show_view() to switch without reloading. Refresh all checks every app from here, a few per call,
    with a progress line; nothing polls."""

    def __init__(self, view=None, arg=None, **properties):
        super().__init__(**properties)
        self.view, self.arg, self.part = '', None, None
        state.set_control_attr(self.search_box, "type", "search")
        state.set_control_attr(self.search_box, "aria-label", "Search apps")
        state.set_control_attr(self.client_dd, "aria-label", "Whose portfolio")
        state.heading(self.title, 1)
        self.search_box.text = apps_data.query()
        apps_data.listen(self._changed)
        apps_data.set_progress(self._progress)
        self.nothing.visible = False
        b = apps_data.load()
        if b is None or not b.get('projects'):
            self._empty()
            return
        self._head()
        self.show_view(view, arg)

    def _empty(self):
        self.title.text, self.sub.text = "Apps", ""
        for c in (self.pc_line, self.tabs, self.refresh_button, self.search_box, self.client_dd):
            c.visible = False
        self.nothing.visible = True

    # ---------------------------------------------------------------- drawing
    def _views(self):
        b = apps_data.board() or {}
        mods = b.get('modules') or apps_data.MODULE_VIEWS
        return [v for v in apps_data.VIEWS if (v[0] not in apps_data.MODULE_VIEWS or v[0] in mods)
                and (v[0] != 'health' or state.is_admin())]  # App health: consultants only

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
        self.pc_dot.classes["on"] = False
        parts = []
        if b.get('refreshed_at'):
            parts.append("Facts checked " + apps_fmt.ago(b['refreshed_at']))
        if b.get('pc_at'):
            parts.append("last PC update " + apps_fmt.ago(b['pc_at']))
        self.pc_text.text = (" · ".join(parts) + ". " if parts else "") + PC_HINT

    def _progress(self, done, total):
        """Refresh all's progress line (apps_data.ask_refresh)."""
        if done is None:
            self._pc()
            self.refresh_button.enabled = True
            return
        self.refresh_button.enabled = False
        self.pc_dot.classes["on"] = True
        self.pc_text.text = "Refreshing: %d of %d apps checked…" % (done, total)

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
        apps_data.ask_refresh(None)
