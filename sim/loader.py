"""Load a scenario folder into a World. No era rules. Files only."""

from __future__ import annotations

from pathlib import Path

import yaml

from sim.ecs.store import World


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text())
    return data or {}


def load_scenario(root: Path) -> tuple[World, dict]:
    root = Path(root)
    meta = _load(root / "scenario.yaml")
    world = World(seed=int(meta["seed"]))
    world.tick = int(meta.get("start_tick", 0))
    bubbles = meta.get("bubbles") or {}
    world.min_bubble_m = int(bubbles.get("min_bubble_m", world.min_bubble_m))
    world.max_bubble_m = int(bubbles.get("max_bubble_m", world.max_bubble_m))

    for path in sorted((root / "oob").glob("*.yaml")):
        for entity in _load(path).get("entities") or []:
            world.add(entity)
    tracks = _load(root / "tracks.yaml")
    world.tracks = list(tracks.get("tracks") or [])
    return world, meta
