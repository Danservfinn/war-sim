"""Naval fight. A strait is a battle if the general orders the run. No navy branch."""

from sim.campaign.step import Campaign, step_day
from sim.systems.combat import resolve_shot


CELL = 10_000_000


def _fac():
    return {
        "cohesion": 50, "manpower": 10, "trainees": 0, "training_cap_per_day": 0,
        "food_t": 10, "food_burn_t": 0, "water_t": 0, "water_burn_t": 0,
        "fuel": {"bunker": 0}, "loss_hold_days": 9, "cohesion_loss_per_day": 0,
        "stockpile": {"rifle": 1}, "victory_points": 3, "continent": "europe",
    }


def _ship(unit_id="ship", side="eu", cell="home", speed=20_000_000, bunker=5):
    return {
        "id": unit_id, "side": side, "domain": "sea", "alive": True, "role": "ship",
        "cell_id": cell, "x_mm": 0, "y_mm": 0, "speed_mm_per_day": speed,
        "bunker": bunker, "bunker_cap": 8, "bunker_per_cell": 1,
        "integrity": 40, "integrity_max": 40, "crew": 12, "pump_per_day": 0,
        "sensor_range_mm": 80_000_000, "cargo": {"steel": 3},
        "Physical": {
            "integrity": 40,
            "signature": {"visual": 1000, "submerged": 0},
            "armor": [{"aspect": "front", "thickness_mm": 0, "ke_mod": 1000}],
        },
        "WeaponMount": [],
    }


def _gun(mount_id="gun", kind="gun", qty=1):
    return {
        "mount_id": mount_id, "kind": kind, "rounds_per_day": 1,
        "ammo": [{
            "ammo_id": kind, "qty": qty, "penetration_mm": 80, "blast": 6,
            "warhead": "ke", "guidance": "none",
        }],
        "range_bands": [{"max_m": 30000, "accuracy": 1000, "penetration_mm": 80, "blast": 6}],
    }


def _general(runs=None, courses=None, command=None, source="fixture"):
    return {
        "id": "gen", "name": "Fixture Admiral", "source": source, "state": "eu",
        "from_day": 0, "to_day": 5, "captured": False,
        "command": command or ["ship"],
        "policy": {"courses": courses or [], "runs": runs or []},
    }


def _war(units, cells, generals=None, mines=None, at_war=None, fuel=0):
    eu = _fac()
    eu["fuel"]["bunker"] = fuel
    af = _fac()
    af["continent"] = "africa"
    return Campaign(
        day=0, nodes=[], plants=[], lots=[], fleets={}, links=[], in_transit=[], imports=[],
        factions={"eu": eu, "af": af},
        victory_rules=[], history=[], victory=None, stocks={},
        units=units, engagements=[], contacts=[],
        cells=cells, mines=mines or [], generals=generals or [],
        at_war=at_war or [["eu", "af"]],
        continent_stocks={"europe": {"steel": 0}, "africa": {"steel": 0}},
    )


def _cells():
    return [
        {"id": "home", "surface": "coast", "x_mm": 0, "y_mm": 0, "owner": "eu"},
        {"id": "strait", "surface": "strait", "x_mm": CELL, "y_mm": 0, "owner": "af"},
        {"id": "far", "surface": "sea", "x_mm": 2 * CELL, "y_mm": 0, "owner": None},
        {"id": "land", "surface": "land", "x_mm": 3 * CELL, "y_mm": 0, "owner": "af", "airfield": True},
    ]


def _course(cells, unit_id="ship"):
    return [{"unit_id": unit_id, "cells": cells, "issue_day": 0}]


def _run(cell_id="strait", unit_id="ship"):
    return [{"unit_id": unit_id, "cell_id": cell_id, "issue_day": 0}]


def test_hostile_strait_rejects_the_course_without_a_general_run():
    ship = _ship()
    c = _war([ship], _cells(), [_general(courses=_course(["strait"]))])
    step_day(c)
    assert c.units[0]["cell_id"] == "home"
    assert c.units[0]["gate"] == "strait_closed"
    assert c.continent_stocks["africa"]["steel"] == 0


def test_head_of_state_cannot_order_the_run():
    ship = _ship()
    c = _war([ship], _cells(), [_general(courses=_course(["strait"]))])
    c.leaders = [{
        "id": "ldr", "name": "Fixture Head", "source": "fixture", "state": "eu",
        "from_day": 0, "to_day": 5,
        "policy": {"runs": _run(), "tactical": []},
    }]
    step_day(c)
    assert c.units[0]["cell_id"] == "home"


