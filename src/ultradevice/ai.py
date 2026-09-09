"""Transparent local power predictor, not a trained general-purpose AI model."""
from collections import deque

from .validation import number


class PolicyLearner:
    def __init__(self):
        self.history = deque(maxlen=100)

    def update(self, load_w, harvest_w):
        number("load_w", load_w)
        number("harvest_w", harvest_w)
        self.history.append((load_w, harvest_w))

    def forecast(self, remaining_wh):
        number("remaining_wh", remaining_wh)
        if not self.history:
            return None
        net = sum(load - harvest for load, harvest in self.history) / len(self.history)
        return remaining_wh / net if net > 0 else None

    def suggest_mode(self):
        if not self.history:
            return "normal"
        load = sum(load for load, _ in self.history) / len(self.history)
        harvest = sum(h for _, h in self.history) / len(self.history)
        return "performance" if harvest > 0.5 * load else "conserve"
