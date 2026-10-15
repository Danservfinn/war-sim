"""Measured color regions. A vertex is a boundary pixel. A failed second trace is not stored."""

from __future__ import annotations

from pathlib import Path

import json


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def _catalog() -> Path:
    return _root() / "catalogs" / "geography" / "regions.json"


def _load() -> dict:
    path = _catalog()
    if not path.exists():
        return {"regions": [], "gaps": [], "adjacencies": []}
    return json.loads(path.read_text())


def load_regions(year_state: str | None = "") -> list[dict]:
    """Measured polygons. Pass a year-state id to refuse every other sheet."""
    rows = list(_load().get("regions") or [])
    if year_state == "":
        return rows
    return [row for row in rows if row.get("year_state") == year_state]


def load_gaps() -> list[dict]:
    return list(_load().get("gaps") or [])


def load_adjacencies() -> list[dict]:
    return list(_load().get("adjacencies") or [])


def _pixel(row: dict, x_mm: int, y_mm: int) -> tuple[float, float]:
    ox, oy = row["origin_px"]
    scale = float(row["mm_per_px"])
    y_sign = -1.0 if row["y_positive"] == "north" else 1.0
    return (x_mm / scale) + ox, (y_mm / (scale * y_sign)) + oy


def _inside_ring(x: float, y: float, ring: list[dict]) -> bool:
    inside = False
    count = len(ring)
    j = count - 1
    for i in range(count):
        xi, yi = ring[i]["px"], ring[i]["py"]
        xj, yj = ring[j]["px"], ring[j]["py"]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi):
            inside = not inside
        j = i
    return inside


def _inside(row: dict, x_mm: int, y_mm: int) -> bool:
    px, py = _pixel(row, x_mm, y_mm)
    width, height = row["image_size"]
    if px < 0 or py < 0 or px >= width or py >= height:
        return False
    if not _inside_ring(px, py, row["vertices"]):
        return False
    for hole in row.get("holes") or []:
        if _inside_ring(px, py, hole):
            return False
    return True


def ground_step(year_state, x_mm: int, y_mm: int) -> str | None:
    """A step into a measured sea polygon is no_surface. No path is searched."""
    for row in load_regions(year_state):
        if row.get("surface") == "sea" and _inside(row, x_mm, y_mm):
            return "no_surface"
    return None
