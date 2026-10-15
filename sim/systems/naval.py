"""Sea movement and the naval fight. No country branch. No second clock."""

from __future__ import annotations

CELL_MM = 10_000_000


def _cell(c, cell_id):
    return next((row for row in c.cells if row.get("id") == cell_id), None)


def _unit(c, unit_id):
    return next((row for row in c.units if row.get("id") == unit_id), None)


def _at_war(c, left, right) -> bool:
    if not left or not right or left == right:
        return False
    for pair in c.at_war:
        if set(pair) == {left, right}:
            return True
    return False


def _seated(c, general) -> bool:
    if not str(general.get("name") or "").strip():
        return False
    if not str(general.get("source") or "").strip():
        return False
    if general.get("captured"):
        return False
    return int(general.get("from_day", 0)) <= c.day < int(general.get("to_day", 0))


def _commands(general, unit) -> bool:
    return unit.get("id") in (general.get("command") or []) and general.get("state") == unit.get("side")


def _orders(general, key):
    return (general.get("policy") or {}).get(key) or []


def _run_ordered(c, unit, cell_id) -> bool:
    for general in c.generals:
        if not _seated(c, general) or not _commands(general, unit):
            continue
        for row in _orders(general, "runs"):
            if row.get("unit_id") != unit.get("id") or row.get("cell_id") != cell_id:
                continue
            if int(row.get("issue_day", -1)) == c.day:
                return True
    return False


def _blocked(c, unit, dest) -> str:
    surface = dest.get("surface")
    if unit.get("domain") == "sea":
        if surface not in ("sea", "coast", "strait"):
            return "no_surface"
        if surface != "strait":
            return ""
        owner = dest.get("owner")
        if not owner or owner == unit.get("side") or not _at_war(c, unit.get("side"), owner):
            return ""
        if _run_ordered(c, unit, dest.get("id")):
            return ""
        return "strait_closed"
    if surface in ("sea", "strait"):
        return "no_surface"
    return ""


def _convoy_ready(c, unit) -> bool:
    cid = unit.get("convoy_id")
    group = [unit]
    if cid:
        group = [row for row in c.units if row.get("convoy_id") == cid and row.get("alive", True)] or [unit]
    return min(int(row.get("speed_mm_per_day", 0)) for row in group) >= CELL_MM


def _accept(c) -> None:
    for general in c.generals:
        if not _seated(c, general):
            continue
        for row in _orders(general, "courses"):
            if int(row.get("issue_day", -1)) != c.day:
                continue
            unit = _unit(c, row.get("unit_id"))
            if unit is None or not _commands(general, unit):
                continue
            unit["nav_course"] = list(row.get("cells") or [])
            unit["course_signed_by"] = general["id"]


def _refill(c, unit) -> None:
    if unit.get("domain") != "sea" or not unit.get("alive", True):
        return
    cell = _cell(c, unit.get("cell_id"))
    cap = int(unit.get("bunker_cap", 0))
    have = int(unit.get("bunker", 0))
    if have >= cap:
        return
    if cell and cell.get("surface") == "coast" and cell.get("owner") == unit.get("side"):
        if int(cell.get("damage_milli", 0)) < 1000:
            pool = c.factions[unit["side"]].setdefault("fuel", {})
            stock = int(pool.get("bunker", 0))
            take = min(cap - have, stock)
            unit["bunker"] = have + take
            pool["bunker"] = stock - take
            return
    for other in c.units:
        if other.get("role") != "oiler" or other.get("side") != unit.get("side"):
            continue
        if other.get("cell_id") != unit.get("cell_id") or not other.get("alive", True):
            continue
        take = min(cap - have, int(other.get("bunker", 0)))
        unit["bunker"] = have + take
        other["bunker"] = int(other.get("bunker", 0)) - take
        return


def _mines(c, unit) -> None:
    for mine in c.mines:
        if mine.get("cell_id") != unit.get("cell_id") or mine.get("owner") == unit.get("side"):
            continue
        if int(mine.get("qty", 0)) <= 0 or unit["id"] in (mine.get("hit") or []):
            continue
        body = unit.setdefault("Physical", {})
        body["integrity"] = max(0, int(body.get("integrity", 0)) - int(mine.get("damage", 0)))
        unit["integrity"] = body["integrity"]
        unit["shot_today"] = True
        mine["qty"] = int(mine["qty"]) - 1
        mine.setdefault("hit", []).append(unit["id"])


