from anvil import *
from anvil.js import window

from ._anvil_designer import ApVideoKitTemplate
from ... import apps_data


class ApVideoKit(ApVideoKitTemplate):
    """An app's pitch video and its YouTube upload kit: plays from YouTube when it's up (click to load), titles,
    description, tags, pinned comment (each with Copy) and the Published tick (= posted['yt-video']).
    project = the app; kit = its video_kit (the long texts; the board itself only carries a summary)."""

    def __init__(self, project=None, kit=None, **properties):
        super().__init__(**properties)
        p = project or {}
        self.p = p
        v = dict(p.get('video') or {})
        v.update(kit or {})
        self.v = v
        y = p.get('youtube') or {}
        on = (p.get('posted') or {}).get('yt-video')
        if on:
            self.dom_nodes["art"].classList.add("posted")
        self.dom_nodes["pub"].checked = bool(on)
        self.dom_nodes["pub_lbl"].textContent = "Published" + (" " + on if isinstance(on, str) and on != 'yes' else "")
        meta = [x for x in [v.get('length'), '1080p', ('%s MB' % v['mb']) if v.get('mb') else '', ('music: ' + v['music']) if v.get('music') else '',
                            ('made ' + v['made']) if v.get('made') else ''] if x]
        self.dom_nodes["meta"].textContent = ' · '.join(meta)
        js = apps_data.js()
        if js:
            js.links(self.dom_nodes["yt"], [{"label": "Watch on YouTube ↗" if y.get('public') else "YouTube (not public) ↗", "href": y['url']}] if y.get('url') else [])
        thumb = apps_data.media_url(p.get('thumb'))
        img = self.dom_nodes["thumb"]
        if thumb:
            img.setAttribute("src", thumb)
            img.setAttribute("alt", "%s YouTube thumbnail" % p.get('name', ''))
        else:
            img.remove()
        play = self.dom_nodes["play"]
        if y.get('id'):
            play.setAttribute("aria-label", "Play the %s pitch video (loads YouTube)" % p.get('name', ''))
        else:
            play.setAttribute("disabled", "")
            self.dom_nodes["go"].textContent = "Not on YouTube yet"
        self.dom_nodes["where"].textContent = ("The video file is on your PC: " + v['file']) if v.get('file') and not y.get('public') else ""
        titles = v.get('titles') or ([v['title']] if v.get('title') else [])
        self.titles_row.visible = bool(titles)
        self.titles.items = [{"i": i, "text": t} for i, t in enumerate(titles)]
        self.desc_row.visible = bool(v.get('description'))
        self.dom_nodes["desc"].textContent = v.get('description') or ''
        tags = v.get('tags') or ''
        if isinstance(tags, list):
            tags = ', '.join(tags)
        self.tags_text = tags
        self.tags_row.visible = bool(tags)
        self.dom_nodes["tags_k"].textContent = "Tags · %d/500 characters" % len(tags)
        self.dom_nodes["tags"].textContent = tags
        self.pin_row.visible = bool(v.get('pinned_comment'))
        self.dom_nodes["pin"].textContent = v.get('pinned_comment') or ''
        foot = ("Category: %s · " % v['category'] if v.get('category') else '') + "Not made for kids · Altered or synthetic content: No"
        if v.get('notes'):
            foot += " · ⚠️ " + v['notes']
        self.dom_nodes["foot"].textContent = foot

    def play_click(self, event):
        y = self.p.get('youtube') or {}
        if not y.get('id'):
            return
        f = window.document.createElement("iframe")
        f.setAttribute("src", "https://www.youtube-nocookie.com/embed/%s?autoplay=1&rel=0" % y['id'])
        f.setAttribute("title", "%s pitch video" % self.p.get('name', ''))
        f.setAttribute("allow", "autoplay; encrypted-media; picture-in-picture; fullscreen")
        f.setAttribute("allowfullscreen", "")
        box = self.dom_nodes["player"]
        while box.firstChild:
            box.removeChild(box.firstChild)
        box.appendChild(f)

    def pub_change(self, event):
        apps_data.set_posted(self.p['key'], 'yt-video', bool(self.dom_nodes["pub"].checked))

    @handle("desc_button", "click")
    def desc_button_click(self, **event_args):
        apps_data.copy(self.v.get('description'), "Description copied")

    @handle("tags_button", "click")
    def tags_button_click(self, **event_args):
        apps_data.copy(self.tags_text, "Tags copied")

    @handle("pin_button", "click")
    def pin_button_click(self, **event_args):
        apps_data.copy(self.v.get('pinned_comment'), "Comment copied")
