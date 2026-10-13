"""Spike load: the same user behaviour as steady.py, driven by a repeating spike shape."""

from locust import LoadTestShape

from steady import ApiUser  # noqa: F401  (Locust runs every user class it finds in this module)


class SpikeShape(LoadTestShape):
    """Repeats every 5 minutes: 2 minutes at 50 users, 1 minute at 200, 2 minutes at 10."""

    # (stage ends at this second of the cycle, users, spawn rate)
    stages = [(120, 50, 10), (180, 200, 50), (300, 10, 50)]

    def tick(self):
        cycle_time = self.get_run_time() % self.stages[-1][0]
        for ends_at, users, spawn_rate in self.stages:
            if cycle_time < ends_at:
                return users, spawn_rate
