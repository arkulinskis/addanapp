from anvil import *
import anvil.server

from ._anvil_designer import RequestDetailTemplate
from ... import i18n, router, state, ui
from ...i18n import tp


class RequestDetail(RequestDetailTemplate):
    """#r/<id>: one request: stepper, the next step (banner with its buttons), description, acceptance criteria,
    quote, the activity timeline with a composer, status and details; consultants also get the client and Manage."""

    def __init__(self, request_id, **properties):
        super().__init__(**properties)
        self.request_id = request_id
        self.data: dict = {}
        self.note_kind.items = ui.dd_items(ui.NOTE_KINDS)
        self.m_status.items = [(ui.STATUS[k][0], k) for k in ui.STATUS_ORDER]
        self.m_prio.items = ui.dd_items(ui.PRIORITIES)
        state.date_box(self.m_eta)
        state.set_control_attr(self.m_quote, "min", 0)
        state.set_control_attr(self.m_quote, "step", 50)
        state.set_control_attr(self.note_kind, "aria-label", tp('Note type'))
        i18n.apply(self)
        self.missing.visible = self.main_part.visible = False
        try:
            res = anvil.server.call('get_request', request_id)
        except Exception:
            res = None  # removed, or another workspace's: a friendly page instead of an error
        if res:
            self._apply(res)
        else:
            self.missing.visible = True

    @property
    def admin(self):
        return bool(self.data and self.data.get('is_admin'))

    def _apply(self, res):
        self.data = res
        self._draw()
        sh = router.shell()
        if sh is not None:
            sh.poll_timer_tick()  # opening a request marks it read: refresh the header counts

    # ---------------------------------------------------------------- drawing
    def _draw(self):
        r = self.data['request']
        admin = self.admin
        self.main_part.visible = True
        state.set_attr(self.back_link, "href", "#admin" if admin else "#portal")
        self.back_label.text = tp('All requests') if admin else tp('Dashboard')
        self.dom_nodes["crumb_ref"].textContent = r["ref"]
        ui.chip(self.ref_chip, r["ref"], 'mono')
        ui.chip(self.kind_chip, ui.KIND.get(r["kind"], r.get("kind_label") or tp('Request')), 'outline')
        ui.priority_chip(self.prio_chip, r["priority"])
        ui.chip(self.project_chip, r.get("project") or '', 'outline')
        self.title.text = r["title"]
        state.heading(self.title, 1)
        self.steps.items = self._steps(r['status'])
        self._banner(r)
        self.desc.text = r["description"]
        self.acc.text = r.get("acceptance") or ''
        self.acc_card.visible = bool(r.get("acceptance"))
        self.scope.text = r.get("quote_note") or ''
        self.scope_card.visible = bool(r.get("quote_note")) and r.get("quote_amount") is not None
        self.notes.items = self.data['notes']
        self.no_notes.visible = not self.data['notes']
        self._composer(r)
        ui.status_chip(self.status_chip, r["status"])
        self.dom_nodes["pct"].textContent = "%d%%" % r["progress"]
        self.progress.value = r["progress"]
        self.progress.done = r["status"] == 'delivered'
        self.client_card.visible = self.manage.visible = admin
        self.billing.visible = not admin
        so = self.data.get('signoff')
        # the record: consultants always see it (draft or not); the client once the delivery is in review or later
        self.signoff_card.record = so if so and (admin or (so.get('complete') and r['status'] in ('review', 'delivered'))) else None
        if admin:
            self._manage(r)
        self.kv.items = self._details(r)

    def _steps(self, st):
        keys = [k for k, _l in ui.PIPELINE]
        idx = -1 if st in ('on_hold', 'declined') else (keys.index(st) if st in keys else 0)
        out = []
        for i, (k, label) in enumerate(ui.PIPELINE):
            done = i < idx or (st == 'delivered' and i == idx)
            out.append({"label": label, "state": 'done' if done else ('cur' if i == idx else '')})
        return out

    def _banner(self, r):
        st = r['status']
        co = self.data.get('pending_change')
        if co and st not in ('delivered', 'declined'):
            return self._banner_change(r, co)
        signed = self.data.get('signoff_ready') or not self.data.get('needs_signoff')
        eta = (' · ' + tp('ETA {date}', date=ui.fmt_date(r['eta']))) if r.get('eta') else ''
        amount = ui.money(r.get('quote_amount'))
        if self.admin:
            m = {
                'new': ('accent', tp('New request'), tp('Read it, ask questions in the thread, then start scoping.'),
                        [('', 'status:scoping', tp('Start scoping'))]),
                'scoping': ('amber', tp('Scoping'), tp('Set the fixed quote, scope summary and ETA in the panel, then send the quote.'),
                            [('', 'manage', tp('Prepare quote'))]),
                'quoted': ('slate', tp('Waiting for client approval'), tp('Quote sent: {amount}{eta}.', amount=amount, eta=eta), []),
                'in_progress': (('slate', tp('In progress'), tp('Post progress notes as you go. Mark ready when it has been validated.'),
                                 [('accent', 'status:review', tp('Mark ready for review'))]) if signed else
                                ('slate', tp('In progress'), tp('Post progress notes as you go. Sign off the delivery, then mark it ready for review.'),
                                 [('green', 'signoff', tp('Sign off delivery'))])),
                'review': ('accent', tp('Waiting for client acceptance'), tp('The client is testing the delivery.'),
                           [('ghost', 'status:delivered', tp('Mark delivered anyway'))]),
                'delivered': ('green', tp('Delivered and accepted'),
                              tp('Accepted {date}. Ready to invoice {amount}.', date=ui.fmt_date(r.get('accepted_at')), amount=amount)
                              if r.get('accepted_at') else tp('Delivered.'), []),
                'on_hold': ('amber', tp('On hold'), tp('Resume by setting a new status in the panel.'), []),
                'declined': ('slate', tp('Closed'), tp('This request is closed.'), []),
            }
        else:
            m = {
                'new': ('slate', tp("We've got it"), tp('An engineer will review your request and reply with a fixed quote, usually within two business days.'),
                        [('ghost', 'withdraw', tp('Withdraw'))]),
                'scoping': ('amber', tp('Being scoped'), tp('Your engineer is defining scope and price. Watch the activity below for questions.'), []),
                'quoted': ('accent', tp('Your fixed quote is ready: {amount}', amount=amount),
                           tp('Fixed price for the agreed scope{eta}. Work starts as soon as you approve.', eta=eta),
                           [('ghost', 'question', tp('Ask a question')), ('green', 'approve', tp('Approve quote'))]),
                'in_progress': ('slate', tp('In progress'), (tp('Being built and validated{eta}. Progress notes appear below.', eta=eta) +
                                (' ' + tp('Your approved quote of {amount} is locked.', amount=amount) if self.data.get('locked') else '')), []),
                'review': ('accent', tp('Ready for your review'), tp('Test the delivery. Accept it if it meets the criteria, or tell us what should change.'),
                           [('ghost', 'changes', tp('Request changes')), ('green', 'accept', tp('Accept delivery'))]),
                'delivered': ('green', tp('Delivered'), tp('You accepted this on {date}. Thank you!', date=ui.fmt_date(r.get('accepted_at')))
                              if r.get('accepted_at') else tp('Delivered. Thank you!'), []),
                'on_hold': ('amber', tp('On hold'), tp('This request is paused. See the latest note for details.'), []),
                'declined': ('slate', tp('Closed'), tp('This request is closed.'), []),
            }
        cls, title, text, acts = m.get(st, ('slate', ui.STATUS.get(st, (st,))[0], '', []))
        for c in ('accent', 'amber', 'slate', 'green'):
            self.banner.classes[c] = c == cls
        self.banner_title.text, self.banner_text.text = title, text
        for btn, act in ((self.act1, acts[0] if len(acts) > 0 else None), (self.act2, acts[1] if len(acts) > 1 else None)):
            btn.visible = act is not None
            if act:
                variant, key, label = act
                btn.text, btn.tag = label, key
                btn.role = ['aa-btn', 'sm'] + ([variant] if variant else [])

    def _banner_change(self, r, co):
        delta = (co.get('amount_after') or 0) - (co.get('amount_before') or 0)
        price = int(round(delta)) != 0
        what = tp('Change order: {delta} (new total {total})', delta=self._delta(delta), total=ui.money(co.get('amount_after'))) \
            if price else tp('Change order: new ETA {date}', date=ui.fmt_date(co.get('eta_after')))
        eta = (tp('New ETA {date}.', date=ui.fmt_date(co.get('eta_after'))) + ' ') if price and co.get('eta_changed') else ''
        if self.admin:
            title = tp('Sent to the client: {what}', what=what)
            text = tp('Waiting for their OK. The approved price and ETA stay until they approve.')
            acts = [('ghost', 'co_cancel', tp('Withdraw change order'))]
        else:
            title = what
            text = eta + tp('Why: {reason}', reason=co.get('reason') or '') + ' ' + tp('Nothing changes unless you approve it.')
            acts = [('ghost', 'co_decline', tp('Keep the original scope')), ('green', 'co_approve', tp('Approve change'))]
        for c in ('accent', 'amber', 'slate', 'green'):
            self.banner.classes[c] = c == 'amber'
        self.banner_title.text, self.banner_text.text = title, text
        for btn, act in ((self.act1, acts[0] if len(acts) > 0 else None), (self.act2, acts[1] if len(acts) > 1 else None)):
            btn.visible = act is not None
            if act:
                variant, key, label = act
                btn.text, btn.tag = label, key
                btn.role = ['aa-btn', 'sm'] + ([variant] if variant else [])

    @staticmethod
    def _delta(d):
        d = int(round(d or 0))
        return ('+' if d >= 0 else '-') + ui.money(abs(d))

    def _composer(self, r):
        admin = self.admin
        self.composer_part.visible = admin or r['status'] != 'declined'
        self.note_opts.visible = self.admin_hint.visible = admin
        self.client_hint.visible = not admin
        self.post_button.text = tp('Post note') if admin else tp('Send')
        if admin:
            cname = (r.get("client") or {}).get("name")
            self.note_box.placeholder = (tp('Write a progress note for {name}…', name=cname) if cname
                                         else tp('Write a progress note for the client…'))
            self.note_kind.selected_value = 'update'
        else:
            self.note_box.placeholder = tp('Ask a question or add details for your engineer…')
        state.set_control_attr(self.note_box, "aria-label", self.note_box.placeholder)

    def _manage(self, r):
        c = r.get('client') or {}
        self.client_avatar.person = c
        self.dom_nodes["client_name"].textContent = c.get("name") or ''
        self.dom_nodes["client_company"].textContent = c.get("company") or ''
        email = self.dom_nodes["client_email"]
        email.textContent = c.get("email") or ''
        email.setAttribute("href", "mailto:" + (c.get("email") or ''))
        self.m_status.selected_value = r['status']
        rng = self.dom_nodes["m_progress"]
        rng.value = str(r["progress"])
        self.dom_nodes["m_pct"].textContent = "%d%%" % r["progress"]
        self.m_quote.text = '' if r.get('quote_amount') is None else str(int(r['quote_amount']))
        locked = bool(self.data.get('locked'))
        pending = self.data.get('pending_change')
        open_ = r['status'] not in ('delivered', 'declined')
        self.m_quote.enabled = not locked
        self.lock_part.visible = locked
        if locked:
            when = ui.fmt_date(self.data.get('approved_at')) if self.data.get('approved_at') else ''
            self.lock_label.text = (tp('A change order is waiting for the client. The approved quote stays locked until they decide.')
                                    if pending else
                                    tp('Locked: the client approved this quote on {date}. Price changes go through a change order.', date=when))
        self.co_button.visible = locked and open_ and not pending
        so = self.data.get('signoff') or {}
        self.so_button.visible = bool(self.data.get('needs_signoff')) and r['status'] in ('in_progress', 'review') and not so.get('accepted')
        self.so_button.text = tp('Edit sign-off') if so else tp('Sign off delivery')
        self.m_eta.text = ui.date_iso(r.get('eta')) if r.get('eta') else ''
        self.m_note.text = r.get("quote_note") or ''
        self.m_prio.selected_value = r.get("priority") or 'normal'

    def _details(self, r):
        kv = self._quote_rows(r) + [
              (tp('ETA'), ui.fmt_date(r.get('eta'), True) if r.get('eta') else '—'),
              (tp('Requested by'), ui.fmt_date(r.get('desired_date'), True) if r.get('desired_date') else tp('Flexible')),
              (tp('Priority'), ui.PRIORITY.get(r.get('priority'), tp('Normal'))),
              (tp('Type'), ui.KIND.get(r.get('kind'), r.get('kind_label'))),
              (tp('Budget'), tp(r.get('budget')) if r.get('budget') else '—'),
              (tp('Submitted'), ui.fmt_date(r.get('created'), True))]
        return [{"k": k, "v": v or '', "first": i == 0} for i, (k, v) in enumerate(kv)]

    def _quote_rows(self, r):
        """Fixed quote; once approved: the approved amount (locked), every change order with its result, the total."""
        if r.get('quote_amount') is None:
            return [(tp('Fixed quote'), tp('Pending'))]
        if not self.data.get('locked'):
            return [(tp('Fixed quote'), ui.money(r.get('quote_amount')))]
        orders = self.data.get('change_orders') or []
        approved = [c for c in orders if c['status'] == 'approved']
        original = approved[0]['amount_before'] if approved else r.get('quote_amount')
        when = ui.fmt_date(self.data.get('approved_at')) if self.data.get('approved_at') else ''
        rows = [(tp('Approved quote'), ui.money(original) + ((' · ' + when) if when else ''))]
        status_word = {'approved': tp('approved'), 'pending': tp('waiting for you') if not self.admin else tp('waiting for the client'),
                       'declined': tp('declined'), 'withdrawn': tp('withdrawn')}
        for i, c in enumerate(orders):
            price = int(round(c.get('delta') or 0)) != 0
            v = self._delta(c.get('delta')) if price else tp('ETA {date}', date=ui.fmt_date(c.get('eta_after')))
            rows.append((tp('Change order {n}', n=i + 1), v + ' · ' + status_word.get(c['status'], c['status'])))
        if approved:
            rows.append((tp('Total'), ui.money(r.get('quote_amount'))))
        return rows

    # ---------------------------------------------------------------- actions
    def range_input(self, event):
        self.dom_nodes["m_pct"].textContent = str(self.dom_nodes["m_progress"].value) + "%"

    @handle("act1", "click")
    def act1_click(self, **event_args):
        self._act(self.act1.tag)

    @handle("act2", "click")
    def act2_click(self, **event_args):
        self._act(self.act2.tag)

    def _act(self, key):
        if key == 'manage':
            ui.scroll_into_view(self.manage, 'start')
            state.focus(self.m_quote)
        elif key and key.startswith('status:'):
            self._quick_status(key.split(':', 1)[1])
        elif key == 'question':
            ui.scroll_into_view(self.note_box)
            self.note_box.focus()
        elif key == 'withdraw':
            if confirm(tp("Withdraw this request? You can always submit it again later."), title=tp('Withdraw request'),
                       buttons=[(tp('Cancel'), False), (tp('Withdraw'), True)]):
                self._client_action('withdraw')
        elif key == 'changes':
            from ...Dialogs.PromptText import PromptText
            text = alert(PromptText(title=tp('Request changes'),
                                    text=tp('What should be different? Reference the acceptance criteria where you can.'),
                                    placeholder=tp('e.g. The refund email should go to the guest, not the manager.'),
                                    ok=tp('Send to engineer')), buttons=[], role="aa-dialog")
            if text:
                self._client_action('request_changes', text)
        elif key == 'approve':
            self._client_action('approve_quote')
        elif key == 'accept':
            so = self.data.get('signoff')
            if so and so.get('criteria'):
                from ...Dialogs.AcceptDelivery import AcceptDelivery
                res = alert(AcceptDelivery(criteria=[c.get('text') or '' for c in so['criteria']]), buttons=[],
                            role="aa-dialog", large=True)
                if res and res['action'] == 'accept':
                    self._client_action('accept', '', res['criteria'], confirmed=True)
                elif res:
                    self._client_action('request_changes', res['comment'], res['criteria'])
            else:
                self._client_action('accept')
        elif key == 'signoff':
            self._open_signoff()
        elif key in ('co_approve', 'co_decline'):
            co = self.data.get('pending_change') or {}
            if key == 'co_approve':
                if confirm(tp("Approve this change order? The new total becomes {total}, and it's locked like the original quote.",
                              total=ui.money(co.get('amount_after'))), title=tp('Approve change'),
                           buttons=[(tp('Cancel'), False), (tp('Approve change'), True)]):
                    self._client_action('approve_change')
            elif confirm(tp("Keep the original scope? The approved price and ETA stay as they are, and your engineer is told."),
                         title=tp('Keep the original scope'), buttons=[(tp('Cancel'), False), (tp('Keep the original scope'), True)]):
                self._client_action('decline_change')
        elif key == 'co_cancel':
            if confirm(tp("Withdraw this change order? The client is told, and the approved price and ETA stay."),
                       title=tp('Withdraw change order'), buttons=[(tp('Cancel'), False), (tp('Withdraw'), True)]):
                res = ui.call('admin_cancel_change_order', self.request_id)
                if res is not ui.FAIL:
                    self._apply(res)
                    state.toast(tp("Change order withdrawn."), "ok")

    def _open_signoff(self):
        from ...Dialogs.SignOff import SignOff
        r = self.data['request']
        res = alert(SignOff(request_id=self.request_id, acceptance=r.get('acceptance') or '', record=self.data.get('signoff')),
                    buttons=[], role="aa-dialog", large=True)
        if res:
            self._apply(res)
            state.toast(tp("Signed off. You can mark it ready for review.") if res.get('signoff_ready')
                        else tp("Sign-off saved as a draft."), "ok")

    @handle("so_button", "click")
    def so_button_click(self, **event_args):
        self._open_signoff()

    @handle("co_button", "click")
    def co_button_click(self, **event_args):
        from ...Dialogs.ChangeOrder import ChangeOrder
        res = alert(ChangeOrder(request=self.data['request']), buttons=[], role="aa-dialog")
        if res:
            self._apply(res)
            state.toast(tp("Change order sent. The client approves or declines it."), "ok")

    def _client_action(self, action, comment='', criteria=None, confirmed=False):
        r = self.data['request']
        if action == 'approve_quote':
            if not confirm(tp("Approve the fixed quote of {amount}? Work starts right away, and you're invoiced only after you accept the delivery.",
                              amount=ui.money(r.get('quote_amount'))), title=tp('Approve quote'),
                           buttons=[(tp('Cancel'), False), (tp('Approve quote'), True)]):
                return
        if action == 'accept' and not confirmed:
            if not confirm(tp("Accept this delivery? This confirms it meets the agreed acceptance criteria."), title=tp('Accept delivery'),
                           buttons=[(tp('Cancel'), False), (tp('Accept delivery'), True)]):
                return
        res = ui.call('client_action', self.request_id, action, comment, criteria)
        if res is not ui.FAIL:
            self._apply(res)
            msgs = {'approve_quote': tp("Quote approved. The build starts now."), 'accept': tp("Accepted. Thank you!"),
                    'request_changes': tp("Changes requested. Your engineer is on it."), 'withdraw': tp("Request withdrawn."),
                    'approve_change': tp("Change approved. The new total is locked."),
                    'decline_change': tp("Kept the original scope. Your engineer is told.")}
            if action in msgs:
                state.toast(msgs[action], "ok")

    def _quick_status(self, status):
        res = ui.call('admin_update_request', self.request_id, {'status': status}, None)
        if res is not ui.FAIL:
            self._apply(res)
            state.toast(tp("Status: {status}", status=ui.STATUS[status][0]), "ok")

    @handle("post_button", "click")
    def post_button_click(self, **event_args):
        body = (self.note_box.text or '').strip()
        if not body:
            state.toast(tp("Write something first."), "error")
            return
        self.post_button.enabled = False
        if self.admin:
            kind = self.note_kind.selected_value or 'update'
            res = ui.call('admin_update_request', self.request_id, {}, {'body': body, 'kind': kind, 'internal': kind == 'internal'})
        else:
            res = ui.call('client_action', self.request_id, 'comment', body)
        self.post_button.enabled = True
        if res is not ui.FAIL:
            self.note_box.text = ''
            self._apply(res)
            state.toast(tp("Posted."), "ok")

    @handle("save_button", "click")
    def save_button_click(self, **event_args):
        quote = (self.m_quote.text or '').strip() if isinstance(self.m_quote.text, str) else self.m_quote.text
        changes = {
            'status': self.m_status.selected_value, 'progress': int(self.dom_nodes["m_progress"].value or 0),
            'quote_amount': float(quote) if quote not in (None, '') else None,
            'quote_note': (self.m_note.text or '').strip(), 'eta': ui.parse_date(self.m_eta.text),
            'priority': self.m_prio.selected_value,
        }
        self.save_button.enabled = False
        self.save_button.text = tp('Saving…')
        res = ui.call('admin_update_request', self.request_id, changes, None)
        self.save_button.enabled = True
        self.save_button.text = tp('Save &amp; notify client')
        if res is not ui.FAIL:
            self._apply(res)
            state.toast(tp("Saved."), "ok")

    @handle("delete_button", "click")
    def delete_button_click(self, **event_args):
        r = self.data['request']
        if not confirm(tp("Delete {ref} and its whole history? This can't be undone.", ref=r['ref']), title=tp('Delete request'),
                       buttons=[(tp('Cancel'), False), (tp('Delete'), True)]):
            return
        if ui.call('admin_delete_request', self.request_id) is not ui.FAIL:
            state.toast(tp("Request deleted."), "ok")
            router.go('admin')