def _hop_cost(unit, dest) -> int:
    per = int(unit.get("bunker_per_cell", 0))
    km = int(dest.get("distance_km") or 1)
    return per * max(1, km)


def _step(c, unit) -> None:
    course = list(unit.get("nav_course") or [])
    if not course or not unit.get("alive", True) or unit.get("embarked_on"):
        return
    dest = _cell(c, course[0])
    if dest is None:
        unit["gate"] = "no_cell"
        return
    reason = _blocked(c, unit, dest)
    if reason:
        unit["gate"] = reason
        return
    if not _convoy_ready(c, unit):
        unit["gate"] = "convoy"
        return
    cost = _hop_cost(unit, dest) if unit.get("domain") == "sea" else 0
    if int(unit.get("bunker", 0)) < cost:
        unit["gate"] = "no_bunker"
        return
    unit["bunker"] = int(unit.get("bunker", 0)) - cost
    unit["bunker_spent"] = int(unit.get("bunker_spent", 0)) + cost
    unit["cell_id"] = dest["id"]
    unit["x_mm"] = int(dest.get("x_mm", 0))
    unit["y_mm"] = int(dest.get("y_mm", 0))
    unit["nav_course"] = course[1:]
    unit["moved"] = True
    unit["gate"] = "ran" if dest.get("surface") == "strait" else "moved"
    if unit.get("domain") == "sea":
        _mines(c, unit)


def _signed(c, key):
    for general in c.generals:
        if not _seated(c, general):
            continue
        for row in _orders(general, key):
            if int(row.get("issue_day", -1)) == c.day:
                yield general, row


def _embark(c) -> None:
    for general, row in _signed(c, "embarks"):
        unit = _unit(c, row.get("unit_id"))
        ship = _unit(c, row.get("ship_id"))
        if unit is None or ship is None or not _commands(general, unit):
            continue
        if unit.get("domain") != "ground" or unit.get("embarked_on") or not ship.get("alive", True):
            continue
        if ship.get("side") != unit.get("side") or ship.get("cell_id") != unit.get("cell_id"):
            continue
        cell = _cell(c, ship.get("cell_id"))
        if cell is None or cell.get("surface") != "coast":
            unit["gate"] = "no_coast"
            continue
        aboard = sum(1 for other in c.units if other.get("embarked_on") == ship["id"])
        if aboard >= int(ship.get("embark_cap", 0)):
            unit["gate"] = "embark_full"
            continue
        unit["embarked_on"] = ship["id"]
        unit["gate"] = "embarked"


def _beach_closed(cell) -> bool:
    if cell.get("port"):
        return False
    return int(cell.get("sea_state", 0)) >= int(cell.get("beach_close", 1000))


def _unload(c) -> None:
    for general, row in _signed(c, "unloads"):
        if row.get("ship_id") and row.get("good"):
            _unload_cargo(c, general, row)
            continue
        unit = _unit(c, row.get("unit_id"))
        if unit is None or not _commands(general, unit) or not unit.get("embarked_on"):
            continue
        ship = _unit(c, unit.get("embarked_on"))
        cell = _cell(c, ship.get("cell_id") if ship else None)
        if cell is None or cell.get("surface") != "coast":
            unit["gate"] = "no_coast"
            continue
        if _beach_closed(cell):
            unit["gate"] = "beach_closed"
            continue
        weight = int(unit.get("weight_t", 1))
        used = int(cell.get("throughput_used", 0))
        if used + weight > int(cell.get("throughput_t", 0)):
            unit["gate"] = "beach_full"
            continue
        cell["throughput_used"] = used + weight
        unit["embarked_on"] = None
        unit["cell_id"] = cell["id"]
        unit["x_mm"] = int(cell.get("x_mm", 0))
        unit["y_mm"] = int(cell.get("y_mm", 0))
        if cell.get("continent"):
            unit["continent"] = cell["continent"]
        unit["gate"] = "landed"


