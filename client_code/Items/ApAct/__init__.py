from anvil import *

from ._anvil_designer import ApActTemplate
from ... import apps_data, router, state


class ApAct(ApActTemplate):
    """A quick action on a notification: a link ({label, href}) or a button ({label, do, key}) where do is
    refresh | refresh-all | posts | grid-merge | grid-schema."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        if it.get('href'):
            a = self.dom_nodes["link"]
            a.textContent = it['label']
            a.setAttribute("href", it['href'])
            if str(it['href']).startswith('http'):
                a.setAttribute("target", "_blank")
                a.setAttribute("rel", "noopener")
            self.dom_nodes["btn"].remove()
        else:
            self.dom_nodes["btn"].textContent = it['label']
            self.dom_nodes["link"].remove()

    def btn_click(self, event):
        it = self.item
        do, key = it.get('do'), it.get('key') or None
        if do in ('refresh', 'refresh-all'):
            from ...Dialogs.ApRefresh import ApRefresh
            k = key if do == 'refresh' else None
            acts = alert(ApRefresh(key=k), buttons=[], large=False, role="aa-dialog", dismissible=True)
            if acts:
                apps_data.queue('refresh', k, {'actions': acts})
        elif do == 'posts':
            router.go("apps/posts/" + (key or ''))
        elif do in ('grid-merge', 'grid-schema'):
            g = dict(apps_data.sget('apps.grid', None) or {})
            g.update(stage='', step='', show='merge' if do == 'grid-merge' else 'schema')
            if do == 'grid-merge':
                g.update(sort='merge', dir=-1)
            apps_data.sset('apps.grid', g)
            router.go("apps/grid")
