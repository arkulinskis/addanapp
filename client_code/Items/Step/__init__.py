from anvil import *

from ._anvil_designer import StepTemplate


class Step(StepTemplate):
    """One stage of a request's stepper. item = {label, state: "done" | "cur" | ""}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.dom_nodes["label"].textContent = self.item["label"]
        if self.item.get("state"):
            self.dom_nodes["s"].classList.add(self.item["state"])