def _unload_cargo(c, general, row) -> None:
    ship = _unit(c, row.get("ship_id"))
    if ship is None or not _commands(general, ship):
        return
    cell = _cell(c, ship.get("cell_id"))
    if cell is None or cell.get("surface") != "coast":
        ship["gate"] = "no_coast"
        return
    if _beach_closed(cell):
        ship["gate"] = "beach_closed"
        return
    good = row["good"]
    have = int((ship.get("cargo") or {}).get(good, 0))
    room = int(cell.get("throughput_t", 0)) - int(cell.get("throughput_used", 0))
    take = min(have, max(0, room))
    if take <= 0:
        ship["gate"] = "beach_full"
        return
    ship.setdefault("cargo", {})[good] = have - take
    cell["throughput_used"] = int(cell.get("throughput_used", 0)) + take
    stock = cell.setdefault("stock", {}).setdefault(ship["side"], {})
    stock[good] = int(stock.get(good, 0)) + take
    ship["tons_delivered"] = int(ship.get("tons_delivered", 0)) + take


def _lay(c) -> None:
    for general, row in _signed(c, "lays"):
        unit = _unit(c, row.get("unit_id"))
        if unit is None or not _commands(general, unit) or not unit.get("alive", True):
            continue
        cell = _cell(c, unit.get("cell_id"))
        if cell is None or cell.get("surface") not in ("sea", "coast", "strait"):
            continue
        mount = next((item for item in unit.get("WeaponMount") or [] if item.get("kind") == "mine"), None)
        if mount is None:
            continue
        ammo = mount["ammo"][0]
        qty = int(row.get("qty", 1))
        if int(ammo.get("qty", 0)) < qty:
            continue
        ammo["qty"] = int(ammo["qty"]) - qty
        c.mines.append({
            "id": f"laid-{unit['id']}-{c.day}",
            "cell_id": unit["cell_id"],
            "owner": unit["side"],
            "qty": qty,
            "damage": int(row.get("damage", ammo.get("blast", 1))),
        })


def _sweep(c) -> None:
    for general, row in _signed(c, "sweeps"):
        unit = _unit(c, row.get("unit_id"))
        if unit is None or not _commands(general, unit):
            continue
        mount = next((item for item in unit.get("WeaponMount") or [] if item.get("kind") == "minesweep"), None)
        if mount is None or int(mount["ammo"][0].get("qty", 0)) <= 0:
            continue
        hostile = [
            mine for mine in c.mines
            if mine.get("cell_id") == unit.get("cell_id") and mine.get("owner") != unit.get("side")
            and int(mine.get("qty", 0)) > 0
        ]
        if not hostile:
            continue
        hostile[0]["qty"] = int(hostile[0]["qty"]) - 1
        mount["ammo"][0]["qty"] = int(mount["ammo"][0]["qty"]) - 1


def _take(c) -> None:
    for general, row in _signed(c, "takes"):
        cell = _cell(c, row.get("cell_id"))
        if cell is None:
            continue
        holders = [
            unit for unit in c.units
            if unit.get("alive", True) and not unit.get("embarked_on")
            and unit.get("cell_id") == cell["id"] and _commands(general, unit)
        ]
        if not holders:
            continue
        enemy = any(
            unit.get("alive", True) and unit.get("cell_id") == cell["id"]
            and unit.get("side") != general.get("state")
            for unit in c.units
        )
        if enemy:
            continue
        cell["owner"] = general["state"]
        if cell.get("surface") == "coast":
            cell["damage_milli"] = int(cell.get("capture_damage_milli", 1000))


def _can_fly(c, wing) -> bool:
    cost = int(wing.get("sortie_fuel", 0))
    if cost <= 0:
        return False
    grade = wing.get("fuel_grade") or "avgas"
    pool = c.factions[wing["side"]].setdefault("fuel", {})
    return int(pool.get(grade, 0)) >= cost


