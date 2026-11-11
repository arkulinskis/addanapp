from anvil import *

from ._anvil_designer import ApBoardTemplate
from ... import apps_data, state

ORDERS = [("Recently pushed", "recent"), ("Most progress", "progress"), ("Name A–Z", "name")]


def ordered(projects, how):
    if how == 'name':
        return sorted(projects, key=lambda p: p['name'].lower())
    if how == 'progress':
        return sorted(projects, key=lambda p: (-p['done'], p['name'].lower()))
    return sorted(sorted(projects, key=lambda p: p['name'].lower()), key=lambda p: p.get('pushed_at') or '', reverse=True)


class ApBoard(ApBoardTemplate):
    """#apps/board: one lane per stage (Build, Deploy, Test, Promote, Standard, Components, Launched, Parked); an app
    sits in the lane of the first stage that still has a step to do."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.order_dd.items = ORDERS
        self.order_dd.selected_value = state.store_get('apps.order', 'recent')
        state.set_control_attr(self.order_dd, "id", "ap-order")
        self.lanes.add_event_handler("x-fold", self._fold)
        self.redraw()

    def redraw(self, key=None):
        b = apps_data.board() or {}
        folded = apps_data.sget('apps.folded', None) or {'parked': True}
        vis = apps_data.visible()
        how = self.order_dd.selected_value or 'recent'
        self.lanes.items = [{"id": ln['id'], "name": ln['name'], "desc": ln['desc'], "folded": bool(folded.get(ln['id'])),
                             "cards": ordered([p for p in vis if p['stage'] == ln['id']], how)}
                            for ln in b.get('lanes') or []]

    def _fold(self, lane, **event_args):
        folded = dict(apps_data.sget('apps.folded', None) or {'parked': True})
        folded[lane] = not folded.get(lane)
        apps_data.sset('apps.folded', folded)
        self.redraw()

    @handle("order_dd", "change")
    def order_dd_change(self, **event_args):
        state.store_set('apps.order', self.order_dd.selected_value)
        self.redraw()
