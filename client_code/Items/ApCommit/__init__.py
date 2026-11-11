from anvil import *

from ._anvil_designer import ApCommitTemplate
from ... import apps_fmt


class ApCommit(ApCommitTemplate):
    """A recent commit on GitHub. item = {date, msg, url}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        self.dom_nodes["when"].textContent = apps_fmt.ago(it.get('date'))
        a = self.dom_nodes["msg"]
        a.textContent = it.get('msg') or ''
        if it.get('url'):
            a.setAttribute("href", it['url'])