def _spend_sortie(c, wing) -> None:
    cost = int(wing.get("sortie_fuel", 0))
    grade = wing.get("fuel_grade") or "avgas"
    pool = c.factions[wing["side"]]["fuel"]
    pool[grade] = int(pool.get(grade, 0)) - cost
    wing["fuel_spent"] = {grade: cost}
    wing["sortie_flown"] = True


def _sorties(c) -> None:
    carriers = [row for row in c.units if row.get("alive", True) and row.get("role") == "carrier"]
    wings = sorted(
        [row for row in c.units if row.get("domain") == "air" and row.get("alive", True)],
        key=lambda row: row["id"],
    )
    for wing in wings:
        wing["sortie_flown"] = False
        if not _can_fly(c, wing):
            continue
        cell = _cell(c, wing.get("cell_id"))
        if cell and cell.get("airfield") and cell.get("surface") == "land" and int(cell.get("damage_milli", 0)) < 1000:
            _spend_sortie(c, wing)
            continue
        for deck in sorted(carriers, key=lambda row: row["id"]):
            if deck.get("side") != wing.get("side") or int(deck.get("deck_sorties", 0)) <= 0:
                continue
            same = deck.get("cell_id") == wing.get("cell_id")
            dx = int(deck.get("x_mm", 0)) - int(wing.get("x_mm", 0))
            dy = int(deck.get("y_mm", 0)) - int(wing.get("y_mm", 0))
            in_range = dx * dx + dy * dy <= int(deck.get("deck_range_mm", 0)) ** 2
            if not same and not in_range:
                continue
            deck["deck_sorties"] = int(deck["deck_sorties"]) - 1
            _spend_sortie(c, wing)
            break


def _lift_open(c) -> None:
    for link in c.links:
        if link.get("kind") != "lift":
            continue
        ends = set(link.get("cells") or [])
        side = link.get("side")
        present = any(
            unit.get("alive", True) and unit.get("domain") == "sea" and unit.get("side") == side
            and unit.get("cell_id") in ends
            for unit in c.units
        )
        fleet = (c.fleets or {}).get(link.get("fleet_id") or "", {})
        link["open"] = bool(present and int(fleet.get("count", 0)) > 0)


def mark_screens(c) -> None:
    groups: dict[tuple, list] = {}
    for unit in c.units:
        if not unit.get("alive", True) or not unit.get("cell_id"):
            continue
        groups.setdefault((unit.get("side"), unit.get("cell_id")), []).append(unit)
    for (side, cell_id), group in groups.items():
        merchants = sorted((row for row in group if row.get("role") == "merchant"), key=lambda row: row["id"])
        escorts = sorted((row for row in group if row.get("role") == "escort"), key=lambda row: row["id"])
        slots = sum(int(row.get("screen_slots", 1)) for row in escorts)
        covered = {row["id"] for row in merchants[:slots]}
        for row in merchants:
            row["screened"] = row["id"] in covered
        cell = _cell(c, cell_id)
        if cell is None or not merchants:
            continue
        cell["escort_ratio_milli"] = len(escorts) * 1000 // len(merchants)


def run_naval(c) -> None:
    for unit in c.units:
        unit["shot_today"] = False
        unit["bunker_spent"] = 0
        unit["tons_delivered"] = 0
        unit["moved"] = False
    for cell in c.cells:
        cell["throughput_used"] = 0
    _take(c)
    for unit in c.units:
        _refill(c, unit)
    _accept(c)
    _embark(c)
    _lay(c)
    for unit in sorted(c.units, key=lambda row: row.get("id", "")):
        _step(c, unit)
    _sweep(c)
    _unload(c)
    mark_screens(c)
    _sorties(c)
    _lift_open(c)


def pump_ships(c) -> None:
    for unit in c.units:
        if unit.get("domain") != "sea" or not unit.get("alive", True):
            continue
        gain = int(unit.get("pump_per_day", 0))
        if unit.get("shot_today") or int(unit.get("crew", 0)) <= 0 or gain <= 0:
            unit["pumped"] = False
            continue
        body = unit.setdefault("Physical", {})
        cap = int(unit.get("integrity_max", body.get("integrity", 0)))
        body["integrity"] = min(cap, int(body.get("integrity", 0)) + gain)
        unit["integrity"] = body["integrity"]
        unit["pumped"] = True


