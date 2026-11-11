from anvil import *
from anvil.js import window

from ._anvil_designer import ApCardTemplate
from ... import apps_data, apps_fmt


def live_dot(node, p):
    lv = p.get('live')
    if not p.get('url'):
        title = "No live address yet"
    elif not lv:
        title = "Live site not checked yet"
    elif lv.get('ok'):
        node.classList.add("ok")
        title = "Live: answers (%s)" % lv.get('status')
    else:
        node.classList.add("bad")
        title = "Not answering: %s" % (lv.get('error') or lv.get('status'))
    node.setAttribute("title", title)
    node.setAttribute("aria-label", title)


class ApCard(ApCardTemplate):
    """An app on the board: screenshot, live dot, last push, description, step strip, next step, links, tags.
    The name is a link to #app/<key> that covers the card. item = an app (apps_core.view)."""

    def __init__(self, **properties):
        super().__init__(**properties)
        p = self.item
        card = self.dom_nodes["card"]
        card.style.setProperty("--c", apps_data.color(p['stage']))
        hero = self.dom_nodes["hero"]
        url = apps_data.media_url(p.get('hero'))
        if url:
            hero.setAttribute("src", url)
            hero.setAttribute("alt", p['name'] + " home page")
        else:
            hero.remove()
        live_dot(self.dom_nodes["dot"], p)
        name = self.dom_nodes["name"]
        name.textContent = p['name']
        name.setAttribute("href", "#app/" + window.encodeURIComponent(p['key']))
        self.dom_nodes["age"].textContent = apps_fmt.ago(p.get('pushed_at'))
        self.dom_nodes["age"].setAttribute("title", "Last push to GitHub")
        self.dom_nodes["desc"].textContent = p.get('desc') or ''
        nx = self.dom_nodes["next"]
        nx.textContent = ("Next: " + p['next'] if p.get('next') else "All steps done") + " · %d/%d" % (p['done'], p['total'])
        ref = self.dom_nodes["ref"]
        ref.setAttribute("title", "Refresh %s: choose what to check" % p['name'])
        ref.setAttribute("aria-label", "Refresh " + p['name'])
        if apps_data.pending(p['key']):
            ref.classList.add("spin")
            card.classList.add("busy")
        js = apps_data.js()
        if js:
            js.segs(self.dom_nodes["segs"], apps_data.segs(p))
            js.links(self.dom_nodes["links"], apps_data.links(p))
            js.chips(self.dom_nodes["chips"], p.get('tags') or [])

    def ref_click(self, event):
        event.stopPropagation()
        event.preventDefault()
        from ...Dialogs.ApRefresh import ApRefresh
        acts = alert(ApRefresh(key=self.item['key']), buttons=[], large=False, role="aa-dialog", dismissible=True)
        if acts:
            apps_data.queue('refresh', self.item['key'], {'actions': acts})
