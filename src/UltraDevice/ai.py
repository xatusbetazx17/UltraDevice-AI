class PolicyLearner:
    def __init__(self):
        self.history = []  # store recent (load_w, harvest_w)

    def update(self, load_w: float, harvest_w: float):
        self.history.append((load_w, harvest_w))
        self.history = self.history[-100:]

    def suggest_mode(self):
        # naive: if harvest dominates, allow higher features; else conserve
        if not self.history:
            return "normal"
        avg_load = sum(l for l, _ in self.history) / len(self.history)
        avg_h = sum(h for _, h in self.history) / len(self.history)
        return "performance" if avg_h > 0.5 * avg_load else "conserve"
