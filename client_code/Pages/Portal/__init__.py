from anvil import *

from ._anvil_designer import PortalTemplate
from ... import i18n, state, ui
from ...i18n import tp, tn

FILTERS = [('active', tp('Active')), ('action', tp('Needs you')), ('delivered', tp('Delivered')), ('closed', tp('Closed')),
           ('all', tp('All'))]


def filter_requests(reqs, f):
    if f == 'active':
        return [r for r in reqs if r['status'] in ui.OPEN_STATUSES]
    if f == 'action':
        return [r for r in reqs if r['status'] in ui.CLIENT_ACTION]
    if f == 'progress':
        return [r for r in reqs if r['status'] == 'in_progress']
    if f == 'delivered':
        return [r for r in reqs if r['status'] == 'delivered']
    if f == 'closed':
        return [r for r in reqs if r['status'] == 'declined']
    return reqs


class Portal(PortalTemplate):
    """#portal: a client's dashboard: what needs their attention, counts, and every request (filter + search)."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.filter, self.search = 'active', ''
        self.data: dict = {}
        self.tiles.add_event_handler("x-pick", self._pick)
        self.pills.add_event_handler("x-pick", self._pick)
        state.set_control_attr(self.search_box, "type", "search")
        state.set_control_attr(self.search_box, "aria-label", tp('Search requests'))
        i18n.apply(self)
        me = state.me() or {}
        company = me.get('company')
        self.eyebrow.text = i18n.plain(tp('{company} workspace', company=company)) if company else tp('Your workspace')
        self.hello.text = tp('{greeting}, {name}.', greeting=ui.greeting(), name=ui.first_name(me))
        state.heading(self.hello, 1)
        self.first_run.visible = self.main_part.visible = False
        res = ui.call('my_requests')
        if res is not ui.FAIL:
            self.data = res
            self._draw()

    def _draw(self):
        st, reqs = self.data['stats'], self.data['requests']
        self.counts.text = tp('{open} · {delivered} accepted', open=tn(st['open'], '{n} open request', '{n} open requests'),
                              delivered=tn(st['delivered'], '{n} delivery', '{n} deliveries'))
        self.first_run.visible = not reqs
        self.main_part.visible = bool(reqs)
        if not reqs:
            return
        action = [r for r in reqs if r['status'] in ui.CLIENT_ACTION]
        self.attn_box.visible = bool(action)
        self.attn.items = action
        f = self.filter
        self.tiles.items = [
            {"key": 'active', "value": st['open'], "label": tp('Open'), "color": '#182031', "on": f == 'active'},
            {"key": 'action', "value": st['action'], "label": tp('Needs you'), "color": '#2F5BFF', "on": f == 'action',
             "attn": bool(st['action'])},
            {"key": 'progress', "value": st['in_progress'], "label": tp('In progress'), "color": '#7A5CFA', "on": f == 'progress'},
            {"key": 'delivered', "value": st['delivered'], "label": tp('Delivered'), "color": '#0E9F6E', "on": f == 'delivered'}]
        self.pills.items = [{"key": k, "label": label, "on": f == k} for k, label in FILTERS]
        self._draw_list()

    def _draw_list(self):
        reqs = filter_requests(self.data['requests'], self.filter)
        s = self.search
        if s:
            reqs = [r for r in reqs if s in (r['title'] + ' ' + r['ref'] + ' ' + r['description']).lower()]
        self.rows.items = [dict(r, _admin=False) for r in reqs]
        self.list.visible = bool(reqs)
        self.none.visible = not reqs

    def _pick(self, key, **event_args):
        self.filter = key
        self._draw()

    @handle("search_box", "change")
    def search_box_change(self, **event_args):
        self.search = (self.search_box.text or '').strip().lower()
        self._draw_list()
