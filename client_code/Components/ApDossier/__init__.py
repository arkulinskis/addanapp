from anvil import *
import anvil.js
from anvil.js import window

from ._anvil_designer import ApDossierTemplate
from ... import apps_data, apps_fmt, router, state, ui
from ...Items.ApCard import live_dot
from ..ApPosts import full, has_promo, counts

ORDERS = [("Biz dev rank", "rank"), ("Stage", "stage"), ("Recently pushed", "recent"), ("Name A–Z", "name")]
WAVE_C = {'1': 'var(--ap-ok)', '2': 'var(--accent)', '3': 'var(--muted)', 'H': 'var(--ap-bad)', 'Hub': 'var(--ap-merge)'}
WINS = ('yes', 'feedback', 'paid')


def facts(p, log_rows):
    n, tot = p['done'], p['total']
    lv, sc, br = p.get('live') or {}, p.get('schema') or {}, p.get('branches') or []
    li, li_t, yt, yt_t = counts(p)
    wins = len([r for r in log_rows if (r[5] if len(r) > 5 else '').strip().lower() in WINS])
    lg, seo, y, m, b = p.get('legal'), p.get('seo'), p.get('youtube') or {}, p.get('money'), p.get('bizdev')
    out = [
        {"k": "Checklist", "v": "%d/%d" % (n, tot), "cls": "ok" if n == tot else "", "title": ("Next step: " + p['next']) if p.get('next') else "All steps done"},
        {"k": "Next step", "v": p.get('next') or "All done 🎉", "cls": "warn" if p.get('next') else "ok"},
        {"k": "Live site", "v": "— no address" if not p.get('url') else ("not checked" if not p.get('live') else ("✅ answers" if lv.get('ok') else "❌ down")),
         "cls": "" if not p.get('url') or not p.get('live') else ("ok" if lv.get('ok') else "bad"), "title": p.get('url') or "No live address yet"},
        {"k": "Last push", "v": apps_fmt.ago(p.get('pushed_at')) or "—", "title": p.get('pushed_at') or "Never pushed"},
        {"k": "Legal", "v": "—" if not lg else ("✅ good" if lg.get('ok') else "⚠️ %s" % apps_fmt.plural(len(lg.get('problems') or []), 'issue')),
         "cls": "" if not lg else ("ok" if lg.get('ok') else "bad"), "title": ' '.join((lg or {}).get('problems') or []) or "In good standing"},
        {"k": "SEO", "v": ("not checked" if p.get('url') else "—") if not seo else ("⚠️ %d missing" % len(seo['missing']) if seo.get('missing') else "✅ good"),
         "cls": "" if not seo else ("bad" if seo.get('missing') else "ok"), "title": ', '.join((seo or {}).get('missing') or []) or "In good standing"},
        {"k": "Database", "v": "—" if not sc else {'ok': "✅ matches", 'mismatch': "⚠️ mismatch", 'not_installed': "no check yet"}.get(sc.get('state'), "couldn't check"),
         "cls": {'ok': 'ok', 'mismatch': 'bad'}.get(sc.get('state'), '')},
        {"k": "Branches", "v": ("⑂ %d to merge" % len(br)) if br else "none waiting", "cls": "merge" if br else "ok",
         "title": ', '.join(x.get('name', '') for x in br) or "Nothing to merge"},
        {"k": "LinkedIn", "v": ("%d/%d posted" % (li, li_t)) if has_promo(p) else "—", "cls": "ok" if li else ""},
        {"k": "YouTube", "v": ("%d/%d published" % (yt, yt_t)) if has_promo(p) else "—", "cls": "ok" if yt else ""},
        {"k": "Pitch video", "v": "✅ on YouTube" if y.get('public') else ("on YouTube, not public" if y else ("🎬 %s ready" % (p.get('video') or {}).get('length', '') if p.get('video') else "—")),
         "cls": "ok" if (p.get('video') or y) else "", "title": y.get('url') or "No pitch video yet"},
        {"k": "Outreach", "v": "%d sent · %s" % (len(log_rows), apps_fmt.plural(wins, 'win')), "cls": "ok" if wins else ("warn" if log_rows else "")},
        {"k": "Biz score", "v": ("%s/15" % b['score']) if b and b.get('score') is not None else "—", "title": "want + reach + money, out of 15"},
        {"k": "Money role", "v": ("%s %s" % (m.get('role_icon', ''), m.get('role_label', ''))) if m else "—",
         "cls": "ok" if m and m.get('role') in ('focus', 'test', 'service') else "", "title": (m.get('role_meaning', '') + ' · ' + m.get('when_label', '')) if m else "No plan yet"},
    ]
    for f in out:
        f.setdefault("cls", "")
    return out


