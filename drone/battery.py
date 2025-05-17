# drone/battery.py

class Battery:
    def __init__(self, level: float = 100.0, drain_rate: float = 1.0):
        """
        level: initial battery percentage 0–100
        drain_rate: percent drained per tick
        """
        self.level = level
        self.drain_rate = drain_rate

    def drain(self) -> float:
        """Drain once. Returns new level."""
        self.level = max(0.0, self.level - self.drain_rate)
        return self.level

    def recharge(self, amount: float) -> float:
        """Recharge by amount. Returns new level."""
        self.level = min(100.0, self.level + amount)
        return self.level

    def is_low(self, threshold: float) -> bool:
        return self.level <= threshold
