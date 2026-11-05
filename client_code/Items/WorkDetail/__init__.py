from anvil import *

from ._anvil_designer import WorkDetailTemplate
from ... import i18n
from ...Components.Shot import BY_KEY
from ..ShowcaseCard import fill_project


class WorkDetail(WorkDetailTemplate):
    """The opened part of a Work index row: preview, the rest of the blurb, what we built, tags, film and link."""

    def __init__(self, project_key, **properties):
        super().__init__(**properties)
        p = BY_KEY[project_key]
        self.shot.project_key = p['key']
        fill_project(self, p)
        i18n.apply(self)
