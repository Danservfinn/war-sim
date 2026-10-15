"""Authoritative clock. One tick is one day. Compression is days per wall step."""

from __future__ import annotations

from sim.constants import MONTH_DAYS, YEAR_DAYS


class SimClock:
    def __init__(self, start_tick: int = 0, start_day: int | None = None):
        self.day = start_tick if start_day is None else start_day
        self.paused = False
        self.compression = 1

    @property
    def tick(self) -> int:
        return self.day

    @property
    def year(self) -> int:
        return self.day // YEAR_DAYS

    @property
    def month(self) -> int:
        return (self.day // MONTH_DAYS) % 12

    def pause(self) -> None:
        self.paused = True

    def resume(self) -> None:
        self.paused = False

    def set_compression(self, n: int) -> None:
        if n < 1:
            raise ValueError("compression must be >= 1")
        self.compression = n

    def step(self, n: int = 1) -> int:
        self.day += n
        return self.day

    def quanta_due(self) -> int:
        if self.paused:
            return 0
        return self.compression
