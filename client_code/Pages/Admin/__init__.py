from anvil import *
import anvil.media

from ._anvil_designer import AdminTemplate
from ... import i18n, router, state, ui
from ...i18n import tp, tn

BOARD_COLS = ['new', 'scoping', 'quoted', 'in_progress', 'review', 'delivered']
LEAD_FILTERS = [('all', tp('All')), ('briefs', tp('Project briefs')), ('guides', tp('Guide readers'))]
_PENDING: dict = {}  # a client's "View requests" (Clients tab) -> the Requests tab opens filtered to them


class Admin(AdminTemplate):
    """#admin[/requests|clients|leads|tools]: the consultant console. Requests as a list or a board (filters, client,
    search), clients and consultants, website leads (project briefs and guide readers), and demo data."""

    def __init__(self, tab='requests', **properties):
        super().__init__(**properties)
        self.tab = tab
        self.view, self.filter, self.client_filter, self.search, self.lead_filter = 'list', 'open', '', '', 'all'
        if tab == 'requests' and _PENDING.get("client"):
            self.client_filter, self.filter = _PENDING.pop("client"), 'all'
        self.data: dict = {}
        self.clients_cache = None
        self.leads_data: list = []
        for panel in (self.tiles, self.pills):
            panel.add_event_handler("x-pick", self._set_filter)
        self.views.add_event_handler("x-pick", self._set_view)
        self.lead_filters.add_event_handler("x-pick", self._set_lead_filter)
        self.people.add_event_handler("x-new-for", self._new_for)
        self.people.add_event_handler("x-client-requests", self._client_requests)
        self.people.add_event_handler("x-changed", lambda **e: self.show_clients(reload=True))
        self.leads.add_event_handler("x-changed", lambda **e: self.show_leads())
        state.set_control_attr(self.client_dd, "aria-label", tp('Filter by client'))
        state.set_control_attr(self.search_box, "type", "search")
        state.set_control_attr(self.search_box, "aria-label", tp('Search'))
        i18n.apply(self)
        c = state.counts() or {}
        self.n_requests.text, self.n_leads.text = str(c.get('unread', 0)), str(c.get('leads', 0))
        self.tab_requests_n.visible = bool(c.get('unread'))
        self.tab_leads_n.visible = bool(c.get('leads'))
        for name in ('requests', 'clients', 'leads', 'tools'):
            getattr(self, 'tab_' + name).classes['on'] = name == tab
            getattr(self, name + '_part').visible = name == tab
        self.new_button.visible = tab == 'requests'
        self.lead_acts.visible = tab == 'leads'
        getattr(self, 'show_' + tab)()

    def _head(self, title, sub):
        self.title.text, self.sub.text = title, sub
        state.heading(self.title, 1)

    # ================================================================ requests
    def show_requests(self):
        res = ui.call('admin_overview')
        if res is ui.FAIL:
            return
        self.data = res
        self._draw_requests()

    def _draw_requests(self):
        reqs = self.data['requests']
        open_n = len([r for r in reqs if r['status'] in ui.OPEN_STATUSES])
        unread = len([r for r in reqs if r.get('unread')])
        self._head(tp('Requests'), tp('{open} across {clients} · {unread} unread', open=tn(open_n, '{n} open request', '{n} open requests'),
                                      clients=tn(len(self.data['clients']), '{n} client', '{n} clients'), unread=unread))

        def count(fn):
            return len([r for r in reqs if fn(r)])
        f = self.filter
        tiles = [('unread', tp('Unread'), count(lambda r: r.get('unread')), '#2F5BFF'),
                 ('new', tp('New'), count(lambda r: r['status'] == 'new'), '#8C94A3'),
                 ('scoping', tp('Scoping'), count(lambda r: r['status'] == 'scoping'), '#B7791F'),
                 ('waiting', tp('Waiting on client'), count(lambda r: r['status'] in ('quoted', 'review')), '#2F5BFF'),
                 ('in_progress', tp('In progress'), count(lambda r: r['status'] == 'in_progress'), '#7A5CFA'),
                 ('delivered', tp('Delivered'), count(lambda r: r['status'] == 'delivered'), '#0E9F6E')]
        self.tiles.items = [{"key": k, "label": label, "value": n, "color": color, "on": f == k, "attn": k == 'unread' and n > 0}
                            for k, label, n, color in tiles]
        self.pills.items = [{"key": k, "label": label, "on": f == k} for k, label in
                            (('open', tp('Open')), ('all', tp('All')), ('declined', tp('Closed')))]
        self.views.items = [{"key": k, "label": label, "icon": ic, "on": self.view == k}
                            for k, label, ic in (('list', tp('List'), 'list'), ('board', tp('Board'), 'columns'))]
        self.client_dd.items = [(tp('All clients'), '')] + [((c.get('company') + ' · ' if c.get('company') else '') + c['name'], c['id'])
                                                            for c in self.data['clients']]
        self.client_dd.selected_value = self.client_filter
        self._draw_list()

    def _filtered(self):
        reqs, f = self.data['requests'], self.filter
        if self.view == 'board' and f in ('open', 'all'):
            pass
        elif f == 'open':
            reqs = [r for r in reqs if r['status'] in ui.OPEN_STATUSES]
        elif f == 'unread':
            reqs = [r for r in reqs if r.get('unread')]
        elif f == 'waiting':
            reqs = [r for r in reqs if r['status'] in ('quoted', 'review')]
        elif f in ui.STATUS:
            reqs = [r for r in reqs if r['status'] == f]
        if self.client_filter:
            reqs = [r for r in reqs if (r.get('client') or {}).get('id') == self.client_filter]
        s = self.search
        if s:
            reqs = [r for r in reqs if s in (r['title'] + ' ' + r['ref'] + ' ' + (r.get('client') or {}).get('name', '') + ' '
                                             + (r.get('client') or {}).get('company', '')).lower()]
        return reqs

    def _draw_list(self):
        reqs = self._filtered()
        board = self.view == 'board'
        self.board.visible = board
        self.list.visible = not board and bool(reqs)
        self.none.visible = not board and not reqs
        if board:
            self.columns.items = [{"status": st, "requests": [r for r in reqs if r['status'] == st]} for st in BOARD_COLS]
        else:
            self.rows.items = [dict(r, _admin=True) for r in reqs]

    def _set_filter(self, key, **event_args):
        self.filter = key
        self._draw_requests()

    def _set_view(self, key, **event_args):
        self.view = key
        self._draw_requests()

    @handle("client_dd", "change")
    def client_dd_change(self, **event_args):
        self.client_filter = self.client_dd.selected_value or ''
        self._draw_list()

    @handle("search_box", "change")
    def search_box_change(self, **event_args):
        self.search = (self.search_box.text or '').strip().lower()
        self._draw_list()

    @handle("new_button", "click")
    def new_button_click(self, **event_args):
        self._new_for(None)

    def _new_for(self, client_id=None, **event_args):
        clients = [c for c in self._clients() if not c.get('is_admin')]
        if not clients:
            state.toast(tp("No clients yet. Clients appear once they create a workspace (or load demo data)."), "error")
            return
        from ...Dialogs.NewForClient import NewForClient
        rid = alert(NewForClient(clients=clients, client_id=client_id), buttons=[], large=True, role="aa-dialog")
        if rid:
            state.toast(tp("Request created."), "ok")
            router.go('r/' + rid)

    # ================================================================ clients
    def _clients(self):
        if self.clients_cache is None:
            res = ui.call('admin_clients')
            self.clients_cache = [] if res is ui.FAIL else res
        return self.clients_cache

    def show_clients(self, reload=False):
        if reload:
            self.clients_cache = None
        people = self._clients()
        clients = [p for p in people if not p.get('is_admin')]
        self._head(tp('Clients'), tn(len(clients), '{n} client', '{n} clients') + ' · ' +
                   tn(len(people) - len(clients), '{n} consultant', '{n} consultants'))
        me_id = (state.me() or {}).get('id')
        self.people.items = [dict(p, _me=p['id'] == me_id) for p in people]
        self.no_people.visible = not people

    def _client_requests(self, client_id, **event_args):
        """A client's "View requests": the Requests tab, all of that client's requests."""
        _PENDING["client"] = client_id
        router.go('admin')

    # ================================================================ leads
    def show_leads(self):
        res = ui.call('admin_leads')
        if res is ui.FAIL:
            return
        self.leads_data = res
        new = len([x for x in res if x['status'] == 'new' and not x['source'].startswith('guide')])
        readers = [x for x in res if x['source'].startswith('guide')]
        tips = len([x for x in readers if x['source'] == 'guide+news'])
        self._head(tp('Leads'), tp('Project briefs from the website · {n} new', n=new) + ' · ' +
                   tp('{n} guide readers, {k} want tips', n=len(readers), k=tips))
        lf = self.lead_filter
        self.lead_filters.items = [{"key": k, "label": label, "on": k == lf, "cls": "aa-btn sm" + ("" if k == lf else " ghost")}
                                   for k, label in LEAD_FILTERS]
        self.csv_button.visible = bool(tips)
        if lf == 'briefs':
            res = [x for x in res if not x['source'].startswith('guide')]
        elif lf == 'guides':
            res = readers
        self.leads.items = res
        self.no_leads.visible = not res

    def _set_lead_filter(self, key, **event_args):
        self.lead_filter = key if key in ('all', 'briefs', 'guides') else 'all'
        self.show_leads()

    @handle("csv_button", "click")
    def csv_button_click(self, **event_args):
        media = ui.call('admin_newsletter_csv')
        if media is not ui.FAIL and media is not None:
            anvil.media.download(media)

    # ================================================================ tools
    def show_tools(self):
        self._head(tp('Tools'), tp('Demo content and site checks.'))

    @handle("seed_button", "click")
    def seed_button_click(self, **event_args):
        self._tool('admin_seed_demo')

    @handle("clear_button", "click")
    def clear_button_click(self, **event_args):
        if confirm(tp("Remove all demo clients and their requests?"), buttons=[(tp('Cancel'), False), (tp('Remove'), True)]):
            self._tool('admin_clear_demo')

    def _tool(self, fn):
        res = ui.call(fn)
        if res is not ui.FAIL:
            state.toast(i18n.plain(i18n.server_text(res)), "ok")
            self.clients_cache = None
            sh = router.shell()
            if sh is not None:
                sh.poll_timer_tick()