def test_general_run_enters_the_strait_and_the_guns_shoot():
    ship = _ship()
    ship["integrity"] = 200
    ship["Physical"]["integrity"] = 200
    gunboat = _ship("gunboat", "af", "strait", bunker=4)
    gunboat["x_mm"] = CELL
    gunboat["Crew"] = {"billets": [{"role": "gunner", "count": 1, "skill": 100}]}
    gunboat["WeaponMount"] = [_gun()]
    c = _war(
        [ship, gunboat], _cells(),
        [_general(courses=_course(["strait"]), runs=_run())],
    )
    step_day(c)
    assert ship["cell_id"] == "strait"
    assert ship["gate"] == "ran"
    assert ship["Physical"]["integrity"] < 200
    assert any(row.get("attacker", {}).get("id") == "gunboat" for row in c.engagements)
    assert c.continent_stocks["africa"]["steel"] == 0


def test_ship_cannot_enter_land_and_ground_cannot_enter_sea():
    ship = _ship()
    boot = {"id": "boot", "side": "eu", "domain": "ground", "alive": True, "foot": True,
            "cell_id": "home", "x_mm": 0, "y_mm": 0, "speed_mm_per_day": 0, "equipment": {}}
    c = _war([ship, boot], _cells(), [_general(courses=_course(["land"]))])
    c.generals[0]["command"] = ["ship", "boot"]
    c.generals[0]["policy"]["courses"].append({"unit_id": "boot", "cells": ["far"], "issue_day": 0})
    step_day(c)
    assert ship["cell_id"] == "home"
    assert ship["gate"] == "no_surface"
    assert boot["cell_id"] == "home"


def test_submerged_hides_drops_signature_and_cannot_fire_the_deck_gun():
    sub = _ship("sub", "eu", "home")
    sub["posture"] = "submerged"
    sub["WeaponMount"] = [_gun("deck", "gun"), _gun("fish", "torpedo")]
    target = _ship("tgt", "af", "home")
    target["detectable"] = True
    hunter = _ship("hunter", "af", "home")
    hunter["sees_submerged"] = False
    c = _war([sub, target, hunter], _cells(), [])
    step_day(c)
    assert not any(row["target"] == "sub" for row in c.contacts)
    assert sub["WeaponMount"][0]["ammo"][0]["qty"] == 1
    shooter = {
        "Physical": {"integrity": 10, "signature": {"visual": 1000},
                     "armor": [{"aspect": "front", "thickness_mm": 0, "ke_mod": 1000}]},
        "Crew": {"billets": [{"role": "gunner", "count": 1, "skill": 100}]},
        "WeaponMount": [_gun()],
    }
    hidden = {
        "posture": "submerged",
        "Physical": {"integrity": 10, "signature": {"visual": 1000, "submerged": 0},
                     "armor": [{"aspect": "front", "thickness_mm": 0, "ke_mod": 1000}]},
    }

    class _Zero:
        def roll(self, n):
            return 0

    missed = resolve_shot(shooter, hidden, 1000, 1000, "front", _Zero())
    assert missed["outcome"] == "miss"


def test_torpedo_and_depth_charge_need_a_contact():
    sub = _ship("sub", "eu", "far")
    sub["posture"] = "submerged"
    sub["sees_submerged"] = True
    sub["x_mm"] = 2 * CELL
    sub["WeaponMount"] = [_gun("fish", "torpedo"), _gun("deck", "gun")]
    prey = _ship("prey", "af", "far")
    prey["x_mm"] = 2 * CELL
    prey["posture"] = "submerged"
    lone = _ship("lone", "eu", "home")
    lone["WeaponMount"] = [_gun("ash", "depth_charge")]
    c = _war([sub, prey, lone], _cells(), [])
    step_day(c)
    assert sub["WeaponMount"][1]["ammo"][0]["qty"] == 1
    assert sub["WeaponMount"][0]["ammo"][0]["qty"] == 0
    assert lone["WeaponMount"][0]["ammo"][0]["qty"] == 1


def test_carrier_deck_is_the_only_field_at_sea():
    wing = {"id": "wing", "side": "eu", "domain": "air", "alive": True, "cell_id": "far",
            "x_mm": 2 * CELL, "y_mm": 0, "speed_mm_per_day": 0, "foot": True, "equipment": {},
            "sortie_fuel": 1, "fuel_grade": "avgas"}
    deck = _ship("deck", "eu", "far")
    deck["role"] = "carrier"
    deck["x_mm"] = 2 * CELL
    deck["deck_sorties"] = 1
    deck["deck_range_mm"] = CELL
    c = _war([wing, deck], _cells(), [])
    c.factions["eu"]["fuel"]["avgas"] = 1
    step_day(c)
    assert wing["sortie_flown"] is True
    assert deck["deck_sorties"] == 0
    wing2 = dict(wing)
    wing2["id"] = "wing2"
    c2 = _war([wing2], _cells(), [])
    step_day(c2)
    assert wing2["sortie_flown"] is False


