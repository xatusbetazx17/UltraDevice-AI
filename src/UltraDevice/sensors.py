class Sensors:
    def __init__(self):
        self.stealth = False

    def set_stealth(self, on: bool):
        self.stealth = on

    def power_draw_w(self) -> float:
        return 0.5 if self.stealth else 1.0  # placeholder
