"""Measured cells from the catalogs already on disk. No invented coordinate."""

from __future__ import annotations

from pathlib import Path

import yaml


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def _cell_dir() -> Path:
    return _root() / "catalogs" / "cells"


def _year_path(year_state_id: str) -> Path:
    return _root() / "catalogs" / "year_states" / f"{year_state_id}.yaml"


def _measured_rows(path: Path, year_state_id: str | None = None) -> list[dict]:
    data = yaml.safe_load(path.read_text()) or {}
    title = data.get("title") or path.stem
    source = f"{title}. {path.name}"
    rows = []
    for row in data.get("cells") or []:
        if not isinstance(row, dict):
            continue
        x_mm = row.get("x_mm")
        y_mm = row.get("y_mm")
        if type(x_mm) is not int or type(y_mm) is not int:
            continue
        copied = dict(row)
        copied["catalog"] = path.name
        copied["x_mm"] = x_mm
        copied["y_mm"] = y_mm
        copied.setdefault("id", copied.get("id") or f"{path.stem}:{copied.get('name')}")
        copied.setdefault("source", source)
        if year_state_id:
            copied["year_state"] = year_state_id
        rows.append(copied)
    return rows


def load_measured_cells() -> list[dict]:
    """Every catalog row that already has integer x_mm and y_mm."""
    rows = []
    for path in sorted(_cell_dir().glob("*.yaml")):
        rows.extend(_measured_rows(path))
    return rows


def geographic_layer(year_state_id: str) -> list[dict]:
    """Measured cells bound to this year-state. The other continent is not included."""
    path = _year_path(year_state_id)
    state = yaml.safe_load(path.read_text()) if path.exists() else None
    if not state or state.get("id") != year_state_id:
        raise ValueError(f"unknown year-state: {year_state_id}")
    rows = []
    for entry in state.get("cell_catalogs") or []:
        catalog = Path(entry)
        if not catalog.is_absolute():
            catalog = path.parent / catalog
        if not catalog.exists():
            raise ValueError(f"missing cell catalog: {entry}")
        rows.extend(_measured_rows(catalog, year_state_id))
    return rows


def use_year_state_cells(year_state_id: str, cells) -> list[dict]:
    """Refuse a cell whose year-state is not the one asked for."""
    foreign = [row for row in cells or [] if row.get("year_state") != year_state_id]
    if foreign:
        other = foreign[0].get("year_state")
        raise ValueError(f"year-state mismatch: {other}")
    return list(cells or [])
