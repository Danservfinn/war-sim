"""Entity store. Iteration is always sorted by id."""

from __future__ import annotations


class World:
    def __init__(self, seed: int):
        self.seed = seed
        self.tick = 0
        self.entities: dict[str, dict] = {}
        self.tracks: list[dict] = []
        self.orders: list[dict] = []
        self.min_bubble_m = 10_000
        self.max_bubble_m = 80_000

    def add(self, entity: dict) -> None:
        eid = entity["Identity"]["id"]
        if eid in self.entities:
            raise ValueError(f"duplicate entity {eid}")
        self.entities[eid] = entity

    def ids(self) -> list[str]:
        return sorted(self.entities)

    def get(self, eid: str) -> dict:
        return self.entities[eid]
