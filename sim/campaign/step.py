"""Day and year stepper. Stocks move. Victory is a condition, not an era."""

from __future__ import annotations

import json
import math
from pathlib import Path


class Campaign:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _link(self, link_id: str) -> dict:
        return next(link for link in self.links if link["id"] == link_id)

    def link_capacity_t(self, link_id: str, volume_l_per_t: int = 0) -> int:
        link = self._link(link_id)
        fleet = self.fleets[link["fleet_id"]]
        keep = 1000 - int(link.get("empties_milli", 0))
        tons = int(fleet["count"]) * int(link["payload_t"]) * keep // 1000
        month = (self.day // 30) % 12
        tons = tons * int((link.get("season_mod") or {}).get(month, 1000)) // 1000
        port = int(link.get("port_slots_t") or 0)
        if port:
            tons = min(tons, port)
        if volume_l_per_t:
            volume = int(fleet["count"]) * int(link["payload_l"]) * keep // 1000
            tons = min(tons, volume // int(volume_l_per_t))
        return tons

    def can_burn(self, side: str, grade: str, qty: int) -> bool:
        return int(self.factions[side]["fuel"].get(grade, 0)) >= int(qty)


def _log_event(c: Campaign, kind: str, sentence: str, **fields) -> None:
    rows = list(getattr(c, "events", None) or [])
    seq = 1 + max(
        (int(row.get("seq") or 0) for row in rows if int(row.get("day") or 0) == c.day),
        default=0,
    )
    row = {"day": c.day, "seq": seq, "kind": kind, "sentence": sentence}
    row.update(fields)
    rows.append(row)
    c.events = rows


def _snap(c: Campaign) -> dict:
    fac = next(iter(c.factions.values()))
    reserve = sum(int(node["reserve_t"]) for node in c.nodes)
    return {
        "day": c.day,
        "year": c.day // 360,
        "reserve_t": reserve,
        "fleet": {key: row["count"] for key, row in c.fleets.items()},
        "strain": [plant["strain_milli"] for plant in c.plants],
        "food_t": fac["food_t"],
        "fuel": dict(fac["fuel"]),
        "cohesion": fac["cohesion"],
        "manpower": fac["manpower"],
        "lots_expired": sum(1 for lot in c.lots if int(lot["dud_milli"]) > int(lot.get("dud_at_mint", lot["dud_milli"]))),
    }


def _age_lots(c: Campaign) -> None:
    for lot in c.lots:
        if "dud_at_mint" not in lot:
            lot["dud_at_mint"] = int(lot["dud_milli"])
        overdue = c.day - int(lot["minted_day"]) - int(lot.get("storage_days", 10**9))
        periods = overdue // 30 if overdue >= 30 else 0
        lot["dud_milli"] = int(lot["dud_at_mint"]) + periods * int(lot.get("age_dud_per_30d", 0))


def _ensure(c: Campaign) -> None:
    c.units = list(getattr(c, "units", []) or [])
    c.hubs = list(getattr(c, "hubs", []) or [])
    c.states = list(getattr(c, "states", []) or [])
    c.research = list(getattr(c, "research", []) or [])
    c.leaders = list(getattr(c, "leaders", []) or [])
    c.conversions = list(getattr(c, "conversions", []) or [])
    c.commanders = list(getattr(c, "commanders", []) or [])
    c.doctrine = dict(getattr(c, "doctrine", {}) or {})
    c.air_missions = list(getattr(c, "air_missions", []) or [])
    c.raids = list(getattr(c, "raids", []) or [])
    c.depots = list(getattr(c, "depots", []) or [])
    c.construction = list(getattr(c, "construction", []) or [])
    c.refiners = list(getattr(c, "refiners", []) or [])
    c.engagements = list(getattr(c, "engagements", []) or [])
    c.contacts = list(getattr(c, "contacts", []) or [])
    c.points = list(getattr(c, "points", []) or [])
    c.cells = list(getattr(c, "cells", []) or [])
    c.mines = list(getattr(c, "mines", []) or [])
    c.generals = list(getattr(c, "generals", []) or [])
    c.march_orders = list(getattr(c, "march_orders", []) or [])
    c.at_war = list(getattr(c, "at_war", []) or [])
    c.continent_stocks = dict(getattr(c, "continent_stocks", {}) or {})
    c.mission_days = list(getattr(c, "mission_days", []) or [])
    c.hull_jobs = list(getattr(c, "hull_jobs", []) or [])
    c.repairs = list(getattr(c, "repairs", []) or [])
    for fac in c.factions.values():
        fac.setdefault("stockpile", {})
        fac.setdefault("fuel", {})
        fac.setdefault("garrison_manpower", 0)
        fac.setdefault("victory_points", 0)
        fac.setdefault("surrender_points", 0)


def _hubs(c: Campaign) -> None:
    for hub in c.hubs:
        trucks = int(hub.get("trucks", 0))
        hub["throughput_t"] = int(hub.get("rail_level", 0)) * max(1, trucks)
    by_id = {hub["id"]: hub for hub in c.hubs}
    for unit in c.units:
        hub = by_id.get(unit.get("hub_id"))
        in_range = bool(unit.get("in_hub_range")) and hub is not None and int(hub["throughput_t"]) > 0
        status = 1000 if in_range else int(unit.get("air_supply_t", 0)) * 100
        unit["supply_status_milli"] = min(1000, status)
        if unit["supply_status_milli"] < 1000:
            unit["organization"] = max(0, int(unit.get("organization", 0)) - 10)
            need = unit.setdefault("equipment", {})
            lost = 0
            for good, qty in list(need.items()):
                cut = max(1, int(qty) // 10) if int(qty) else 0
                need[good] = int(qty) - cut
                lost += cut
            unit["attrition_qty"] = lost
            unit["attack_mod_milli"] = 800 if unit.get("posture") == "attack" else 500
        else:
            unit["attrition_qty"] = 0
            unit["attack_mod_milli"] = 1000
            unit["organization"] = min(int(unit.get("organization_max", 100)), int(unit.get("organization", 0)) + 5)


def _fuel_state(c: Campaign) -> None:
    for unit in c.units:
        if _accepted_march(c, unit):
            continue
        if unit.get("foot") or unit.get("fuel_grade") in (None, "none"):
            unit["fuel_stat_milli"] = 1000
            unit["fuel_speed_milli"] = 1000
            continue
        grade = unit.get("fuel_grade", "diesel")
        fac = c.factions[unit["side"]]
        have = int(fac.setdefault("fuel", {}).get(grade, 0))
        need = int(unit.get("fuel_need", 0))
        if have < need or int(unit.get("supply_status_milli", 1000)) == 0:
            unit["fuel_stat_milli"] = 100
            unit["fuel_speed_milli"] = 600
            continue
        fac["fuel"][grade] = have - need
        unit["fuel_stat_milli"] = 1000
        unit["fuel_speed_milli"] = 1000


def _air(c: Campaign) -> None:
    for mission in c.air_missions:
        if mission.get("kind") == "supply_drop":
            target = next(unit for unit in c.units if unit["id"] == mission["target"])
            target["air_supply_t"] = int(mission.get("supply_t", 0))
        if mission.get("kind") == "cas":
            continue
    c.air_missions = []


def _efficiency(c: Campaign) -> None:
    for plant in c.plants:
        line = plant["lines"][0]
        model = line.get("model")
        if model != plant.get("last_model") and plant.get("last_model") is not None:
            plant["efficiency_milli"] = min(100, int(plant.get("efficiency_milli", 0)) // 5)
        elif "efficiency_milli" in plant:
            cap = int(plant.get("efficiency_cap_milli", 1000))
            plant["efficiency_milli"] = min(cap, int(plant["efficiency_milli"]) + 50)
        plant["last_model"] = model


def _power(c: Campaign) -> None:
    for state in c.states:
        out = int(state.get("power_plants", 0)) * int(state.get("terrain_power", 0))
        out += int(state.get("coal_boost", 0)) + int(state.get("industry_power", 0))
        if state.get("occupied"):
            resist = int(state.get("resistance", 0))
            state["output_milli"] = max(0, 1000 - resist)
            out = out * int(state["output_milli"]) // 1000
            owner = state.get("owner")
            if owner in c.factions:
                c.factions[owner]["garrison_manpower"] = int(c.factions[owner].get("garrison_manpower", 0)) + int(state.get("garrison_need", 0))
        else:
            state["output_milli"] = 1000
        state["power_out"] = out
    for plant in c.plants:
        state = next((row for row in c.states if row.get("owner") == plant.get("side")), None)
        supply = int(state["power_out"]) if state else int(plant.get("power_mw", 0))
        draw = int(plant["lines"][0].get("power_draw", plant["lines"][0].get("power_mw_need", 0)))
        ratio = 1000 if draw <= 0 else min(1000, supply * 1000 // draw)
        plant["energy_ratio_milli"] = ratio
        plant["power_ratio_milli"] = ratio


def _quiet_attrition(c: Campaign) -> None:
    for unit in c.units:
        rate = int(unit.get("reliability_milli", 0))
        if rate <= 0:
            continue
        for good, qty in list(unit.get("equipment", {}).items()):
            lost = max(1, int(qty) * rate // 1000)
            unit["equipment"][good] = max(0, int(qty) - lost)
        stock = c.factions[unit["side"]].setdefault("stockpile", {})
        for good, qty in list(stock.items()):
            if int(qty) <= 0:
                continue
            stock[good] = int(qty) - max(1, int(qty) * rate // 1000)


def _research(c: Campaign) -> None:
    # Technical level is frozen. A row never unlocks. A leader order can retool a plant. It cannot unlock this row.
    for row in c.research:
        row["unlocked"] = False


def _seated(c: Campaign, leader: dict) -> bool:
    if not str(leader.get("name") or "").strip():
        return False
    if not str(leader.get("source") or "").strip():
        return False
    return int(leader.get("from_day", 0)) <= c.day < int(leader.get("to_day", 0))


def _way_open(link: dict) -> bool:
    return link.get("kind") in ("road", "rail") and link.get("open", True) and int(link.get("capacity_t", 0)) > 0


def _incident(c: Campaign, node_id: str) -> list:
    return [
        link for link in c.links
        if _way_open(link) and node_id in (link.get("from_node"), link.get("to_node"))
    ]


def _node_feeds(plant: dict, node: dict) -> bool:
    home = plant.get("continent")
    there = node.get("continent")
    if home and there and there != home:
        return False
    return True


def _plant_accessible(c: Campaign, plant: dict) -> bool:
    node = plant.get("node_id")
    if not node:
        return True
    return bool(_incident(c, node))


def _carries(link: dict, good: str | None) -> bool:
    """A named cargo stays that cargo. An unnamed link is not a second good."""
    if not good:
        return True
    cargo = link.get("cargo_id")
    if cargo in (None, "", "none"):
        return True
    return cargo == good


def _path_cap(c: Campaign, origin: str, dest: str, good: str | None = None) -> int:
    if not origin or not dest:
        return 0
    if origin == dest:
        return 10 ** 9
    best = {origin: 10 ** 9}
    seen = set()
    while True:
        cur = None
        cur_cap = -1
        for node, cap in best.items():
            if node in seen:
                continue
            if cap > cur_cap:
                cur, cur_cap = node, cap
        if cur is None:
            return 0
        if cur == dest:
            return cur_cap
        seen.add(cur)
        for link in c.links:
            if not _way_open(link) or not _carries(link, good):
                continue
            a, b = link.get("from_node"), link.get("to_node")
            nxt = b if a == cur else a if b == cur else None
            if not nxt:
                continue
            thru = min(cur_cap, int(link["capacity_t"]))
            if thru > int(best.get(nxt, -1)):
                best[nxt] = thru


def _deliverable(c: Campaign, plant: dict, good: str) -> int:
    dest = plant.get("node_id")
    if not dest or not _plant_accessible(c, plant):
        return 0
    local = 0
    remote = 0
    incident = sum(int(link["capacity_t"]) for link in _incident(c, dest) if _carries(link, good))
    for node in c.nodes:
        if node.get("good") != good or not _node_feeds(plant, node):
            continue
        stock = int(node.get("stock_t", 0))
        if node.get("id") == dest:
            local += stock
        else:
            remote += min(stock, _path_cap(c, node.get("id") or "", dest, good))
    return local + min(remote, incident)


def _draw_input(c: Campaign, plant: dict, good: str, qty: int) -> int:
    dest = plant.get("node_id")
    left = int(qty)
    if left <= 0 or not dest:
        return 0
    for node in sorted(c.nodes, key=lambda row: row.get("id") or ""):
        if node.get("id") != dest or node.get("good") != good or not _node_feeds(plant, node):
            continue
        take = min(left, int(node.get("stock_t", 0)))
        node["stock_t"] = int(node["stock_t"]) - take
        left -= take
    incident = sum(int(link["capacity_t"]) for link in _incident(c, dest) if _carries(link, good))
    moved = 0
    for node in sorted(c.nodes, key=lambda row: row.get("id") or ""):
        if left <= 0 or moved >= incident:
            break
        if node.get("id") == dest or node.get("good") != good or not _node_feeds(plant, node):
            continue
        take = min(left, int(node.get("stock_t", 0)), _path_cap(c, node.get("id") or "", dest, good), incident - moved)
        if take <= 0:
            continue
        node["stock_t"] = int(node["stock_t"]) - take
        left -= take
        moved += take
    return int(qty) - left


def _skill_ok(plant: dict, skill: str, need: int) -> bool:
    if not skill:
        return False
    return int((plant.get("labor") or {}).get(skill, 0)) >= int(need)


def _gate(c: Campaign, plant: dict, skill: str, inputs: dict) -> str:
    """Resources, the named skill, then a live road or rail. A continent pile is not a resource."""
    if not plant.get("node_id") or not _plant_accessible(c, plant):
        return "no_access"
    if not _skill_ok(plant, skill, plant["lines"][0].get("skilled_need", 1)):
        return "no_skill"
    if not inputs:
        return "no_input"
    for good, per in inputs.items():
        if _deliverable(c, plant, good) < max(1, int(per)):
            return "no_input"
    return ""


def _general_seated(c: Campaign, general: dict) -> bool:
    if not general.get("name") or not general.get("source") or general.get("captured"):
        return False
    return int(general.get("from_day", 0)) <= c.day < int(general.get("to_day", 0))


def _decide(c: Campaign) -> None:
    """Strategic orders come from the leader in office. A land posture does not."""
    for leader in c.leaders:
        if not _seated(c, leader):
            continue
        policy = leader.get("policy") or {}
        for row in policy.get("conversions") or []:
            if int(row.get("issue_day", -1)) != c.day:
                continue
            plant = next((item for item in c.plants if item.get("id") == row.get("plant_id")), None)
            if plant is None or plant.get("owner") != leader.get("state"):
                continue
            line = plant["lines"][0]
            if int(line.get("daily_cap", 0)) <= 0:
                continue
            output = row.get("output")
            if not output or output in (plant.get("capabilities") or []):
                continue
            if any(job.get("plant_id") == plant["id"] and job.get("output") == output for job in c.conversions):
                continue
            skill = row.get("skill") or ""
            inputs = row.get("inputs") or {}
            reason = _gate(c, plant, skill, inputs)
            if reason:
                plant["gate"] = reason
                continue
            c.conversions.append({
                "plant_id": plant["id"],
                "output": output,
                "days_left": int(row["days"]),
                "capacity_milli": min(1000, int(row.get("capacity_milli", 1000))),
                "signed_by": leader["id"],
                "skill": skill,
                "inputs": dict(inputs),
            })
    for general in c.generals:
        if not _general_seated(c, general):
            continue
        for row in (general.get("policy") or {}).get("tactical") or []:
            if int(row.get("issue_day", -1)) != c.day:
                continue
            unit = next((item for item in c.units if item.get("id") == row.get("unit_id")), None)
            if unit is None or unit.get("id") not in (general.get("command") or []):
                continue
            if general.get("state") != unit.get("side"):
                continue
            if row.get("posture"):
                unit["posture"] = row["posture"]
    _accept_hulls(c)
    _accept_repairs(c)


def _finish_conversion(c: Campaign, job: dict) -> None:
    plant = next(item for item in c.plants if item.get("id") == job["plant_id"])
    caps = plant.setdefault("capabilities", [])
    if job["output"] not in caps:
        caps.append(job["output"])
    line = plant["lines"][0]
    line["output"] = job["output"]
    line["requires"] = [job["output"]]
    line["skill"] = job.get("skill") or ""
    line["inputs"] = dict(job.get("inputs") or {})


def _convert(c: Campaign) -> None:
    still = []
    for job in c.conversions:
        if not job.get("signed_by"):
            continue
        if int(job.get("days_left", 0)) <= 0:
            _finish_conversion(c, job)
            continue
        still.append(job)
    c.conversions = still


def _tick_conversions(c: Campaign) -> None:
    for job in c.conversions:
        plant = next(item for item in c.plants if item.get("id") == job["plant_id"])
        reason = _gate(c, plant, job.get("skill") or "", job.get("inputs") or {})
        if reason:
            plant["gate"] = reason
            continue
        job["days_left"] = int(job["days_left"]) - 1
        plant["gate"] = ""
    _tick_hulls(c)
    _tick_repairs(c)


def _owns(plant: dict, state: str) -> bool:
    return state in (plant.get("owner"), plant.get("side"))


def _accept_hulls(c: Campaign) -> None:
    for leader in c.leaders:
        if not _seated(c, leader):
            continue
        for row in (leader.get("policy") or {}).get("hulls") or []:
            if int(row.get("issue_day", -1)) != c.day:
                continue
            plant = next((item for item in c.plants if item.get("id") == row.get("plant_id")), None)
            hull = dict(row.get("hull") or {})
            if plant is None or not _owns(plant, leader.get("state")) or not hull.get("id"):
                continue
            if any(job.get("hull", {}).get("id") == hull["id"] for job in c.hull_jobs):
                continue
            if any(unit.get("id") == hull["id"] for unit in c.units):
                continue
            reason = _gate(c, plant, row.get("skill") or "", row.get("inputs") or {})
            if reason:
                plant["gate"] = reason
                continue
            c.hull_jobs.append({
                "plant_id": plant["id"],
                "days_left": int(row["days"]),
                "skill": row.get("skill") or "",
                "inputs": dict(row.get("inputs") or {}),
                "hull": hull,
                "signed_by": leader["id"],
                "side": leader["state"],
            })


def _tick_hulls(c: Campaign) -> None:
    still = []
    for job in c.hull_jobs:
        plant = next((item for item in c.plants if item.get("id") == job["plant_id"]), None)
        if plant is None:
            continue
        reason = _gate(c, plant, job.get("skill") or "", job.get("inputs") or {})
        if reason:
            plant["gate"] = reason
            still.append(job)
            continue
        if int(job["days_left"]) > 0:
            job["days_left"] = int(job["days_left"]) - 1
            still.append(job)
            continue
        short = False
        for good, qty in (job.get("inputs") or {}).items():
            if _draw_input(c, plant, good, int(qty)) < int(qty):
                short = True
                break
        if short:
            still.append(job)
            continue
        hull = dict(job["hull"])
        hull.setdefault("side", job["side"])
        hull.setdefault("alive", True)
        hull.setdefault("domain", "sea")
        c.units.append(hull)
    c.hull_jobs = still


def _accept_repairs(c: Campaign) -> None:
    for leader in c.leaders:
        if not _seated(c, leader):
            continue
        for row in (leader.get("policy") or {}).get("repairs") or []:
            if int(row.get("issue_day", -1)) != c.day:
                continue
            if any(job.get("cell_id") == row.get("cell_id") for job in c.repairs):
                continue
            c.repairs.append({
                "cell_id": row.get("cell_id"),
                "days_left": int(row["days"]),
                "signed_by": leader["id"],
                "state": leader.get("state"),
            })


def _tick_repairs(c: Campaign) -> None:
    still = []
    for job in c.repairs:
        cell = next((row for row in c.cells if row.get("id") == job.get("cell_id")), None)
        if cell is None:
            continue
        engineer = any(
            unit.get("alive", True) and unit.get("role") == "engineer"
            and unit.get("cell_id") == cell["id"] and unit.get("side") == job.get("state")
            for unit in c.units
        )
        if not engineer or int(job["days_left"]) > 1:
            if engineer and int(job["days_left"]) > 1:
                job["days_left"] = int(job["days_left"]) - 1
            still.append(job)
            continue
        cell["damage_milli"] = 0
    c.repairs = still


def _committed_cap(c: Campaign, plant: dict) -> int:
    line = plant["lines"][0]
    share = 0
    for job in c.conversions:
        if job.get("plant_id") != plant.get("id") or int(job.get("days_left", 0)) <= 0:
            continue
        share += int(line["daily_cap"]) * int(job.get("capacity_milli", 1000)) // 1000
    return min(int(line["daily_cap"]), share)


def _refine(c: Campaign) -> None:
    """Ore is not a usable good. A refiner consumes a node stock and emits another good."""
    for ref in c.refiners:
        source = next((node for node in c.nodes if node.get("good") == ref["consumes"]
                       and node.get("continent") == ref.get("continent")), None)
        have = int(source["stock_t"]) if source else 0
        made = min(int(ref["daily_cap"]), have * int(ref["ratio_milli"]) // 1000)
        used = min(have, made * 1000 // max(1, int(ref["ratio_milli"])))
        if source:
            source["stock_t"] = have - used
        ref["out_t"] = made
        if made:
            pile = c.continent_stocks.setdefault(ref.get("continent") or "", {})
            pile[ref["makes"]] = int(pile.get(ref["makes"], 0)) + made


def _cross_continent(c: Campaign, row: dict) -> bool:
    origin = row.get("from_continent") or row.get("continent")
    dest = row.get("to_continent") or row.get("continent")
    return bool(origin and dest and origin != dest)


def _orders(c: Campaign) -> None:
    for unit in c.units:
        if int(unit.get("order_days", 0)) or int(unit.get("planning", 0)):
            unit["planning"] = int(unit.get("planning", 0)) + 1
            unit["order_days"] = int(unit.get("order_days", 0)) + 1
        if unit.get("posture") == "defend":
            unit["stationary_days"] = int(unit.get("stationary_days", 0)) + 1
            unit["entrenchment"] = int(unit.get("entrenchment", 0)) + 1


def _raids(c: Campaign) -> None:
    hit = {row["target"] for row in c.raids if int(row.get("day", -1)) == c.day and int(row.get("sink_milli", 0)) >= 1000}
    if hit:
        c.in_transit = [row for row in c.in_transit if row["id"] not in hit]
    c.raids = [row for row in c.raids if int(row.get("day", -1)) != c.day]


def _capture(c: Campaign) -> None:
    for depot in c.depots:
        taker = depot.get("captured_by")
        if not taker or int(depot.get("captured_day", -1)) != c.day:
            continue
        pile = c.factions.setdefault(taker, {}).setdefault("stockpile", {})
        for good, qty in list(depot.get("stock", {}).items()):
            pile[good] = int(pile.get(good, 0)) + int(qty)
            depot["stock"][good] = 0


def _build(c: Campaign) -> None:
    still = []
    for job in c.construction:
        job["days_left"] = int(job["days_left"]) - 1
        if int(job["days_left"]) > 0:
            still.append(job)
            continue
        if job.get("kind") == "rail":
            hub = next(row for row in c.hubs if row["id"] == job["target"])
            hub["rail_level"] = int(hub.get("rail_level", 0)) + int(job.get("levels", 1))
    c.construction = still


def _surrender(c: Campaign) -> None:
    """Complete and total. Points, units, stocks, and output must all be gone."""
    if c.victory:
        return
    for side, fac in c.factions.items():
        living = any(unit.get("alive", True) and unit.get("side") == side for unit in c.units)
        stock = sum(int(qty) for qty in (fac.get("stockpile") or {}).values())
        output = 0
        for plant in c.plants:
            owner = plant.get("side")
            if owner not in (None, side):
                continue
            output += int(plant.get("military_out", 0))
        if int(fac.get("victory_points", 0)) > 0 or living or stock > 0 or output > 0:
            fac["surrender_held"] = 0
            continue
        fac["surrender_held"] = int(fac.get("surrender_held", 0)) + 1
        if fac["surrender_held"] < int(fac.get("surrender_hold_days", 1)):
            continue
        winner = next((other for other in c.factions if other != side), "other")
        held = int(fac["surrender_held"])
        _log_event(
            c,
            "state_surrender",
            f"{side} surrendered. Points 0, living 0, stock 0, output 0, held {held} days.",
            numbers={"points": 0, "living": 0, "stock": 0, "output": 0, "held_days": held},
        )
        c.history.append(_snap(c))
        c.victory = {
            "winner": winner,
            "lost": side,
            "reason": "total_surrender",
            "day": c.day,
            "history": list(c.history),
        }
        return


def _mine(c: Campaign) -> None:
    month = (c.day // 30) % 12
    for node in c.nodes:
        mod = int((node.get("season_mod") or {}).get(month, 1000))
        raw = int(node["nameplate_t"]) * mod // 1000
        out = min(raw, int(node["reserve_t"]))
        node["reserve_t"] = int(node["reserve_t"]) - out
        # Ore stays on the node. A refiner takes it. It is not a usable good.
        node["stock_t"] = int(node.get("stock_t", 0)) + out
        node["last_output_t"] = out


def _produce(c: Campaign) -> None:
    for plant in c.plants:
        line = plant["lines"][0]
        can = (
            int(plant["power_mw"]) >= int(line["power_mw_need"])
            and int(plant["tools"]) >= int(line["tools_need"])
            and int(plant["skilled_labor"]) >= int(line["skilled_need"])
            and int(line["damage_milli"]) < 1000
        )
        if not can:
            plant["military_out"] = 0
            plant["strain_milli"] = max(0, int(plant["strain_milli"]) - 20)
            continue
        cap = int(line["daily_cap"]) - _committed_cap(c, plant)
        ratio = int(plant.get("power_ratio_milli", 1000))
        eff = int(plant.get("efficiency_milli", 1000))
        out = cap * (1000 - int(line["damage_milli"])) // 1000
        out = out * ratio // 1000 * eff // 1000
        requires = line.get("requires") or []
        have_caps = plant.get("capabilities") or []
        if any(req not in have_caps for req in requires):
            out = 0
        if line.get("powder_local") is False and not getattr(c, "imports_open", False):
            out = 0
        networked = bool(line.get("inputs")) or bool(line.get("skill"))
        if plant.get("node_id") and not _plant_accessible(c, plant):
            out = 0
            plant["gate"] = "no_access"
        elif networked:
            reason = _gate(c, plant, line.get("skill") or "", line.get("inputs") or {})
            if reason:
                out = 0
                plant["gate"] = reason
            else:
                for good, per in (line.get("inputs") or {}).items():
                    out = min(out, _deliverable(c, plant, good) // max(1, int(per)))
                if out <= 0 and line.get("inputs"):
                    plant["gate"] = "no_input"
                else:
                    for good, per in (line.get("inputs") or {}).items():
                        _draw_input(c, plant, good, out * int(per))
                    plant["gate"] = ""
        else:
            need = plant.get("input_good")
            if need:
                if not plant.get("node_id"):
                    out = 0
                    plant["gate"] = "no_access"
                else:
                    per = max(1, int(plant.get("input_per", 1)))
                    have = _deliverable(c, plant, need)
                    out = min(out, have // per)
                    if out:
                        _draw_input(c, plant, need, out * per)
                        plant["gate"] = ""
                    else:
                        out = 0
                        plant["gate"] = "no_input"
        military = out * (1000 - int(plant["civilian_share_milli"])) // 1000
        plant["military_out"] = military
        if military == 0 and plant.get("gate"):
            _log_event(
                c,
                "plant_gate",
                f"Plant {plant['id']} produced 0. Gate {plant['gate']}.",
                place_name=plant.get("place"),
                numbers={"military_out": 0},
            )
        dud = int(plant["dud_base"]) + int(plant["strain_milli"]) // 10
        c.lots.append({
            "lot_id": f"{plant['id']}-{c.day}",
            "ammo_id": line.get("output", "he"),
            "plant_id": plant["id"],
            "minted_day": c.day,
            "qty": military,
            "dud_milli": dud,
            "dud_at_mint": dud,
            "storage_days": 1800,
            "age_dud_per_30d": 10,
        })
        if out >= cap:
            plant["strain_milli"] = min(1000, int(plant["strain_milli"]) + 50)


def _arrive_and_dispatch(c: Campaign) -> None:
    still = []
    for row in c.in_transit:
        if int(row["arrive_day"]) != c.day:
            still.append(row)
            continue
        if row["cargo_id"] == "food":
            for fac in c.factions.values():
                fac["food_t"] = int(fac["food_t"]) + int(row["qty_t"])
        else:
            c.stocks[row["cargo_id"]] = int(c.stocks.get(row["cargo_id"], 0)) + int(row["qty_t"])
    c.in_transit = still
    for link in c.links:
        if link.get("kind") == "lift" and not link.get("open"):
            continue
        if _cross_continent(c, link):
            continue
        cargo = link["cargo_id"]
        have = int(c.stocks.get(cargo, 0))
        cap = c.link_capacity_t(link["id"])
        qty = min(have, cap)
        if qty <= 0 or int(link["distance_km"]) <= 0:
            continue
        days = max(1, int(link["distance_km"]) // int(link["speed_km_per_day"]))
        c.stocks[cargo] = have - qty
        c.in_transit.append({
            "id": f"{link['id']}-{c.day}",
            "link_id": link["id"],
            "cargo_id": cargo,
            "qty_t": qty,
            "depart_day": c.day,
            "arrive_day": c.day + days,
        })


def _imports(c: Campaign) -> None:
    for imp in c.imports:
        embargo = imp.get("embargo_day")
        for row in imp["schedule"]:
            if int(row["day"]) != c.day or row.get("shipped"):
                continue
            row["shipped"] = True
            if _cross_continent(c, imp) or (embargo is not None and c.day >= int(embargo)):
                continue
            imp["received_t"] = int(imp["received_t"]) + int(row["qty_t"])
            c.stocks[imp["good"]] = int(c.stocks.get(imp["good"], 0)) + int(row["qty_t"])


def _consume(c: Campaign) -> None:
    for fac in c.factions.values():
        burn = int(fac["food_burn_t"])
        fac["food_t"] = max(0, int(fac["food_t"]) - burn)
        if int(fac["food_t"]) <= 0:
            fac["cohesion"] = max(0, int(fac["cohesion"]) - int(fac["cohesion_loss_per_day"]))
            fac["loss_hold_days"] = int(fac["loss_hold_days"]) + 1
        else:
            fac["loss_hold_days"] = 0
        grad = min(int(fac["trainees"]), int(fac["training_cap_per_day"]))
        fac["trainees"] = int(fac["trainees"]) - grad
        fac["manpower"] = int(fac["manpower"]) + grad
        fac["graduated_today"] = grad


def _victory(c: Campaign) -> None:
    if c.day > 0 and c.day % 360 == 0:
        c.history.append(_snap(c))


def _units_gone(c: Campaign) -> None:
    return


def _accepted_march(c: Campaign, unit: dict):
    for order in c.march_orders:
        if order.get("entity_id") != unit.get("id"):
            continue
        if c.day < int(order.get("active_day", 0)):
            continue
        course = order.get("course") or []
        if int(order.get("waypoint", 0)) >= len(course):
            continue
        return order
    return None


def _along(x: int, y: int, wx: int, wy: int, step: int):
    dx = wx - x
    dy = wy - y
    dist = math.isqrt(dx * dx + dy * dy)
    if dist == 0:
        return x, y, True
    if step >= dist:
        return wx, wy, True
    if step <= 0:
        return x, y, False
    nx = x + dx * step // dist
    ny = y + dy * step // dist
    if nx == x and ny == y:
        if abs(dx) >= abs(dy) and dx:
            nx = x + (1 if dx > 0 else -1)
        elif dy:
            ny = y + (1 if dy > 0 else -1)
    return nx, ny, nx == wx and ny == wy


def _grid_step(x: int, y: int, wx: int, wy: int, cell: int):
    dx = wx - x
    dy = wy - y
    if math.isqrt(dx * dx + dy * dy) < cell:
        return x, y, False
    if abs(dx) >= abs(dy):
        if abs(dx) < cell:
            return x, y, False
        sign = 1 if dx > 0 else -1
        nx = x + sign * cell
        if (dx > 0 and nx > wx) or (dx < 0 and nx < wx):
            nx = wx
        return nx, y, nx == wx and y == wy
    if abs(dy) < cell:
        return x, y, False
    sign = 1 if dy > 0 else -1
    ny = y + sign * cell
    if (dy > 0 and ny > wy) or (dy < 0 and ny < wy):
        ny = wy
    return x, ny, x == wx and ny == wy


def _pay_march_fuel(unit: dict) -> bool:
    if unit.get("foot") or not unit.get("fuel_grade"):
        return True
    links = unit.get("supply_links") or []
    source = int(unit.get("supply_source_t", 0))
    if links and source:
        from sim.systems.logistics import path_delivery
        unit["fuel_buffer"] = int(unit.get("fuel_buffer", 0)) + path_delivery(source, links)
        unit["supply_source_t"] = 0
    need = int(unit.get("fuel_need", 0))
    have = int(unit.get("fuel_buffer", 0))
    if have < need:
        return False
    unit["fuel_buffer"] = have - need
    return True


def _point_on_segment(x: int, y: int, nx: int, ny: int, cx: int, cy: int) -> bool:
    dx = nx - x
    dy = ny - y
    ex = cx - x
    ey = cy - y
    if dx * ey - dy * ex != 0:
        return False
    dot = ex * dx + ey * dy
    if dot < 0:
        return False
    return dot <= dx * dx + dy * dy


def _move_cells(c: Campaign, unit: dict) -> list:
    cells = [row for row in (getattr(c, "cells", None) or []) if isinstance(row, dict)]
    bound = unit.get("year_state")
    tags = {row.get("year_state") for row in cells if row.get("year_state")}
    if bound:
        return [row for row in cells if row.get("year_state") == bound]
    if len(tags) > 1:
        return [row for row in cells if not row.get("year_state")]
    return cells


def _measured_point(cell: dict) -> bool:
    return type(cell.get("x_mm")) is int and type(cell.get("y_mm")) is int


def _leaves_measured_land(cells, nx: int, ny: int) -> bool:
    """A step that is not exactly a measured land cell has left every one. No interpolation."""
    land = [row for row in cells if row.get("surface") == "land" and _measured_point(row)]
    if not land:
        return False
    return not any(row["x_mm"] == nx and row["y_mm"] == ny for row in land)


def _crosses_sea(c: Campaign, x: int, y: int, nx: int, ny: int, cells=None) -> bool:
    rows = c.cells if cells is None else cells
    catalog = None
    for cell in rows:
        if _measured_point(cell) and cell["x_mm"] == x and cell["y_mm"] == y:
            catalog = cell.get("catalog")
            break
    for cell in rows:
        if cell.get("surface") not in ("sea", "strait") or not _measured_point(cell):
            continue
        if catalog and cell.get("catalog") and cell.get("catalog") != catalog:
            if cell["x_mm"] == nx and cell["y_mm"] == ny:
                return True
            continue
        cx = cell["x_mm"]
        cy = cell["y_mm"]
        if cx == x and cy == y:
            continue
        if _point_on_segment(x, y, nx, ny, cx, cy):
            return True
    return False


def _move(c: Campaign) -> None:
    """One day of march. No accepted course, no move. Heading is not an order."""
    cell = 10_000_000
    for unit in c.units:
        if not unit.get("alive", True) or unit.get("domain") in ("sea", "port") or unit.get("embarked_on"):
            continue
        order = _accepted_march(c, unit)
        if order is None:
            continue
        point = order["course"][int(order.get("waypoint", 0))]
        x = int(unit.get("x_mm", 0))
        y = int(unit.get("y_mm", 0))
        wx = int(point["x_mm"])
        wy = int(point["y_mm"])
        if unit.get("in_bubble"):
            step = int(unit.get("speed_mm_per_day", 0))
            nx, ny, reached = _along(x, y, wx, wy, step)
            moved = (nx, ny) != (x, y) or reached
        else:
            nx, ny, reached = _grid_step(x, y, wx, wy, cell)
            moved = (nx, ny) != (x, y) or reached
        if not moved:
            continue
        layer = _move_cells(c, unit)
        if _crosses_sea(c, x, y, nx, ny, layer) or _leaves_measured_land(layer, nx, ny):
            order["gate"] = "no_surface"
            continue
        if not _pay_march_fuel(unit):
            continue
        unit["x_mm"] = nx
        unit["y_mm"] = ny
        if reached:
            order["waypoint"] = int(order.get("waypoint", 0)) + 1


def _detect(c: Campaign) -> None:
    """A living unit sees another side inside its sensor range. Same cell is not omniscience."""
    from sim.rng.streams import Stream
    from sim.systems.naval import weather_milli

    rng = Stream(int(getattr(c, "seed", 0) or 0), c.day, "detect")
    existing = {(row["observer"], row["target"]): row for row in c.contacts}

    def hidden(observer, target) -> bool:
        if target.get("detectable", True) is False or target.get("embarked_on"):
            return True
        return target.get("posture") == "submerged" and not observer.get("sees_submerged")

    def local(observer, target) -> bool:
        origin = observer.get("cell_id")
        dest = target.get("cell_id")
        if not origin or not dest:
            return False
        if origin == dest:
            return bool(observer.get("WeaponMount")) or observer.get("posture") == "patrol"
        cell = next((row for row in c.cells if row.get("id") == origin), None)
        return bool(cell and dest in (cell.get("covers") or []))

    for observer in c.units:
        if not observer.get("alive", True) or observer.get("embarked_on"):
            continue
        if observer.get("domain") == "air" and not observer.get("sortie_flown"):
            continue
        reach = int(observer.get("sensor_range_mm", 0))
        for target in c.units:
            if target["id"] == observer["id"] or target.get("side") == observer.get("side"):
                continue
            if hidden(observer, target):
                continue
            key = (observer["id"], target["id"])
            dx = int(observer.get("x_mm", 0)) - int(target.get("x_mm", 0))
            dy = int(observer.get("y_mm", 0)) - int(target.get("y_mm", 0))
            in_range = reach > 0 and dx * dx + dy * dy <= reach * reach
            here = local(observer, target)
            if not here and not in_range:
                continue
            if not here:
                signature = int(((target.get("Physical") or {}).get("signature") or {}).get("visual", 1000))
                if target.get("posture") == "submerged":
                    signature = int(((target.get("Physical") or {}).get("signature") or {}).get("submerged", 0))
                detect = weather_milli(c, target) * signature // 1000
                if rng.roll(1000) >= detect:
                    continue
            if key in existing:
                existing[key]["day"] = c.day
                existing[key]["quality"] = "detected"
                continue
            row = {"observer": observer["id"], "target": target["id"], "quality": "detected", "day": c.day}
            c.contacts.append(row)
            existing[key] = row
    for row in c.contacts:
        if int(row.get("day", -1)) != c.day:
            row["quality"] = "last_known"


def _isqrt(n: int) -> int:
    n = max(0, int(n))
    guess = 0
    bit = 1 << 62
    while bit:
        trial = guess + bit
        if trial * trial <= n:
            guess = trial
        bit >>= 2
    return guess


def _engage(c: Campaign) -> None:
    """A contact inside weapon range becomes one shot that day. No scheduled script."""
    by_id = {unit["id"]: unit for unit in c.units}
    for contact in c.contacts:
        if int(contact.get("day", -1)) != c.day:
            continue
        attacker = by_id.get(contact["observer"])
        defender = by_id.get(contact["target"])
        if not attacker or not defender or not defender.get("alive", True):
            continue
        if attacker.get("embarked_on") or defender.get("embarked_on"):
            continue
        if attacker.get("domain") == "air" and not attacker.get("sortie_flown"):
            continue
        mounts = attacker.get("WeaponMount") or []
        if not mounts:
            continue
        dx = int(attacker.get("x_mm", 0)) - int(defender.get("x_mm", 0))
        dy = int(attacker.get("y_mm", 0)) - int(defender.get("y_mm", 0))
        reach_m = max(int(band["max_m"]) for mount in mounts for band in mount.get("range_bands") or [{"max_m": 0}])
        if _isqrt(dx * dx + dy * dy) > reach_m * 1000:
            continue
        defender.setdefault("Physical", {
            "integrity": int(defender.get("integrity", 10)),
            "signature": {"visual": 1000},
            "armor": [{"aspect": "front", "thickness_mm": 0, "ke_mod": 1000}],
        })
        from sim.systems.naval import weather_milli
        c.engagements.append({
            "day": c.day,
            "attacker": attacker,
            "defender": defender,
            "distance_m": max(1, _isqrt(dx * dx + dy * dy) // 1000),
            "weather": weather_milli(c, defender),
            "aspect": "front",
        })


def _near(unit: dict, point: dict) -> bool:
    dx = int(unit.get("x_mm", 0)) - int(point["x_mm"])
    dy = int(unit.get("y_mm", 0)) - int(point["y_mm"])
    reach = int(point.get("hold_mm", 0))
    return dx * dx + dy * dy <= reach * reach


def _take_points(c: Campaign) -> None:
    for point in c.points:
        friendly = any(
            unit.get("alive", True) and unit.get("side") == point["side"] and _near(unit, point)
            for unit in c.units
        )
        hostile = next((
            unit for unit in c.units
            if unit.get("alive", True) and unit.get("side") != point["side"] and _near(unit, point)
        ), None)
        if hostile and not friendly:
            point["held_by"] = hostile["side"]
        elif friendly:
            point["held_by"] = point["side"]
    for side, fac in c.factions.items():
        owned = [point for point in c.points if point["side"] == side]
        if not owned:
            continue
        fac["victory_points"] = sum(1 for point in owned if point.get("held_by", side) == side)


def _ready(mount: dict) -> int:
    return sum(int(ammo.get("qty", 0)) for ammo in mount.get("ammo") or [])


def _fight(c: Campaign) -> None:
    """One clock. Engagements share each mount's day cap. Target ids sort ascending."""
    from sim.systems.combat import resolve_shot
    from sim.systems.naval import mount_may_fire, screen_target

    class _Roll:
        def roll(self, n: int) -> int:
            return 0

    rows = [
        row for row in c.engagements
        if int(row.get("day", c.day)) == c.day and not row.get("resolved")
    ]
    rows.sort(key=lambda row: str(row["defender"].get("id", "")))
    for row in rows:
        attacker = row["attacker"]
        row["defender"] = screen_target(attacker, row["defender"], c.units)
        mounts = sorted(attacker.get("WeaponMount") or [], key=lambda item: item.get("mount_id", ""))
        last = None
        for mount in mounts:
            if not mount_may_fire(attacker, mount, row["defender"]):
                continue
            cap = int(mount.get("rounds_per_day", 1))
            fired = int(mount.get("fired_today", 0))
            budget = min(_ready(mount), max(0, cap - fired))
            for _ in range(budget):
                last = resolve_shot(
                    attacker, row["defender"], int(row["distance_m"]),
                    int(row["weather"]), row["aspect"], _Roll(),
                    mount_id=mount.get("mount_id"),
                )
                outcome = last.get("outcome") if isinstance(last, dict) else None
                _log_event(
                    c,
                    "shot",
                    f"A shot was fired. Outcome {outcome}." if outcome else "The log does not have this.",
                    place_name=row["defender"].get("place"),
                    numbers={"outcome": outcome} if outcome else {},
                )
                fired += 1
                if last.get("outcome") in ("penetrated", "hit_no_penetration"):
                    row["defender"]["shot_today"] = True
            mount["fired_today"] = fired
        if last is not None:
            row["result"] = last
        row["resolved"] = True
        if int(row["defender"].get("Physical", {}).get("integrity", 1)) <= 0:
            row["defender"]["alive"] = False
            defender_id = row["defender"].get("id") or ""
            _log_event(
                c,
                "death",
                f"{defender_id} was no longer alive." if defender_id else "The log does not have this.",
                numbers={"alive": 0},
            )


def step_day(c: Campaign) -> None:
    if c.victory:
        return
    _ensure(c)
    _build(c)
    _research(c)
    _decide(c)
    _convert(c)
    _power(c)
    _efficiency(c)
    _mine(c)
    _refine(c)
    from sim.systems.naval import pump_ships, run_naval, sink_ships, mark_ports, log_missions
    run_naval(c)
    _move(c)
    _detect(c)
    _engage(c)
    _age_lots(c)
    _produce(c)
    _tick_conversions(c)
    _fight(c)
    pump_ships(c)
    sink_ships(c)
    mark_ports(c)
    log_missions(c)
    _take_points(c)
    _air(c)
    _raids(c)
    _capture(c)
    _arrive_and_dispatch(c)
    _imports(c)
    _hubs(c)
    _fuel_state(c)
    _quiet_attrition(c)
    _orders(c)
    _consume(c)
    c.day += 1
    _units_gone(c)
    _surrender(c)
    _victory(c)


_UNBUILT = ("fronts", "pockets", "beachheads", "lifts", "full_simulation")


def _measured_land_and_sea(cells) -> bool:
    land = sea = False
    for row in cells or []:
        if not isinstance(row, dict) or not _measured_point(row):
            continue
        if row.get("surface") == "land":
            land = True
        elif row.get("surface") == "sea":
            sea = True
    return land and sea


def prediction_refusals(cells=None) -> tuple:
    """Fronts, pockets, beachheads, lifts, and the full sim stay refused.

    Both year-states need a measured land cell and a measured sea cell.
    An empty year-state keeps the refusal. Those cells do not build the
    higher systems.
    """
    if isinstance(cells, dict) and not (
        cells and all(_measured_land_and_sea(rows) for rows in cells.values())
    ):
        return _UNBUILT
    return _UNBUILT


def write_aar(c: Campaign, path, stop: str | None = None) -> None:
    """Write the event log. Does not invent a sentence."""
    chosen = stop or ("victory" if c.victory else "limit")
    winner = [c.victory["winner"]] if c.victory and c.victory.get("winner") else None
    log = {
        "scenario_id": getattr(c, "scenario_id", None),
        "day_start": 0,
        "day_end": c.day,
        "layer": "record",
        "stop": chosen,
        "winner": winner,
        "prediction_gate_met": False,
        "refused": list(prediction_refusals(getattr(c, "cells", None))),
        "events": list(getattr(c, "events", None) or []),
        "battles": [],
        "campaigns": [],
        "days": [],
    }
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(log, indent=2))


def step_until_victory(c: Campaign, limit_days: int = 10) -> dict:
    for _ in range(limit_days):
        step_day(c)
        if c.victory:
            return c.victory
    return c.victory or {"winner": None, "reason": "limit", "day": c.day, "history": list(c.history)}
