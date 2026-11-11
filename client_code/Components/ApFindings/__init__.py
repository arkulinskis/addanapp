from anvil import *

from ._anvil_designer import ApFindingsTemplate
from ... import apps_data, apps_fmt


class ApFindings(ApFindingsTemplate):
    """An app's legal, SEO and database findings (from the PC's last check). show(project), recheck=False hides the
    database button (the dossier)."""

    def __init__(self, project=None, recheck=True, **properties):
        super().__init__(**properties)
        self.recheck = recheck
        self.p: dict = {}
        if project:
            self.show(project)

    def show(self, p):
        self.p = p
        b = apps_data.board() or {}
        lg = p.get('legal')
        self.legal_box.visible = bool(lg)
        if lg:
            self.legal_state.text = ("✅ in good standing" + (" (kit %s)" % lg['kit_version'] if lg.get('kit_version') else "")) if lg.get('ok') else "⚠️ needs work"
            self.legal_list.items = [{"text": x} for x in lg.get('problems') or []]
        seo = p.get('seo')
        self.seo_box.visible = bool(seo) or bool(p.get('url'))
        if seo:
            miss = seo.get('missing') or []
            self.seo_state.text = ("⚠️ %d missing" % len(miss)) if miss else "✅ in good standing"
            checks = seo.get('checks') or {}
            self.seo_list.items = [{"text": ("✓ " if checks.get(k) else "✗ ") + label} for k, label in b.get('seo_labels') or []]
        else:
            self.seo_state.text = "not checked yet"
            self.seo_list.items = []
        sc = p.get('schema')
        self.db_box.visible = bool(p.get('url'))
        self.schema_button.visible = self.recheck and bool(p.get('repo'))
        items = []
        hint = ""
        if not sc:
            self.db_state.text = "not checked yet"
        elif sc.get('state') == 'ok':
            self.db_state.text = "✅ matches the code (%s tables)" % sc.get('tables')
        elif sc.get('state') == 'not_installed':
            self.db_state.text = "can't check yet"
            hint = "The live app doesn't have the schema check yet. It arrives with the next deploy (and Publish, if the live version is pinned)."
        elif sc.get('state') == 'error':
            self.db_state.text = "couldn't check: " + (sc.get('error') or 'unknown error')
        else:
            self.db_state.text = "⚠️ doesn't match the code"
            for label, k in (("Tables missing in the database", 'missing_tables'), ("Columns missing in the database", 'missing_columns'),
                             ("Columns only in the database (accepting the code's schema deletes them and their data)", 'extra_columns')):
                if sc.get(k):
                    items.append({"text": label + ": " + ", ".join(sc[k])})
            hint = ("In the Anvil editor, click Resolve on the Schema Mismatch alert and choose " +
                    ("carefully: “The schema of the source code is correct” deletes the extra columns. If you added them in Anvil on purpose, ask Claude to add them to the code first."
                     if sc.get('extra_columns') else "“The schema of the source code is correct”.") + " Then re-check.")
        if sc and sc.get('checked'):
            hint = (hint + " " if hint else "") + "Checked " + apps_fmt.ago(sc['checked']) + "."
        self.db_list.items = items
        self.db_hint.text = hint

    @handle("schema_button", "click")
    def schema_button_click(self, **event_args):
        apps_data.queue('schema', self.p.get('key'))
