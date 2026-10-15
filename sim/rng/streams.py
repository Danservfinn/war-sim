"""Named RNG streams. Seed is scenario + tick + stream name. No wall clock."""

from __future__ import annotations

import hashlib


def stream_seed(scenario_seed: int, tick: int, name: str) -> int:
    digest = hashlib.sha256(f"{scenario_seed}:{tick}:{name}".encode()).digest()
    return int.from_bytes(digest[:8], "big")


class Stream:
    def __init__(self, scenario_seed: int, tick: int, name: str):
        self.name = name
        self.state = stream_seed(scenario_seed, tick, name)
        self.rolls: list[int] = []

    def roll(self, sides: int = 1000) -> int:
        # xorshift64, logged so replay can hash the same sequence.
        x = self.state & 0xFFFFFFFFFFFFFFFF
        x ^= (x << 13) & 0xFFFFFFFFFFFFFFFF
        x ^= x >> 7
        x ^= (x << 17) & 0xFFFFFFFFFFFFFFFF
        self.state = x
        value = x % sides
        self.rolls.append(value)
        return value
