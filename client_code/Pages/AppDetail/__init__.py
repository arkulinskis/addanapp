from anvil import *
from anvil.js import window

from ._anvil_designer import AppDetailTemplate
from ... import apps_data, apps_fmt, router, state, ui
from ...Components.ApPosts import counts, has_promo

SOURCE = {'github': ' · on GitHub, not in apps.json', 'board': ' · added on the board'}


class AppDetail(AppDetailTemplate):
    """#app/<key>: one app of the portfolio in full (the old App Board's side drawer): screenshots, live check,
    branches to merge, the checklist, Changes for Claude (requests), an idea for Prepsto, notes, links (the PC writes
    them into apps.json), commits, and summaries of its video, posts, biz dev plan, money plan and findings."""

    def __init__(self, key, **properties):
        super().__init__(**properties)
        self.key = key
        self.f: dict = {}
        state.heading(self.name, 1)
        self.idea_kind.items = [("Idea", "idea"), ("Bug", "bug"), ("Question", "question")]
        for c, label in ((self.change_box, "Change for Claude"), (self.idea_box_text, "Idea for Prepsto"), (self.idea_kind, "Kind of ticket"),
                         (self.notes_box, "Notes"), (self.url_box, "Live address"), (self.editor_box, "Anvil editor link")):
            state.set_control_attr(c, "aria-label", label)
        apps_data.listen(self._changed)
        if apps_data.load() is None:
            return
        self._load_full()
        self.redraw()

    def _load_full(self):
        res = apps_data.call('apps_project', self.key)
        self.f = res if res is not ui.FAIL else {}

    def _changed(self, key=None):
        if key in (None, self.key):
            self.redraw()

    def redraw(self):
        p = apps_data.project(self.key)
        self.missing.visible = p is None
        self.page.visible = p is not None
        if p is None:
            return
        self.p = p
        self.name.text = p['name']
        st = self.dom_nodes["stage"]
        st.textContent = p['stage_name']
        st.style.setProperty("--c", apps_data.color(p['stage']))
        self.park_button.text = "Un-park" if p.get('parked') else "Park (put on hold)"
        self.dom_nodes["sub"].textContent = ("%d/%d steps done" % (p['done'], p['total'])) + \
            ((" · last push " + apps_fmt.ago(p['pushed_at'])) if p.get('pushed_at') else "") + SOURCE.get(p.get('source'), '')
        self.dom_nodes["desc"].textContent = p.get('desc') or ''
        desk, phone = self.dom_nodes["desk"], self.dom_nodes["phone"]
        hu, pu = apps_data.media_url(p.get('hero')), apps_data.media_url(p.get('hero_phone'))
        self.dom_nodes["heroes"].style.display = "grid" if hu else "none"
        if hu:
            desk.setAttribute("src", hu)
            desk.setAttribute("alt", p['name'] + " home page, desktop")
        phone.style.display = "block" if pu else "none"
        if pu:
            phone.setAttribute("src", pu)
            phone.setAttribute("alt", p['name'] + " home page, phone")
        live = apps_data.live_text(p)
        if p.get('domain_planned'):
            live += "  ·  Planned domain: %s (not serving this app yet)" % p['domain_planned']
        if p.get('moved'):
            live += "  ·  🚚 Moved from %s on %s" % (', '.join(p.get('old_urls') or []), p['moved'])
        self.dom_nodes["live"].textContent = live
        js = apps_data.js()
        if js:
            js.links(self.dom_nodes["links"], apps_data.links(p))
            js.chips(self.dom_nodes["chips"], p.get('tags') or [])
        self._jobs()
        # banners
        self.guess_box.visible = bool(p.get('guess_url'))
        if p.get('guess_url'):
            self.dom_nodes["guess_text"].textContent = "%s answers%s. If it's yours, use it as the app's live link." % (
                p['guess_url'], (" (page title: “%s”)" % p['guess_title']) if p.get('guess_title') else "")
        self.followup_box.visible = bool(p.get('url_followup'))
        bs, old = p.get('branches') or [], p.get('branches_merged') or []
        self.branch_box.visible = bool(bs or old)
        base = (bs[0].get('base') if bs else None) or p.get('branch') or 'master'
        self.branch_head.text = "⑂ Branches to merge into " + base + ("" if bs else ": nothing waiting ✅")
        items = []
        for b in bs:
            txt = "%s · %s not on %s" % (b.get('name'), apps_fmt.plural(b.get('ahead', 0), 'commit'), b.get('base'))
            if b.get('last_date'):
                txt += " · last " + apps_fmt.ago(b['last_date'])
            if b.get('last_msg'):
                txt += " · “%s”" % b['last_msg']
            if b.get('behind'):
                txt += " · %s has %d newer commits (GitHub may ask you to resolve conflicts)" % (b.get('base'), b['behind'])
            items.append({"text": txt + (" → open pull request #%s" % b['pr']['number'] if b.get('pr') else " → review & merge on GitHub"),
                          "href": b['pr']['url'] if b.get('pr') else b.get('compare_url')})
        self.branches.items = items
        hint = ""
        if bs:
            hint = "On GitHub: %sMerge pull request. The live app follows %s." % ("Create pull request, then " if any(not b.get('pr') for b in bs) else "", base)
            if p.get('layout') == 'source':
                hint += " This app is deployed from its folder on the PC, so after merging tell Claude Code “bring the %s merge into %s” before its next deploy." % (bs[0].get('name'), p['name'])
        if old:
            hint += (" " if hint else "") + "Already in %s (safe to delete on GitHub): %s" % (base, ', '.join(old))
        self.branch_hint.text = hint
        # checklist
        from ...Components.ApSteps import ApSteps
        self.steps_holder.clear()
        self.steps_holder.add_component(ApSteps(project=p))
        # changes for Claude
        cmd = "/app-board run " + p['key']
        self.dom_nodes["run_cmd"].textContent = cmd
        self.copy_run.text = "Copy “%s”" % cmd
        self.changes.items = [{"text": "%s · %s · %s" % (c['ref'], c['status_label'], c['title']), "href": "#r/" + c['id']} for c in p.get('changes') or []]
        self.fix_legal.visible = bool(p.get('legal') and not p['legal'].get('ok'))
        self.fix_seo.visible = bool((p.get('seo') or {}).get('missing'))
        done = self.f.get('changes_done') or ''
        self.done_box.visible = bool(done)
        self.dom_nodes["done"].textContent = done
        # idea for Prepsto
        self.idea_box.visible = bool(p.get('prepsto'))
        ideas = self.f.get('ideas')
        if ideas:
            tk = ideas.get('tickets') or []
            self.dom_nodes["tickets_head"].textContent = (("Open on Prepsto (%d), checked %s:" % (ideas.get('total', len(tk)), apps_fmt.ago(ideas.get('checked'))))
                                                          if tk else ("Couldn't load its tickets: " + ideas['error']) if ideas.get('error') else "No open tickets on its Prepsto link.")
            self.tickets.items = [{"text": "%s · %s · %s" % (t.get('kind', ''), (t.get('message') or '')[:160], t.get('status', '')), "href": t.get('url')} for t in tk]
        else:
            self.dom_nodes["tickets_head"].textContent = "Prepsto link %s." % p.get('prepsto', '')
            self.tickets.items = []
        # notes + links (don't overwrite what's being typed)
        active = window.document.activeElement
        if not self._is_focused(self.notes_box, active):
            self.notes_box.text = p.get('notes') or ''
        if not self._is_focused(self.url_box, active):
            self.url_box.text = p.get('url') or ''
        if not self._is_focused(self.editor_box, active):
            self.editor_box.text = p.get('anvil_editor') or ''
        self.dom_nodes["commits_h"].textContent = "Recent commits" + ((" on " + p['branch']) if p.get('branch') else "")
        self.commits.items = (self.f.get('commits') or [])[:6]
        self.dom_nodes["folder"].textContent = ("Folder: Documents\\CLAUDE\\" + p['folder'].replace('/', '\\')) if p.get('folder') else ""
        # summaries
        v, y = p.get('video'), p.get('youtube') or {}
        self.video_box.visible = bool(v)
        if v:
            pub = (p.get('posted') or {}).get('yt-video')
            self.dom_nodes["video_line"].textContent = "%s · %s%s" % (v.get('length') or '', ("published " + pub) if pub else "ready to upload",
                                                                     " · " + v['title'] if v.get('title') else "")
        enc = window.encodeURIComponent(p['key'])
        self.dom_nodes["video_kit"].setAttribute("href", "#apps/posts/" + enc)
        self.posts_box.visible = has_promo(p)
        li, li_t, yt, yt_t = counts(p)
        self.dom_nodes["posts_line"].textContent = "LinkedIn %d/%d posted · YouTube %d/%d published" % (li, li_t, yt, yt_t)
        self.dom_nodes["posts_link"].setAttribute("href", "#apps/posts/" + enc)
        b = p.get('bizdev')
        self.biz_box.visible = bool(b)
        if b:
            self.dom_nodes["biz_line"].textContent = "%s · rank #%s%s · 30-day keep bar: %s · 15-minute first step: %s" % (
                b.get('wave_name', ''), b.get('rank'), (" · score %s/15" % b['score']) if b.get('score') is not None else "", b.get('keep', ''), b.get('first', ''))
            self.dom_nodes["biz_plan"].setAttribute("href", "#apps/bizdev/apps." + b.get('key', apps_data.biz_key(p['key'])))
        from ...Components.ApMoneyBody import ApMoneyBody
        from ...Components.ApFindings import ApFindings
        self.money_box.visible = bool(p.get('money'))
        self.money_holder.clear()
        if p.get('money'):
            self.money_holder.add_component(ApMoneyBody(money=p['money']))
        self.findings_holder.clear()
        self.findings_holder.add_component(ApFindings(project=p))

    def _is_focused(self, component, active):
        try:
            return active is not None and active == state.control(component)
        except Exception:
            return False

    # ---------------------------------------------------------------- jobs for this app
    def _jobs(self):
        b = apps_data.board() or {}
        w = b.get('worker') or {}
        mine = apps_data.pending(self.key)
        self.jobs_line.visible = bool(mine) or not w.get('online')
        self.jobs_dot.classes["on"] = bool(w.get('online'))
        if mine:
            self.jobs_text.text = ("Your PC is on it: " if w.get('online') else "Waiting for your PC: ") + ', '.join(apps_data.WHAT.get(j['kind'], j['kind']) for j in mine)
        else:
            self.jobs_text.text = "Your PC link is off, so refreshes and links wait until it's on."
        self.poll_timer.interval = 4 if mine else 0

    @handle("poll_timer", "tick")
    def poll_timer_tick(self, **event_args):
        if router.current().split('/')[0] != 'app':
            self.poll_timer.interval = 0
            return
        ids = [j['id'] for j in apps_data.pending(self.key)]
        if not ids:
            self.poll_timer.interval = 0
            return
        res = apps_data.call('apps_jobs', ids)
        if res is ui.FAIL:
            return
        b = apps_data.board()
        b['worker'] = res['worker']
        left = [j for j in res['jobs'] if j['status'] in ('queued', 'running')]
        done = [j for j in res['jobs'] if j['status'] not in ('queued', 'running')]
        b['jobs'] = [j for j in b.get('jobs') or [] if j['id'] not in [x['id'] for x in done]]
        for j in done:
            if j['status'] == 'failed':
                state.toast(apps_data.WHAT.get(j['kind'], 'Job') + " failed: " + (j.get('error') or 'no details'), "error")
            else:
                state.toast(apps_data.WHAT.get(j['kind'], 'Job') + ": done", "ok")
        if done:
            apps_data.load(force=True)
            self._load_full()
            self.redraw()
        elif not left:
            self.poll_timer.interval = 0

    # ---------------------------------------------------------------- actions
    @handle("refresh_button", "click")
    def refresh_button_click(self, **event_args):
        from ...Dialogs.ApRefresh import ApRefresh
        acts = alert(ApRefresh(key=self.key), buttons=[], large=False, role="aa-dialog", dismissible=True)
        if acts:
            apps_data.queue('refresh', self.key, {'actions': acts})

    @handle("park_button", "click")
    def park_button_click(self, **event_args):
        apps_data.set_state(self.key, {'parked': not self.p.get('parked')})

    @handle("change_button", "click")
    def change_button_click(self, **event_args):
        text = (self.change_box.text or '').strip()
        if apps_data.add_change(self.key, text) is not ui.FAIL:
            self.change_box.text = ''

    def _add_fix(self, line):
        cur = (self.change_box.text or '').strip()
        if line in cur:
            return state.toast("Already in the box", "ok")
        self.change_box.text = (cur + "\n\n" if cur else "") + line

    @handle("fix_legal", "click")
    def fix_legal_click(self, **event_args):
        self._add_fix("Legal: bring the Privacy & Terms page into good standing. The App Board says: " + ' '.join(self.p['legal'].get('problems') or []))

    @handle("fix_seo", "click")
    def fix_seo_click(self, **event_args):
        self._add_fix("SEO: add what the App Board finds missing on the live site: " + ', '.join(self.p['seo']['missing']) + ". Then re-check with board_cli.py check.")

    @handle("copy_run", "click")
    def copy_run_click(self, **event_args):
        apps_data.copy("/app-board run " + self.key, "Copied: paste it into Claude Code")

    @handle("followup_copy", "click")
    def followup_copy_click(self, **event_args):
        apps_data.copy("/app-board finish " + self.key, "Copied: paste it into Claude Code")

    @handle("guess_button", "click")
    def guess_button_click(self, **event_args):
        apps_data.queue('link', self.key, {'field': 'url', 'value': self.p['guess_url']})

    @handle("idea_button", "click")
    def idea_button_click(self, **event_args):
        text = (self.idea_box_text.text or '').strip()
        if apps_data.queue('idea', self.key, {'text': text, 'kind': self.idea_kind.selected_value or 'idea'}):
            self.idea_box_text.text = ''

    @handle("tickets_button", "click")
    def tickets_button_click(self, **event_args):
        apps_data.queue('ideas', self.key)

    @handle("notes_box", "lost_focus")
    def notes_box_lost_focus(self, **event_args):
        text = self.notes_box.text or ''
        if text != (self.p.get('notes') or ''):
            if apps_data.set_state(self.key, {'notes': text}, quiet=True) is not ui.FAIL:
                state.toast("Notes saved", "ok")

    @handle("links_button", "click")
    def links_button_click(self, **event_args):
        url, ed = (self.url_box.text or '').strip(), (self.editor_box.text or '').strip()
        p = self.p
        if url != (p.get('url') or ''):
            host = lambda u: (u.split('://', 1)[-1].split('/', 1)[0])
            if p.get('url') and url and not host(p['url']).endswith('.anvil.app') and host(url).endswith('.anvil.app'):
                if not confirm("%s is live on its own domain, %s. Switch its live address back to the Anvil address %s?" % (p['name'], p['url'], url)):
                    self.url_box.text = p['url']
                    return
            apps_data.queue('link', self.key, {'field': 'url', 'value': url})
        if ed != (p.get('anvil_editor') or ''):
            apps_data.queue('link', self.key, {'field': 'anvil_editor', 'value': ed})
        if url == (p.get('url') or '') and ed == (p.get('anvil_editor') or ''):
            state.toast("Nothing changed", "ok")
