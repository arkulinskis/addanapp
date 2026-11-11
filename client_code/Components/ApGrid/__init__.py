from anvil import *
import anvil.js

from ._anvil_designer import ApGridTemplate
from ... import apps_data, router, state
from ..ApBoard import ordered

SHOWS = [("All apps", ""), ("Branches to merge", "merge"), ("Changes queued for Claude", "changes"), ("Live", "live"),
         ("Not live yet", "notlive"), ("Legal or SEO issues", "issues"), ("Database schema mismatch", "schema")]
BASE = [{"id": "stage", "label": "Stage"}, {"id": "live", "label": "Live"}, {"id": "merge", "label": "Merge"}]
VALUE_ORDER = {'todo': 0, 'na': 1, 'done': 2}


class ApGrid(ApGridTemplate):
    """#apps/grid: every app as a row, every step as a tick square (drawn by apps.js: 1,000+ squares), with sort and
    filters remembered in this browser. A tick redraws only its row."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.g: dict = dict({'sort': 'stage', 'dir': 1, 'stage': '', 'show': '', 'step': '', 'stepv': 'todo'}, **(apps_data.sget('apps.grid', None) or {}))
        b = apps_data.board() or {}
        self.stage_dd.items = [("All stages", "")] + [(ln['name'], ln['id']) for ln in b.get('lanes') or []]
        self.show_dd.items = SHOWS
        self.step_dd.items = [("Any step", "")] + [(ph['name'] + ": " + it['label'], it['id']) for ph in b.get('phases') or [] for it in ph.get('items') or []]
        self.stepv_dd.items = [("is still to do", "todo"), ("is done", "done"), ("is not needed", "na")]
        for dd, label in ((self.stage_dd, "Only apps in this stage"), (self.show_dd, "Only apps that"), (self.step_dd, "Only apps where this step"),
                          (self.stepv_dd, "is")):
            state.set_control_attr(dd, "aria-label", label)
        self.redraw()

    def _match(self, p):
        g = self.g
        if g['stage'] and p['stage'] != g['stage']:
            return False
        s = g['show']
        lv = p.get('live') or {}
        if s == 'merge' and not p.get('branches'):
            return False
        if s == 'changes' and not p.get('changes_todo'):
            return False
        if s == 'live' and not lv.get('ok'):
            return False
        if s == 'notlive' and lv.get('ok'):
            return False
        if s == 'schema' and (p.get('schema') or {}).get('state') != 'mismatch':
            return False
        if s == 'issues' and not ((p.get('legal') and not p['legal'].get('ok')) or (p.get('seo') or {}).get('missing')):
            return False
        if g['step'] and (p['items'].get(g['step']) or {}).get('v') != g['stepv']:
            return False
        return True

    def _row(self, p):
        lv = p.get('live') or {}
        live = '' if not p.get('url') or not p.get('live') else ('ok' if lv.get('ok') else 'bad')
        return {"key": p['key'], "name": p['name'], "stage": p['stage'], "stage_name": p['stage_name'], "stage_color": apps_data.color(p['stage']),
                "live": live, "url": p.get('url') or '', "live_title": apps_data.live_text(p),
                "merge": len(p.get('branches') or []), "merge_names": ', '.join(x.get('name', '') for x in p.get('branches') or []),
                "cells": {k: v['v'] for k, v in p['items'].items()}, "auto": {k: v['auto'] for k, v in p['items'].items()}}

    def _sorted(self, rows):
        b = apps_data.board() or {}
        order = {ln['id']: i for i, ln in enumerate(b.get('lanes') or [])}
        col, d = self.g['sort'], int(self.g['dir'])

        def key(p):
            if col == 'name':
                return p['name'].lower()
            if col == 'stage':
                return order.get(p['stage'], 99)
            if col == 'live':
                lv = p.get('live')
                return 0 if not lv else (2 if lv.get('ok') else 1)
            if col == 'merge':
                return len(p.get('branches') or [])
            return VALUE_ORDER.get((p['items'].get(col) or {}).get('v'), 0)
        base = sorted(ordered(rows, 'recent'), key=lambda p: order.get(p['stage'], 99))
        return sorted(base, key=key, reverse=d < 0)

    def redraw(self, key=None):
        js = apps_data.js()
        host = self.dom_nodes["host"]
        if key and js:
            p = apps_data.project(key)
            if p and js.gridRow(host, self._row(p)):
                return
        b = apps_data.board() or {}
        g = self.g
        self.stage_dd.selected_value = g['stage']
        self.show_dd.selected_value = g['show']
        self.step_dd.selected_value = g['step']
        self.stepv_dd.selected_value = g['stepv']
        self.stepv_dd.visible = bool(g['step'])
        self.clear_button.visible = bool(g['stage'] or g['show'] or g['step'])
        vis = apps_data.visible()
        shown = self._sorted([p for p in vis if self._match(p)])
        self.count.text = ("%d apps" % len(vis)) if len(shown) == len(vis) else "Showing %d of %d apps" % (len(shown), len(vis))
        short = b.get('short') or {}
        cols = [{"id": it['id'], "label": it['label'], "short": short.get(it['id'], it['label']), "color": apps_data.color(it['phase'])}
                for it in apps_data.items()]
        phases = [{"name": ph['name'], "n": len(ph.get('items') or []), "color": apps_data.color(ph['id'])} for ph in b.get('phases') or [] if ph.get('items')]
        model = {"base": BASE, "cols": cols, "phases": phases, "rows": [self._row(p) for p in shown], "sort": g['sort'], "dir": g['dir']}
        if js:
            js.grid(host, model, {"cell": anvil.js.report_exceptions(self._cell), "sort": anvil.js.report_exceptions(self._sort),
                                  "open": anvil.js.report_exceptions(lambda k: router.go("app/" + k))})

    def _save(self):
        apps_data.sset('apps.grid', self.g)
        self.redraw()

    def _cell(self, key, item_id):
        apps_data.tick(key, item_id)

    def _sort(self, col):
        if self.g['sort'] == col:
            self.g['dir'] = -int(self.g['dir'])
        else:
            self.g['sort'], self.g['dir'] = col, (-1 if col == 'merge' else 1)
        self._save()

    @handle("stage_dd", "change")
    def stage_dd_change(self, **event_args):
        self.g['stage'] = self.stage_dd.selected_value or ''
        self._save()

    @handle("show_dd", "change")
    def show_dd_change(self, **event_args):
        self.g['show'] = self.show_dd.selected_value or ''
        self._save()

    @handle("step_dd", "change")
    def step_dd_change(self, **event_args):
        self.g['step'] = self.step_dd.selected_value or ''
        self._save()

    @handle("stepv_dd", "change")
    def stepv_dd_change(self, **event_args):
        self.g['stepv'] = self.stepv_dd.selected_value or 'todo'
        self._save()

    @handle("clear_button", "click")
    def clear_button_click(self, **event_args):
        self.g.update(stage='', show='', step='')
        self._save()
