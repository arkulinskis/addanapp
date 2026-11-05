from anvil import *

from ._anvil_designer import NoteItemTemplate
from ... import i18n, ui
from ...i18n import tp
from ...portfolio import esc


class NoteItem(NoteItemTemplate):
    """One entry in a request's activity: a status change (a quiet system line) or a note / comment with its author.
    item = a note dict from the server (serial.note)."""

    def __init__(self, **properties):
        super().__init__(**properties)
        n = self.item
        a = n.get('author') or {'name': 'Addanapp', 'initials': 'AA', 'is_admin': True}
        node = self.dom_nodes["n"]
        sys = n['kind'] == 'status'
        self.sys_ico.visible = self.sys_txt.visible = sys
        self.avatar.visible = self.body_part.visible = not sys
        when, title = str(ui.ago(n['created'])), str(ui.fmt_dt(n['created']))
        if sys:
            node.classList.add('sys')
            body = esc(i18n.server_text(n.get('body') or ''))
            if n.get('status_from'):
                label, cls, _c = ui.STATUS.get(n['status_to'], (n['status_to'] or '?', '', ''))
                chip = '<span class="chip %s"><span class="d"></span>%s</span>' % (cls, esc(label))
                html = i18n.t('{name} moved this to {status}', name='<b>%s</b>' % esc(a['name']), status=chip)
                html += (' · ' + body) if body else ''
            else:
                html = '<b>%s</b>' % (body or esc(tp('Request submitted')))
            self.dom_nodes["sys_text"].innerHTML = html
            self.dom_nodes["sys_time"].textContent = when
            self.dom_nodes["sys_time"].setAttribute("title", title)
            return
        if n.get('mine'):
            node.classList.add('mine')
        if n.get('internal'):
            node.classList.add('internal')
        self.avatar.person = a
        self.dom_nodes["who"].textContent = str(a.get('name') or '')
        if a.get('is_admin'):
            ui.chip(self.role_chip, tp('Engineer'), 'outline')
        else:
            self.role_chip.visible = False
        if n['kind'] in ui.NOTE_CHIP:
            label, cls, ico = ui.NOTE_CHIP[n['kind']]
            ui.chip(self.kind_chip, label, cls, ico=ico)
        else:
            self.kind_chip.visible = False
        self.dom_nodes["time"].textContent = when
        self.dom_nodes["time"].setAttribute("title", title)
        self.body.text = n['body']
