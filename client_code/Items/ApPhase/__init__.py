from anvil import *

from ._anvil_designer import ApPhaseTemplate
from ... import apps_data


class ApPhase(ApPhaseTemplate):
    """One stage of an app's checklist with its steps. item = {phase, project}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        ph, p = self.item["phase"], self.item["project"]
        self.dom_nodes["box"].style.setProperty("--c", apps_data.color(ph['id']))
        self.dom_nodes["name"].textContent = ph['name']
        steps = []
        done = 0
        for it in ph.get('items') or []:
            st = p['items'].get(it['id']) or {'v': 'todo', 'auto': False}
            done += st['v'] != 'todo'
            steps.append({"key": p['key'], "id": it['id'], "label": it['label'], "v": st['v'], "auto": st['auto'],
                          "auto_note": it.get('auto') or ''})
        self.dom_nodes["count"].textContent = "%d/%d" % (done, len(steps))
        self.steps.items = steps