def sink_ships(c) -> None:
    for unit in c.units:
        if unit.get("domain") != "sea":
            continue
        integrity = int((unit.get("Physical") or {}).get("integrity", 1))
        if integrity > 0 and unit.get("alive", True):
            continue
        unit["alive"] = False
        unit["cause"] = "sunk"
        unit["cargo"] = {}
        for other in c.units:
            if other.get("embarked_on") == unit["id"]:
                other["alive"] = False
                other["cause"] = "sunk"


def mark_ports(c) -> None:
    for unit in c.units:
        if unit.get("domain") != "port":
            continue
        integrity = int((unit.get("Physical") or {}).get("integrity", 1))
        if integrity > 0 and unit.get("alive", True):
            continue
        cell = _cell(c, unit.get("cell_id"))
        if cell is not None:
            cell["damage_milli"] = 1000


def log_missions(c) -> None:
    rows = list(getattr(c, "mission_days", []) or [])
    for unit in c.units:
        if unit.get("domain") == "air" and unit.get("sortie_flown"):
            rows.append({
                "id": f"air-{unit['id']}-{c.day}",
                "day": c.day,
                "domain": "air",
                "owner": unit.get("side"),
                "fuel_spent": dict(unit.get("fuel_spent") or {}),
                "crews_lost": 0,
                "hulls_sunk": [],
                "units_sunk": [],
                "tons_loaded": 0,
                "tons_delivered": 0,
                "bunker_end": 0,
            })
            continue
        if unit.get("domain") != "sea":
            continue
        sunk = unit.get("cause") == "sunk" and not unit.get("alive", True)
        if not unit.get("bunker_spent") and not unit.get("tons_delivered") and not sunk and not unit.get("moved"):
            continue
        passengers = [other["id"] for other in c.units if other.get("embarked_on") == unit["id"] and other.get("cause") == "sunk"]
        rows.append({
            "id": f"sea-{unit['id']}-{c.day}",
            "day": c.day,
            "domain": "sea",
            "owner": unit.get("side"),
            "fuel_spent": {"bunker": int(unit.get("bunker_spent", 0))},
            "crews_lost": int(unit.get("crew", 0)) if sunk else 0,
            "hulls_sunk": [unit["id"]] if sunk else [],
            "units_sunk": passengers,
            "tons_loaded": 0,
            "tons_delivered": int(unit.get("tons_delivered", 0)),
            "bunker_end": int(unit.get("bunker", 0)),
        })
    c.mission_days = rows


def weather_milli(c, unit) -> int:
    cell = _cell(c, (unit or {}).get("cell_id"))
    if not cell:
        return 1000
    if "weather_milli" in cell:
        return max(0, int(cell["weather_milli"]))
    if "sea_state" in cell:
        return max(0, 1000 - int(cell["sea_state"]))
    return 1000


def screen_target(attacker, defender, units):
    if defender.get("role") == "escort":
        return defender
    if defender.get("role") != "merchant" or not defender.get("screened"):
        return defender
    escorts = sorted(
        [
            row for row in units
            if row.get("alive", True) and row.get("role") == "escort"
            and row.get("side") == defender.get("side") and row.get("cell_id") == defender.get("cell_id")
            and row.get("id") != attacker.get("id")
        ],
        key=lambda row: row.get("id", ""),
    )
    return escorts[0] if escorts else defender


def mount_may_fire(attacker, mount, defender=None) -> bool:
    kind = mount.get("kind", "gun")
    if attacker.get("posture") == "submerged" and kind == "gun":
        return False
    if attacker.get("domain") == "air" and not attacker.get("sortie_flown"):
        return False
    if kind in ("mine", "minesweep"):
        return False
    if defender is None:
        return True
    if kind == "depth_charge":
        return (
            defender.get("posture") == "submerged"
            and bool(defender.get("cell_id"))
            and defender.get("cell_id") == attacker.get("cell_id")
        )
    if kind == "torpedo":
        return defender.get("domain") == "sea"
    return True