class ApDossier(ApDossierTemplate):
    """#apps/dossier[/<key>]: one app per page (big screenshot, every status, its biz dev plan and outreach, its money
    plan, its posts and video kit). Flip with the arrows, the arrow keys or the list; order by rank, stage, push, name."""

    def __init__(self, arg=None, **properties):
        super().__init__(**properties)
        self.key = arg or state.store_get('apps.dosKey', '')
        self.order_dd.items = ORDERS
        self.order_dd.selected_value = state.store_get('apps.dosOrder', 'rank')
        state.set_control_attr(self.order_dd, "id", "ap-dos-order")
        state.set_control_attr(self.pick_dd, "aria-label", "Jump to an app")
        state.set_attr(self.prev_button, "aria-label", "Previous app")
        state.set_attr(self.next_button, "aria-label", "Next app")
        self._keys = anvil.js.report_exceptions(self._on_key)
        self._plans: dict = {}
        self.redraw()

    @handle("", "show")
    def form_show(self, **event_args):
        window.addEventListener("keydown", self._keys)

    @handle("", "hide")
    def form_hide(self, **event_args):
        window.removeEventListener("keydown", self._keys)

    def _on_key(self, event):
        if event.altKey or event.ctrlKey or event.metaKey:
            return
        tag = str(getattr(window.document.activeElement, "tagName", "") or "")
        if tag in ("INPUT", "TEXTAREA", "SELECT"):
            return
        if event.key == "ArrowLeft":
            event.preventDefault()
            self._go(-1)
        elif event.key == "ArrowRight":
            event.preventDefault()
            self._go(1)

    def set_arg(self, arg):
        if arg and arg != self.key:
            self.key = arg
            self.redraw()
            window.scrollTo(0, 0)

    def _list(self):
        b = apps_data.board() or {}
        order = {ln['id']: i for i, ln in enumerate(b.get('lanes') or [])}
        how = self.order_dd.selected_value or 'rank'
        lst = sorted(apps_data.visible(), key=lambda p: p['name'].lower())
        if how == 'rank':
            return sorted(lst, key=lambda p: (p.get('bizdev') or {}).get('rank') or 999)
        if how == 'stage':
            return sorted(lst, key=lambda p: order.get(p['stage'], 99))
        if how == 'recent':
            return sorted(lst, key=lambda p: p.get('pushed_at') or '', reverse=True)
        return lst

    def _go(self, step):
        lst = self._list()
        if not lst:
            return
        i = next((j for j, p in enumerate(lst) if p['key'] == self.key), -1)
        i = 0 if i < 0 else (i + step) % len(lst)
        router.go("apps/dossier/" + window.encodeURIComponent(lst[i]['key']))

    def redraw(self, key=None):
        lst = self._list()
        self.none.visible = not lst
        self.page.visible = bool(lst)
        if not lst:
            return
        i = next((j for j, p in enumerate(lst) if p['key'] == self.key), -1)
        if i < 0:
            i = 0
            self.key = lst[0]['key']
        state.store_set('apps.dosKey', self.key)
        p = lst[i]
        prev, nxt = lst[(i - 1) % len(lst)], lst[(i + 1) % len(lst)]
        self.pick_dd.items = [("%d. %s" % (j + 1, x['name']), x['key']) for j, x in enumerate(lst)]
        self.pick_dd.selected_value = p['key']
        self.dom_nodes["pos"].textContent = "%d of %d" % (i + 1, len(lst))
        self.prev_button.tooltip = "Previous: " + prev['name']
        self.next_button.tooltip = "Next: " + nxt['name']
        self.prev2_button.text = "← " + prev['name']
        self.next2_button.text = nxt['name'] + " →"
        self.dom_nodes["open"].setAttribute("href", "#app/" + window.encodeURIComponent(p['key']))
        # top
        desk, phone, none = self.dom_nodes["desk"], self.dom_nodes["phone"], self.dom_nodes["noshot"]
        hu, pu = apps_data.media_url(p.get('hero')), apps_data.media_url(p.get('hero_phone'))
        desk.style.display = "block" if hu else "none"
        phone.style.display = "block" if pu else "none"
        none.style.display = "none" if hu else "block"
        if hu:
            desk.setAttribute("src", hu)
            desk.setAttribute("alt", p['name'] + " home page, desktop")
        if pu:
            phone.setAttribute("src", pu)
            phone.setAttribute("alt", p['name'] + " home page, phone")
        self.dom_nodes["name"].textContent = p['name']
        dot = self.dom_nodes["dot"]
        dot.className = "ap-dot"
        live_dot(dot, p)
        st = self.dom_nodes["stage"]
        st.textContent = p['stage_name']
        st.style.setProperty("--c", apps_data.color(p['stage']))
        b = p.get('bizdev') or {}
        wave = self.dom_nodes["wave"]
        wave.style.display = "inline-block" if b else "none"
        wave.textContent = b.get('wave_name') or ''
        wave.style.setProperty("--wc", WAVE_C.get(str(b.get('wave')), 'var(--muted)'))
        total = len([x for x in (apps_data.board() or {}).get('projects') or [] if x.get('bizdev')])
        self.dom_nodes["rank"].textContent = ("rank #%s of %d" % (b.get('rank'), total)) if b else ""
        self.dom_nodes["desc"].textContent = p.get('desc') or "No description yet."
        self.dom_nodes["live"].textContent = apps_data.live_text(p) + (("  Planned domain: " + p['domain_planned']) if p.get('domain_planned') else "")
        self.dom_nodes["quick"].textContent = ("🎯 30-day keep bar: %s  ·  15-minute first step: %s" % (b.get('keep', ''), b.get('first', ''))) if b else ""
        self.dom_nodes["quick"].style.display = "block" if b else "none"
        js = apps_data.js()
        if js:
            js.chips(self.dom_nodes["chips"], [t for t in p.get('tags') or [] if t.get('cls') in ('ai', 'bad', 'merge')])
            js.links(self.dom_nodes["links"], apps_data.links(p))
        # status
        from ..ApSteps import ApSteps
        from ..ApFindings import ApFindings
        self.steps_holder.clear()
        self.steps_holder.add_component(ApSteps(project=p))
        self.findings_holder.clear()
        self.findings_holder.add_component(ApFindings(project=p, recheck=False))
        self.changes_box.visible = bool(p.get('changes'))
        self.changes.items = [{"text": "%s · %s · %s" % (c['ref'], c['status_label'], c['title']), "href": "#r/" + c['id']} for c in p.get('changes') or []]
        self.notes_box.visible = bool(p.get('notes'))
        self.dom_nodes["notes"].textContent = p.get('notes') or ''
        self.dom_nodes["folder"].textContent = ("Folder: Documents\\CLAUDE\\" + p['folder'].replace('/', '\\')) if p.get('folder') else ""
        f = full(p['key']) or {}
        self.commits.items = (f.get('commits') or [])[:5]
        # biz dev + money + posts
        bk = apps_data.biz_key(p['key'])
        plan = self._plans.get(bk)
        if plan is None:
            plan = apps_data.call('apps_bizdev_plan', bk) if b else {"html": "", "rows": []}
            if plan is ui.FAIL:
                plan = {"html": "", "rows": []}
            self._plans[bk] = plan
        names = [x.lower() for x in (p['name'], b.get('name') or '') if x]
        rows = [r for r in plan.get('rows') or [] if len(r) > 1 and (r[1] or '').strip().lower() in names]
        self.facts.items = facts(p, rows)
        # the plan's markdown is rendered by the server from escaped text (apps_core.markdown)
        self.dom_nodes["plan"].innerHTML = str(plan.get('html') or '<p class="muted">No go-to-market plan for this app yet.</p>')
        if js:
            js.table(self.dom_nodes["log"], [{"key": k, "label": k} for k in ('Date', 'Channel', 'Who', 'Result', 'Next step')],
                     [[r[0], r[2], r[3], r[5], r[6]] for r in reversed([list(x) + [''] * (8 - len(x)) for x in rows])])
        from ..ApMoneyBody import ApMoneyBody
        self.money_holder.clear()
        if p.get('money'):
            self.money_holder.add_component(ApMoneyBody(money=p['money']))
        else:
            self.money_holder.add_component(Label(text="No monetization plan for this app yet.", role="t"))
        from ..ApVideoKit import ApVideoKit
        from ..ApPostList import ApPostList
        self.posts_holder.clear()
        if p.get('video'):
            self.posts_holder.add_component(ApVideoKit(project=p, kit=f.get('video_kit')))
        self.posts_holder.add_component(ApPostList(project=p, promo=f.get('promo'), closed=True))

    @handle("prev_button", "click")
    def prev_button_click(self, **event_args):
        self._go(-1)

    @handle("next_button", "click")
    def next_button_click(self, **event_args):
        self._go(1)

    @handle("prev2_button", "click")
    def prev2_button_click(self, **event_args):
        self._go(-1)

    @handle("next2_button", "click")
    def next2_button_click(self, **event_args):
        self._go(1)

    @handle("pick_dd", "change")
    def pick_dd_change(self, **event_args):
        router.go("apps/dossier/" + window.encodeURIComponent(self.pick_dd.selected_value))

    @handle("order_dd", "change")
    def order_dd_change(self, **event_args):
        state.store_set('apps.dosOrder', self.order_dd.selected_value)
        self.redraw()

    @handle("refresh_button", "click")
    def refresh_button_click(self, **event_args):
        from ...Dialogs.ApRefresh import ApRefresh
        acts = alert(ApRefresh(key=self.key), buttons=[], large=False, role="aa-dialog", dismissible=True)
        if acts:
            apps_data.queue('refresh', self.key, {'actions': acts})
