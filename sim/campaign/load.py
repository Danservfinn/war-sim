"""Load a scenario folder into the day stepper. No era rules."""

from __future__ import annotations

from pathlib import Path

import yaml

from sim.campaign.step import Campaign
from sim.spatial.cells import geographic_layer


def _read(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


def _year_path(root: Path, entry: str) -> Path:
    path = Path(entry)
    if path.is_absolute():
        return path
    local = root / path
    if local.exists():
        return local
    from_cwd = Path.cwd() / path
    return from_cwd if from_cwd.exists() else local


def _sourced(row: dict) -> bool:
    return bool(str((row or {}).get("source") or "").strip())


def _require_source(row: dict, where: str) -> None:
    if not _sourced(row):
        raise ValueError(f"empty source: {where}")


def _file_sourced(state: dict) -> bool:
    text = (state or {}).get("source") or (state or {}).get("as_of_source") or ""
    return bool(str(text).strip())


def _strip_year_pointer(row: dict) -> dict:
    drop = {"civil_year", "as_of", "region", "goods_cross"}
    return {key: value for key, value in row.items() if key not in drop}


def _year_plant(row: dict, civil_year):
    if row.get("not_a_plant") or row.get("kind") in ("plan", "target", "contract", "export_contract", "national_output"):
        return None
    year = row.get("year")
    if year is not None and (civil_year is None or int(year) != int(civil_year)):
        return None
    if "lines" in row:
        return _strip_year_pointer(row)
    if "daily_cap" in row:
        cap = int(row["daily_cap"])
    elif row.get("annual_t") is not None:
        cap = int(row["annual_t"]) // 360
    else:
        return None
    line = {
        "id": row.get("good") or row["id"],
        "daily_cap": cap,
        "power_mw_need": 1,
        "tools_need": 1,
        "skilled_need": int(row.get("skilled_need", 1)),
        "damage_milli": 0,
    }
    if "powder_local" in row:
        line["powder_local"] = bool(row["powder_local"])
    return {
        "id": row["id"],
        "side": row.get("side") or row.get("state"),
        "continent": row.get("continent"),
        "place": row.get("place"),
        "input_good": row.get("input_good"),
        "input_per": int(row.get("input_per", 1)),
        "strain_milli": 0,
        "dud_base": 10,
        "skilled_labor": int(row.get("skilled_labor", 0)),
        "power_mw": int(row.get("power_mw", 0)),
        "tools": int(row.get("tools", 0)),
        "civilian_share_milli": 0,
        "source": row.get("source"),
        "lines": [line],
    }


def _copy_year_states(root: Path, meta: dict) -> dict:
    entries = meta.get("year_states") or []
    if isinstance(entries, str):
        entries = [entries]
    copied = {
        "leaders": [],
        "generals": [],
        "units": [],
        "plants": [],
        "stocks": {},
        "points": [],
        "links": [],
        "cells": [],
        "series": [],
    }
    seen = set()
    for entry in entries:
        path = _year_path(root, str(entry))
        state = _read(path)
        if not _file_sourced(state):
            raise ValueError(f"empty source: {path}")
        file_ids = {str(item) for item in (state.get("states") or [])}
        for key in ("leaders", "generals", "units", "plants", "points"):
            for row in state.get(key) or []:
                if isinstance(row, dict) and row.get("state"):
                    file_ids.add(str(row["state"]))
        shared = file_ids & seen
        if shared:
            raise ValueError(f"shared state id: {sorted(shared)[0]}")
        seen |= file_ids
        for key in ("leaders", "generals", "points", "links", "cells"):
            for row in state.get(key) or []:
                _require_source(row, key)
                copied[key].append(_strip_year_pointer(row))
        if state.get("cell_catalogs") and state.get("id"):
            for row in geographic_layer(str(state["id"])):
                _require_source(row, "cells")
                copied["cells"].append(_strip_year_pointer(row))
        for row in state.get("units") or []:
            _require_source(row, "units")
            if row.get("kind") == "strength" or row.get("not_a_formation") or row.get("not_placed"):
                continue
            copied["units"].append(_strip_year_pointer(row))
        civil = state.get("civil_year")
        for row in state.get("plants") or []:
            _require_source(row, "plants")
            plant = _year_plant(row, civil)
            if plant is not None:
                copied["plants"].append(plant)
        for row in state.get("series") or []:
            _require_source(row, "series")
            copied["series"].append(_strip_year_pointer(row))
        for row in list(state.get("weapons") or []) + list(state.get("orders") or []):
            _require_source(row, "counted")
        stocks = state.get("stocks") or []
        if isinstance(stocks, dict):
            if stocks:
                raise ValueError("empty source: stocks")
        else:
            for row in stocks:
                _require_source(row, "stocks")
                copied["stocks"][row["id"]] = int(row.get("qty", row.get("t", 0)))
    return copied


def _faction(row: dict) -> dict:
    base = {
        "cohesion": 50,
        "manpower": 10,
        "trainees": 0,
        "training_cap_per_day": 0,
        "food_t": 0,
        "food_burn_t": 0,
        "water_t": 0,
        "water_burn_t": 0,
        "fuel": {},
        "loss_hold_days": 0,
        "cohesion_loss_per_day": 0,
        "stockpile": {},
        "victory_points": 0,
        "surrender_hold_days": 1,
    }
    base.update(row)
    return base


def _catalog_plant(src: dict, row: dict) -> dict:
    return {
        "id": src["id"],
        "side": row["side"],
        "continent": src["continent"],
        "place": src.get("place"),
        "input_good": row.get("input_good"),
        "input_per": int(row.get("input_per", 1)),
        "strain_milli": 0,
        "dud_base": 10,
        "skilled_labor": 1,
        "power_mw": 10,
        "tools": 1,
        "civilian_share_milli": 0,
        "lines": [{
            "id": src["good"],
            "daily_cap": int(src["daily_cap"]),
            "powder_local": bool(src["powder_local"]),
            "power_mw_need": 1,
            "tools_need": 1,
            "skilled_need": 1,
            "damage_milli": 0,
        }],
    }


def load_campaign(root: Path) -> Campaign:
    root = Path(root)
    meta = _read(root / "scenario.yaml")
    factions = {side: _faction(row) for side, row in (_read(root / "factions.yaml").get("factions") or {}).items()}
    units = list(_read(root / "units.yaml").get("units") or [])
    points = list(_read(root / "points.yaml").get("points") or [])
    industry = _read(root / "industry.yaml")
    catalog_path = Path(meta["catalog"])
    if not catalog_path.is_absolute():
        catalog_path = Path.cwd() / catalog_path
    catalog = {row["id"]: row for row in (yaml.safe_load(catalog_path.read_text()) or {}).get("plants") or []}
    plants = []
    for row in industry.get("plants") or []:
        if row.get("from_catalog"):
            plants.append(_catalog_plant(catalog[row["from_catalog"]], row))
        else:
            plants.append(row)
    for point in points:
        point.setdefault("held_by", point["side"])
    for side, fac in factions.items():
        owned = [point for point in points if point["side"] == side]
        if owned:
            fac["victory_points"] = len(owned)
    campaign = Campaign(
        day=0,
        nodes=list(industry.get("nodes") or []),
        refiners=list(industry.get("refiners") or []),
        plants=plants,
        lots=[],
        fleets={"trucks": {"count": 1}},
        links=[],
        in_transit=[],
        imports=list(industry.get("imports") or []),
        factions=factions,
        victory_rules=[],
        history=[],
        victory=None,
        stocks={},
        units=units,
        points=points,
        viewer_side=meta.get("viewer_side"),
        goods_cross=bool(meta.get("goods_cross", False)),
        at_war=list(meta.get("at_war") or []),
        scenario_id=meta.get("id"),
        events=[],
        cells=list(_read(root / "cells.yaml").get("cells") or []),
    )
    if meta.get("year_states"):
        copied = _copy_year_states(root, meta)
        campaign.leaders = copied["leaders"]
        campaign.generals = copied["generals"]
        campaign.units = list(campaign.units) + copied["units"]
        campaign.plants = list(campaign.plants) + copied["plants"]
        campaign.points = list(campaign.points) + copied["points"]
        campaign.links = list(campaign.links) + copied["links"]
        campaign.cells = list(copied["cells"])
        campaign.stocks.update(copied["stocks"])
        campaign.series = copied["series"]
        owner_map = meta.get("owner_map") or {}
        for plant in campaign.plants:
            mapped = owner_map.get(plant.get("side"))
            if mapped:
                plant["side"] = mapped
    campaign.plants_by_id = {plant["id"]: plant for plant in campaign.plants}
    return campaign


def select_year_catalog(name: str, also: str | None = None) -> dict:
    """Plants, stocks, and units from one year-state. The other catalog is not mixed in."""
    if also:
        raise ValueError("mixed year-states")
    root = Path(__file__).resolve().parents[2] / "catalogs" / "year_states" / f"{name}.yaml"
    state = _read(root)
    if not state or state.get("id") != name:
        raise ValueError(f"unknown year-state: {name}")
    units = []
    for row in state.get("units") or []:
        if row.get("kind") == "strength" or row.get("not_a_formation") or row.get("not_placed"):
            continue
        units.append(_strip_year_pointer(row))
    stocks = state.get("stocks") or []
    if isinstance(stocks, list):
        stocks = {}
    return {
        "id": state["id"],
        "plants": list(state.get("plants") or []),
        "stocks": stocks,
        "units": units,
        "leaders": list(state.get("leaders") or []),
    }