def test_escort_takes_the_shot_meant_for_the_merchant():
    merchant = _ship("merchant", "eu", "far")
    merchant["role"] = "merchant"
    merchant["x_mm"] = 2 * CELL
    merchant["integrity"] = 80
    merchant["Physical"]["integrity"] = 80
    escort = _ship("escort", "eu", "far")
    escort["role"] = "escort"
    escort["x_mm"] = 2 * CELL
    escort["detectable"] = False
    escort["integrity"] = 80
    escort["Physical"]["integrity"] = 80
    attacker = _ship("attacker", "af", "far")
    attacker["x_mm"] = 2 * CELL
    attacker["Crew"] = {"billets": [{"role": "gunner", "count": 1, "skill": 100}]}
    attacker["WeaponMount"] = [_gun()]
    attacker["WeaponMount"][0]["rounds_per_day"] = 2
    attacker["WeaponMount"][0]["ammo"][0]["qty"] = 2
    c = _war([merchant, escort, attacker], _cells(), [])
    step_day(c)
    assert merchant["Physical"]["integrity"] == 80
    assert escort["Physical"]["integrity"] < 80


def test_convoy_moves_at_the_slowest_hull():
    fast = _ship("fast", speed=30_000_000)
    slow = _ship("slow", speed=5_000_000)
    fast["convoy_id"] = "cv"
    slow["convoy_id"] = "cv"
    gen = _general(courses=[
        {"unit_id": "fast", "cells": ["far"], "issue_day": 0},
        {"unit_id": "slow", "cells": ["far"], "issue_day": 0},
    ], command=["fast", "slow"])
    c = _war([fast, slow], _cells(), [gen], at_war=[])
    step_day(c)
    assert fast["cell_id"] == "home"
    assert slow["cell_id"] == "home"
    fast["speed_mm_per_day"] = 20_000_000
    slow["speed_mm_per_day"] = 20_000_000
    step_day(c)
    assert fast["cell_id"] == "far"
    assert slow["cell_id"] == "far"


def test_sea_mine_persists_and_own_mines_do_not_hit():
    ship = _ship(bunker=5)
    ship["integrity"] = 30
    ship["Physical"]["integrity"] = 30
    mines = [
        {"id": "m1", "cell_id": "far", "owner": "af", "qty": 2, "damage": 7},
        {"id": "m2", "cell_id": "far", "owner": "eu", "qty": 2, "damage": 9},
    ]
    gen = _general(courses=_course(["far"]))
    c = _war([ship], _cells(), [gen], mines=mines, at_war=[])
    step_day(c)
    assert ship["cell_id"] == "far"
    assert ship["Physical"]["integrity"] == 23
    assert mines[0]["qty"] == 1
    assert mines[1]["qty"] == 2


def test_pumping_repairs_a_ship_that_was_not_hit():
    ship = _ship()
    ship["Physical"]["integrity"] = 10
    ship["integrity"] = 10
    ship["pump_per_day"] = 4
    c = _war([ship], _cells(), [])
    step_day(c)
    assert ship["Physical"]["integrity"] == 14
    assert ship["pumped"] is True


def test_sinking_deletes_embarked_units_and_does_not_credit_the_far_stock():
    ship = _ship(bunker=5)
    ship["integrity"] = 5
    ship["Physical"]["integrity"] = 5
    boot = {"id": "boot", "side": "eu", "domain": "ground", "alive": True, "foot": True,
            "embarked_on": "ship", "cell_id": "home", "x_mm": 0, "y_mm": 0,
            "speed_mm_per_day": 0, "equipment": {}}
    mines = [{"id": "m1", "cell_id": "far", "owner": "af", "qty": 1, "damage": 5}]
    gen = _general(courses=_course(["far"]))
    c = _war([ship, boot], _cells(), [gen], mines=mines, at_war=[])
    step_day(c)
    assert ship["alive"] is False
    assert ship["cause"] == "sunk"
    assert ship["cargo"] == {}
    assert boot["alive"] is False
    assert boot["cause"] == "sunk"
    assert c.continent_stocks["africa"]["steel"] == 0


def test_hostile_port_does_not_refill_bunker():
    ship = _ship(cell="land", bunker=0)
    ship["cell_id"] = "strait"
    cells = _cells()
    cells[1]["surface"] = "coast"
    cells[1]["owner"] = "af"
    c = _war([ship], cells, [], fuel=9)
    step_day(c)
    assert ship["bunker"] == 0
    assert c.factions["eu"]["fuel"]["bunker"] == 9
    ship["cell_id"] = "home"
    step_day(c)
    assert ship["bunker"] == 8
    assert c.factions["eu"]["fuel"]["bunker"] == 1
