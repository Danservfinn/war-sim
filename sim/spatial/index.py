"""Spatial indexes and the frozen contact-bubble rule."""

from __future__ import annotations

from sim.constants import (
    BUBBLE_QUALITIES,
    DAY,
    FINE_CELL_MM,
    MAX_BUBBLE_M,
    MIN_BUBBLE_M,
    STRATEGIC_CELL_MM,
)


def cell(x_mm: int, y_mm: int, size: int) -> tuple[int, int]:
    return (x_mm // size, y_mm // size)


def strategic_cell(x_mm: int, y_mm: int) -> tuple[int, int]:
    return cell(x_mm, y_mm, STRATEGIC_CELL_MM)


def fine_cell(x_mm: int, y_mm: int) -> tuple[int, int]:
    return cell(x_mm, y_mm, FINE_CELL_MM)


def _dist2(ax: int, ay: int, bx: int, by: int) -> int:
    dx = ax - bx
    dy = ay - by
    return dx * dx + dy * dy


def bubble_radius_mm(track: dict, min_bubble_m: int = MIN_BUBBLE_M, max_bubble_m: int = MAX_BUBBLE_M) -> int:
    raw = int(track["sensor_range_mm"])
    floor = min_bubble_m * 1000
    cap = max_bubble_m * 1000
    return max(floor, min(raw, cap))


def contact_bubbles(world) -> list[str]:
    """Sorted entity ids inside a bubble. Frozen input: tracks + positions at tick start."""
    members: set[str] = set()
    for track in world.tracks:
        if track.get("quality") not in BUBBLE_QUALITIES:
            continue
        r = bubble_radius_mm(track, world.min_bubble_m, world.max_bubble_m)
        r2 = r * r
        tx, ty = int(track["x_mm"]), int(track["y_mm"])
        observer = track.get("observer_id")
        target = track.get("target_id")
        if observer and observer in world.entities:
            members.add(observer)
        if target and target in world.entities:
            members.add(target)
        for eid in world.ids():
            pos = world.entities[eid].get("Position")
            if not pos:
                continue
            if _dist2(int(pos["x_mm"]), int(pos["y_mm"]), tx, ty) <= r2:
                members.add(eid)
    return sorted(members)


def movement_resolution(in_bubble: bool) -> dict:
    if in_bubble:
        return {"cadence_days": DAY, "grid_mm": None, "position": "mm"}
    return {"cadence_days": DAY, "grid_mm": STRATEGIC_CELL_MM, "position": "strategic_cell"}
