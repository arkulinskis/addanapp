from ._anvil_designer import RequestDetailTemplate
from anvil import *

from .. import ui, state, dialogs
from ..ui import esc
from ..icons import icon


class RequestDetail(RequestDetailTemplate):
  """One request: stepper, client actions, timeline of notes, details, and (for consultants) the manage panel."""

  def __init__(self, request_id, **properties):
    self.init_components(**properties)
    self.request_id = request_id
    self.data = None
    self.html = '<div class="app-page"><div class="aa-wrap js-root"></div></div>'
    ui.wire_segs(self)
    ui.bind(self, {
      'approve': lambda a: self.client_action('approve_quote'),
      'accept': lambda a: self.client_action('accept'),
      'changes': lambda a: self.ask_changes(),
      'question': lambda a: self.focus_composer(),
      'withdraw': lambda a: self.withdraw(),
      'post': lambda a: self.post(),
      'status': self.quick_status,
      'save': lambda a: self.save_manage(),
      'delete': lambda a: self.delete(),
      'to-manage': lambda a: self.focus_manage(),
    })
    self.load()

  # ------------------------------------------------------------ data
  def load(self):
    res = ui.call('get_request', self.request_id)
    if res is ui.FAIL:
      ui.q(self, '.js-root').innerHTML = ui.empty('inbox', "Request not available", "It may have been removed, or it belongs to another workspace.",
                                                  '<a class="aa-btn" href="#portal">Back to dashboard</a>')
      return
    self.apply(res)

  def apply(self, res):
    self.data = res
    self.render()
    if state.main is not None:
      state.main._poll()

  @property
  def admin(self):
    return bool(self.data and self.data.get('is_admin'))

  # ------------------------------------------------------------ render
  def render(self):
    r = self.data['request']
    root = ui.q(self, '.js-root')
    back = '#admin' if self.admin else '#portal'
    back_lbl = 'All requests' if self.admin else 'Dashboard'
    root.innerHTML = f'''
      <div class="crumbs"><a href="{back}">&larr; {back_lbl}</a><span>/</span><span class="mono">{esc(r["ref"])}</span></div>
      <div class="rd-title"><span class="chip mono">{esc(r["ref"])}</span>{ui.kind_chip(r["kind"])}{ui.priority_chip(r["priority"])}
        {('<span class="chip outline">' + esc(r["project"]) + '</span>') if r.get("project") else ''}</div>
      <h1 class="rd-h">{esc(r["title"])}</h1>
      {self._stepper(r)}
      {self._banner(r)}
      <div class="rd">
        <div>
          <div class="sec-card"><h3>Request</h3><div class="prose">{esc(r["description"])}</div></div>
          {('<div class="sec-card"><h3>Acceptance criteria</h3><div class="prose">' + esc(r["acceptance"]) + '</div></div>') if r.get("acceptance") else ''}
          {('<div class="sec-card" style="border-color:#CBD6FF"><h3>Scope &amp; quote</h3><div class="prose">' + esc(r["quote_note"]) + '</div></div>') if r.get("quote_note") and r.get("quote_amount") is not None else ''}
          <div class="sec-card"><h3>Activity</h3>
            <div class="tl">{self._timeline()}</div>
            {self._composer()}
          </div>
        </div>
        <div class="side">{self._side(r)}</div>
      </div>'''
    if self.admin:
      rng = root.querySelector('[name=m_progress]')
      pct = root.querySelector('.js-pct')

      def on_range(e):
        pct.textContent = str(rng.value) + '%'
      rng.addEventListener('input', on_range)

  def _stepper(self, r):
    st = r['status']
    keys = [k for k, _l in ui.PIPELINE]
    if st in ('on_hold', 'declined'):
      idx = -1
    else:
      idx = keys.index(st) if st in keys else 0
    out = '<div class="stepper" aria-label="Request progress">'
    for i, (k, label) in enumerate(ui.PIPELINE):
      cls = 'done' if (i < idx or (st == 'delivered' and i == idx)) else ('cur' if i == idx else '')
      out += f'<div class="s {cls}"><div class="b"></div><span>{label}</span></div>'
    return out + '</div>'

  def _banner(self, r):
    st = r['status']
    eta = (' · ETA ' + ui.fmt_date(r['eta'])) if r.get('eta') else ''
    if self.admin:
      m = {
        'new': ('accent', 'New request', 'Read it, ask questions in the thread, then start scoping.',
                '<button type="button" class="aa-btn sm" data-act="status" data-arg="scoping">Start scoping</button>'),
        'scoping': ('amber', 'Scoping', 'Set the fixed quote, scope summary and ETA in the panel, then send the quote.',
                    '<button type="button" class="aa-btn sm" data-act="to-manage">Prepare quote</button>'),
        'quoted': ('slate', 'Waiting for client approval', f'Quote sent: {ui.money(r.get("quote_amount"))}{eta}.', ''),
        'in_progress': ('slate', 'In progress', 'Post progress notes as you go. Mark ready when it has been validated.',
                        '<button type="button" class="aa-btn sm accent" data-act="status" data-arg="review">Mark ready for review</button>'),
        'review': ('accent', 'Waiting for client acceptance', 'The client is testing the delivery.',
                   '<button type="button" class="aa-btn sm ghost" data-act="status" data-arg="delivered">Mark delivered anyway</button>'),
        'delivered': ('green', 'Delivered and accepted', ('Accepted ' + ui.fmt_date(r.get('accepted_at')) + '. Ready to invoice ' + ui.money(r.get('quote_amount')) + '.') if r.get('accepted_at') else 'Delivered.', ''),
        'on_hold': ('amber', 'On hold', 'Resume by setting a new status in the panel.', ''),
        'declined': ('slate', 'Closed', 'This request is closed.', ''),
      }
    else:
      m = {
        'new': ('slate', "We've got it", 'An engineer will review your request and reply with a fixed quote, usually within two business days.',
                '<button type="button" class="aa-btn sm ghost" data-act="withdraw">Withdraw</button>'),
        'scoping': ('amber', 'Being scoped', 'Your engineer is defining scope and price. Watch the activity below for questions.', ''),
        'quoted': ('accent', f'Your fixed quote is ready: {ui.money(r.get("quote_amount"))}',
                   f'Fixed price for the agreed scope{eta}. Work starts as soon as you approve.',
                   '<button type="button" class="aa-btn sm ghost" data-act="question">Ask a question</button>'
                   '<button type="button" class="aa-btn sm green" data-act="approve">Approve quote</button>'),
        'in_progress': ('slate', 'In progress', f'Being built and validated{eta}. Progress notes appear below.', ''),
        'review': ('accent', 'Ready for your review', 'Test the delivery. Accept it if it meets the criteria, or tell us what should change.',
                   '<button type="button" class="aa-btn sm ghost" data-act="changes">Request changes</button>'
                   '<button type="button" class="aa-btn sm green" data-act="accept">Accept delivery</button>'),
        'delivered': ('green', 'Delivered', ('You accepted this on ' + ui.fmt_date(r.get('accepted_at')) + '. Thank you!') if r.get('accepted_at') else 'Delivered. Thank you!', ''),
        'on_hold': ('amber', 'On hold', 'This request is paused. See the latest note for details.', ''),
        'declined': ('slate', 'Closed', 'This request is closed.', ''),
      }
    cls, title, text, acts = m.get(st, ('slate', ui.STATUS.get(st, (st,))[0], '', ''))
    return (f'<div class="banner {cls}"><div><h4>{esc(title)}</h4><p>{esc(text)}</p></div>'
            f'<div class="acts">{acts}</div></div>')

  def _timeline(self):
    out = ''
    for n in self.data['notes']:
      a = n.get('author') or {'name': 'Addanapp', 'initials': 'AA', 'is_admin': True}
      when = f'<time title="{esc(ui.fmt_dt(n["created"]))}">{esc(ui.ago(n["created"]))}</time>'
      if n['kind'] == 'status':
        body = esc(n.get('body') or '')
        if n.get('status_from'):
          txt = f'<b>{esc(a["name"])}</b> moved this to {ui.status_chip(n["status_to"])}' + (f' · {body}' if body else '')
        else:
          txt = f'<b>{body or "Request submitted"}</b>'
        out += f'<div class="n sys"><div class="ico"><i></i></div><div class="txt">{txt} · {when}</div></div>'
        continue
      cls = 'n'
      if n.get('mine'):
        cls += ' mine'
      if n.get('internal'):
        cls += ' internal'
      tag = ''
      if n['kind'] in ui.NOTE_CHIP:
        label, ccls, ico = ui.NOTE_CHIP[n['kind']]
        tag = ui.chip(label, ccls, ico)
      role = '<span class="chip outline">Engineer</span>' if a.get('is_admin') else ''
      out += (f'<div class="{cls}">{ui.avatar(a, 36)}<div><div class="who"><b>{esc(a["name"])}</b>{role}{tag}{when}</div>'
              f'<div class="bubble">{esc(n["body"])}</div></div></div>')
    return out or '<p class="muted small">No activity yet.</p>'

  def _composer(self):
    r = self.data['request']
    if self.admin:
      return f'''
        <div class="composer js-composer">
          <textarea name="note_body" placeholder="Write a progress note for {esc((r.get("client") or {}).get("name", "the client"))}…"></textarea>
          <div class="bar"><div class="opts">
              <select name="note_kind" aria-label="Note type">{ui.options(ui.NOTE_KINDS, 'update')}</select>
            </div>
            <button type="button" class="aa-btn sm" data-act="post">Post note</button></div>
        </div>
        <p class="tiny muted" style="margin:8px 2px 0">Client-visible notes are emailed to the client. Internal notes stay private to consultants.</p>'''
    if r['status'] == 'declined':
      return ''
    return '''
      <div class="composer js-composer">
        <textarea name="note_body" placeholder="Ask a question or add details for your engineer…"></textarea>
        <div class="bar"><span class="tiny muted">Your engineer is notified by email.</span>
          <button type="button" class="aa-btn sm" data-act="post">Send</button></div>
      </div>'''

  def _side(self, r):
    done = r['status'] == 'delivered'
    status_card = f'''
      <div class="sec-card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px"><h3 style="margin:0;font-size:.8rem;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);font-family:var(--font-m)">Status</h3>{ui.status_chip(r["status"])}</div>
        <div class="big-pct"><b>{r["progress"]}%</b><span class="small muted">complete</span></div>
        {ui.progress_bar(r["progress"], done)}
      </div>'''
    kv = [('Fixed quote', ui.money(r.get('quote_amount')) if r.get('quote_amount') is not None else 'Pending'),
          ('ETA', ui.fmt_date(r.get('eta'), True) if r.get('eta') else '—'),
          ('Requested by', ui.fmt_date(r.get('desired_date'), True) if r.get('desired_date') else 'Flexible'),
          ('Priority', ui.PRIORITY.get(r.get('priority'), 'Normal')),
          ('Type', r.get('kind_label')),
          ('Budget', r.get('budget') or '—'),
          ('Submitted', ui.fmt_date(r.get('created'), True))]
    rows = ''.join(f'<div><span>{esc(k)}</span><span>{esc(v)}</span></div>' for k, v in kv)
    details = f'<div class="sec-card"><h3>Details</h3><div class="kv">{rows}</div></div>'
    if not self.admin:
      return status_card + details + ('<div class="sec-card"><h3>How billing works</h3><p class="small muted" style="margin:0">'
                                      'The fixed quote covers the agreed scope. You are invoiced only after you accept the delivery.</p></div>')
    c = r.get('client') or {}
    client = f'''
      <div class="sec-card"><h3>Client</h3>
        <div style="display:flex;gap:12px;align-items:center">{ui.avatar(c, 40)}<div><b style="color:var(--ink)">{esc(c.get("name"))}</b>
          <div class="small muted">{esc(c.get("company"))}</div>
          <a class="small" href="mailto:{esc(c.get("email"))}">{esc(c.get("email"))}</a></div></div></div>'''
    eta = ui.date_iso(r.get('eta')) if r.get('eta') else ''
    qa = '' if r.get('quote_amount') is None else str(int(r['quote_amount']))
    status_opts = ui.options([(k, ui.STATUS[k][0]) for k in ui.STATUS_ORDER], r['status'])
    manage = f'''
      <div class="sec-card manage js-manage" id="manage"><h3>Manage</h3>
        <div class="f"><label>Status</label><select name="m_status">{status_opts}</select></div>
        <div class="f"><label>Progress <span class="opt js-pct">{r["progress"]}%</span></label>
          <input class="range" type="range" min="0" max="100" step="5" name="m_progress" value="{r["progress"]}"></div>
        <div class="row2">
          <div class="f"><label>Fixed quote ($)</label><input type="number" min="0" step="50" name="m_quote" value="{qa}" placeholder="e.g. 2400"></div>
          <div class="f"><label>ETA</label><input type="date" name="m_eta" value="{eta}"></div>
        </div>
        <div class="f"><label>Scope summary (shown with the quote)</label><textarea name="m_quote_note" rows="4" placeholder="What's included, assumptions, exclusions…">{esc(r.get("quote_note"))}</textarea></div>
        <div class="f"><label>Priority</label><select name="m_priority">{ui.options(ui.PRIORITIES, r.get("priority"))}</select></div>
        <button type="button" class="aa-btn block" data-act="save">Save &amp; notify client</button>
        <button type="button" class="aa-btn danger block sm" style="margin-top:10px" data-act="delete">{icon("trash", 'width="14" height="14"')} Delete request</button>
      </div>'''
    html = status_card + client + manage + details
    return html

  # ------------------------------------------------------------ actions
  def client_action(self, action, comment=''):
    if action == 'approve_quote':
      r = self.data['request']
      if not ui.ask(f"Approve the fixed quote of {ui.money(r.get('quote_amount'))}? Work starts right away, and you're invoiced "
                    "only after you accept the delivery.", title='Approve quote', yes='Approve quote'):
        return
    if action == 'accept':
      if not ui.ask("Accept this delivery? This confirms it meets the agreed acceptance criteria.", title='Accept delivery',
                    yes='Accept delivery'):
        return
    res = ui.call('client_action', self.request_id, action, comment)
    if res is not ui.FAIL:
      self.apply(res)
      msgs = {'approve_quote': "Quote approved. The build starts now.", 'accept': "Accepted. Thank you!",
              'request_changes': "Changes requested. Your engineer is on it.", 'withdraw': "Request withdrawn."}
      if action in msgs:
        ui.toast(msgs[action])

  def ask_changes(self):
    text = dialogs.prompt_text('Request changes', 'What should be different? Reference the acceptance criteria where you can.',
                               'e.g. The refund email should go to the guest, not the manager.', ok='Send to engineer')
    if text:
      self.client_action('request_changes', text)

  def withdraw(self):
    if ui.ask("Withdraw this request? You can always submit it again later.", title='Withdraw request', yes='Withdraw'):
      self.client_action('withdraw')

  def focus_composer(self):
    ta = ui.q(self, '.js-composer textarea')
    if ta is not None:
      ta.scrollIntoView({'behavior': 'smooth', 'block': 'center'})
      ta.focus()

  def focus_manage(self):
    el = ui.q(self, '.js-manage')
    if el is not None:
      el.scrollIntoView({'behavior': 'smooth', 'block': 'start'})
      inp = el.querySelector('[name=m_quote]')
      if inp is not None:
        inp.focus()

  def post(self):
    box = ui.q(self, '.js-composer')
    v = ui.vals(box)
    body = v.get('note_body', '')
    if len(body) < 1:
      return ui.toast("Write something first.", 'warning')
    btn = box.querySelector('[data-act=post]')
    ui.busy(btn, True)
    if self.admin:
      kind = v.get('note_kind') or 'update'
      res = ui.call('admin_update_request', self.request_id, {}, {'body': body, 'kind': kind, 'internal': kind == 'internal'})
    else:
      res = ui.call('client_action', self.request_id, 'comment', body)
    ui.busy(btn, False)
    if res is not ui.FAIL:
      self.apply(res)
      ui.toast("Posted.")

  def quick_status(self, status):
    res = ui.call('admin_update_request', self.request_id, {'status': status}, None)
    if res is not ui.FAIL:
      self.apply(res)
      ui.toast(f"Status: {ui.STATUS[status][0]}")

  def save_manage(self):
    box = ui.q(self, '.js-manage')
    v = ui.vals(box)
    changes = {
      'status': v.get('m_status'), 'progress': int(v.get('m_progress') or 0),
      'quote_amount': float(v['m_quote']) if v.get('m_quote') else None,
      'quote_note': v.get('m_quote_note', ''), 'eta': ui.parse_date(v.get('m_eta')), 'priority': v.get('m_priority'),
    }
    btn = box.querySelector('[data-act=save]')
    ui.busy(btn, True, 'Saving…')
    res = ui.call('admin_update_request', self.request_id, changes, None)
    ui.busy(btn, False)
    if res is not ui.FAIL:
      self.apply(res)
      ui.toast("Saved.")

  def delete(self):
    r = self.data['request']
    if not ui.ask(f"Delete {r['ref']} and its whole history? This can't be undone.", title='Delete request', yes='Delete'):
      return
    if ui.call('admin_delete_request', self.request_id) is not ui.FAIL:
      ui.toast("Request deleted.")
      state.go('admin')
