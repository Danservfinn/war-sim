"""Scaffold checks: bubble freeze, movement resolution, snapshot filter, loader."""

from pathlib import Path

from sim.loader import load_scenario
from sim.spatial.index import contact_bubbles, movement_resolution
from sim.snapshot.builder import build_snapshot
from sim.systems.schedule import schedule
from sim.constants import TICK_ORDER

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "scenarios" / "sample_asymmetric"


def test_loader_and_bubbles():
    world, meta = load_scenario(SCENARIO)
    assert meta["viewer_side"] == "side_a"
    assert world.ids() == ["a-radar", "b-bomber", "b-far"]
    bubbles = contact_bubbles(world)
    assert bubbles == contact_bubbles(world)
    assert bubbles == ["a-radar", "b-bomber"]
    assert "b-far" not in bubbles


def test_movement_resolution():
    assert movement_resolution(True) == {"cadence_days": 1, "grid_mm": None, "position": "mm"}
    assert movement_resolution(False)["cadence_days"] == 1
    assert movement_resolution(False)["grid_mm"] == 10_000_000


def test_snapshot_hides_undetected():
    world, meta = load_scenario(SCENARIO)
    rows = build_snapshot(world, meta["viewer_side"], contact_bubbles(world))
    ids = [r["id"] for r in rows]
    assert "a-radar" in ids
    assert "b-bomber" in ids
    assert "b-far" not in ids
    bomber = next(r for r in rows if r["id"] == "b-bomber")
    assert bomber["contact_quality"] == "detected"
    assert bomber["draw_mode"] == "platform"
    own = next(r for r in rows if r["id"] == "a-radar")
    assert own["contact_quality"] == "friendly"


def test_schedule_order_has_no_era_field():
    names = [s.name for s in schedule()]
    assert names == list(TICK_ORDER)
    for system in schedule():
        blob = " ".join(system.reads + system.writes)
        assert "year" not in blob
        assert "era" not in blob
