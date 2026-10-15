"""The six holes that change a naval war. No navy branch."""

from sim.campaign.step import Campaign, step_day


CELL = 10_000_000


def _fac(side="eu"):
    return {
        "cohesion": 50, "manpower": 10, "trainees": 0, "training_cap_per_day": 0,
        "food_t": 10, "food_burn_t": 0, "water_t": 0, "water_burn_t": 0,
        "fuel": {"bunker": 0, "avgas": 0}, "loss_hold_days": 9, "cohesion_loss_per_day": 0,
        "stockpile": {"rifle": 1}, "victory_points": 3,
        "continent": "europe" if side == "eu" else "africa",
    }


def _ship(unit_id="ship", side="eu", cell="home", bunker=5):
    return {
        "id": unit_id, "side": side, "domain": "sea", "alive": True, "role": "ship",
        "cell_id": cell, "x_mm": 0, "y_mm": 0, "speed_mm_per_day": 20_000_000,
        "bunker": bunker, "bunker_cap": 8, "bunker_per_cell": 1,
        "integrity": 40, "integrity_max": 40, "crew": 12, "pump_per_day": 0,
        "sensor_range_mm": 0, "cargo": {}, "embark_cap": 1,
        "Physical": {
            "integrity": 40,
            "signature": {"visual": 1000, "submerged": 0},
            "armor": [{"aspect": "front", "thickness_mm": 0, "ke_mod": 1000}],
        },
        "WeaponMount": [],
    }


def _gun(kind="gun", qty=1, rounds=1):
    return {
        "mount_id": kind, "kind": kind, "rounds_per_day": rounds,
        "ammo": [{"ammo_id": kind, "qty": qty, "penetration_mm": 80, "blast": 6,
                  "warhead": "ke", "guidance": "none"}],
        "range_bands": [{"max_m": 30000, "accuracy": 1000, "penetration_mm": 80, "blast": 6}],
    }


def _boot(unit_id="boot", cell="home", weight=1):
    return {
        "id": unit_id, "side": "eu", "domain": "ground", "alive": True, "foot": True,
        "cell_id": cell, "x_mm": 0, "y_mm": 0, "speed_mm_per_day": 0, "weight_t": weight,
        "cargo": {"steel": 3}, "equipment": {}, "continent": "europe",
    }


def _general(policy, command):
    return {
        "id": "gen", "name": "Fixture Admiral", "source": "fixture", "state": "eu",
        "from_day": 0, "to_day": 9, "captured": False, "command": command, "policy": policy,
    }


def _war(units, cells, generals=None, **kw):
    return Campaign(
        day=0, nodes=[], plants=[], lots=[], fleets=kw.pop("fleets", {}),
        links=kw.pop("links", []), in_transit=[], imports=[],
        factions={"eu": _fac("eu"), "af": _fac("af")},
        victory_rules=[], history=[], victory=None, stocks=kw.pop("stocks", {}),
        units=units, engagements=[], contacts=[],
        cells=cells, mines=kw.pop("mines", []), generals=generals or [],
        at_war=[["eu", "af"]],
        continent_stocks={"europe": {"steel": 0}, "africa": {"steel": 0}},
        leaders=kw.pop("leaders", []),
        **kw,
    )


def _coast(cell_id="home", owner="eu", port=True, **extra):
    row = {"id": cell_id, "surface": "coast", "x_mm": 0, "y_mm": 0, "owner": owner,
           "continent": "europe", "port": port, "throughput_t": 10, "sea_state": 0,
           "beach_close": 500}
    row.update(extra)
    return row


def test_general_embarks_a_unit_and_the_head_of_state_cannot():
    ship = _ship()
    boot = _boot()
    gen = _general({"embarks": [{"unit_id": "boot", "ship_id": "ship", "issue_day": 0}]}, ["boot", "ship"])
    c = _war([ship, boot], [_coast()], [gen])
    step_day(c)
    assert boot["embarked_on"] == "ship"
    boot["embarked_on"] = None
    c2 = _war([_ship(), _boot()], [_coast()], [])
    c2.leaders = [{
        "id": "ldr", "name": "Fixture Head", "source": "fixture", "state": "eu",
        "from_day": 0, "to_day": 9,
        "policy": {"embarks": [{"unit_id": "boot", "ship_id": "ship", "issue_day": 0}]},
    }]
    step_day(c2)
    assert c2.units[1].get("embarked_on") in (None, "")


def test_embarked_unit_cannot_shoot_and_is_not_a_target():
    ship = _ship()
    boot = _boot()
    boot["WeaponMount"] = [_gun()]
    boot["Crew"] = {"billets": [{"role": "gunner", "count": 1, "skill": 100}]}
    boot["sensor_range_mm"] = 80_000_000
    enemy = _ship("enemy", "af", "home")
    enemy["sensor_range_mm"] = 80_000_000
    enemy["Crew"] = {"billets": [{"role": "gunner", "count": 1, "skill": 100}]}
    enemy["WeaponMount"] = [_gun()]
    gen = _general({"embarks": [{"unit_id": "boot", "ship_id": "ship", "issue_day": 0}]}, ["boot", "ship"])
    c = _war([ship, boot, enemy], [_coast()], [gen])
    step_day(c)
    assert not any(row["target"] == "boot" or row["observer"] == "boot" for row in c.contacts)
    assert boot["WeaponMount"][0]["ammo"][0]["qty"] == 1


def test_unload_lands_the_unit_and_does_not_credit_the_far_stock():
    ship = _ship(cell="far")
    boot = _boot(cell="far")
    boot["embarked_on"] = "ship"
    far = _coast("far", owner="eu", port=True, continent="africa", x_mm=CELL)
    gen = _general({"unloads": [{"unit_id": "boot", "issue_day": 0}]}, ["boot", "ship"])
    c = _war([ship, boot], [_coast(), far], [gen])
    step_day(c)
    assert boot.get("embarked_on") in (None, "")
    assert boot["cell_id"] == "far"
    assert boot["continent"] == "africa"
    assert boot["cargo"]["steel"] == 3
    assert c.continent_stocks["africa"]["steel"] == 0


def test_beach_throughput_and_rough_seas():
    ship = _ship(cell="beach")
    one = _boot("one", "beach")
    two = _boot("two", "beach")
    one["embarked_on"] = "ship"
    two["embarked_on"] = "ship"
    beach = _coast("beach", port=False, throughput_t=1, sea_state=0)
    gen = _general({
        "unloads": [{"unit_id": "one", "issue_day": 0}, {"unit_id": "two", "issue_day": 0}],
    }, ["one", "two", "ship"])
    c = _war([ship, one, two], [beach], [gen])
    step_day(c)
    landed = [row for row in (one, two) if not row.get("embarked_on")]
    assert len(landed) == 1
    assert any(row.get("gate") == "beach_full" for row in (one, two))
    storm = _coast("storm", port=False, sea_state=500, beach_close=500)
    boot = _boot("boot", "storm")
    boot["embarked_on"] = "ship"
    ship2 = _ship(cell="storm")
    gen2 = _general({"unloads": [{"unit_id": "boot", "issue_day": 0}]}, ["boot", "ship"])
    c2 = _war([ship2, boot], [storm], [gen2])
    step_day(c2)
    assert boot["embarked_on"] == "ship"
    assert boot["gate"] == "beach_closed"
    port = _coast("port", port=True, sea_state=500, beach_close=500)
    boot3 = _boot("boot", "port")
    boot3["embarked_on"] = "ship"
    ship3 = _ship(cell="port")
    gen3 = _general({"unloads": [{"unit_id": "boot", "issue_day": 0}]}, ["boot", "ship"])
    c3 = _war([ship3, boot3], [port], [gen3])
    step_day(c3)
    assert boot3.get("embarked_on") in (None, "")


def test_ship_cargo_feeds_the_beachhead_not_the_continent_pile():
    ship = _ship()
    ship["cargo"] = {"steel": 4}
    cell = _coast(throughput_t=2)
    gen = _general({"unloads": [{"ship_id": "ship", "good": "steel", "issue_day": 0}]}, ["ship"])
    c = _war([ship], [cell], [gen])
    step_day(c)
    assert cell["stock"]["eu"]["steel"] == 2
    assert ship["cargo"]["steel"] == 2
    assert c.continent_stocks["europe"]["steel"] == 0
    assert c.continent_stocks["africa"]["steel"] == 0


def test_lift_link_needs_a_living_ship_and_a_fleet_and_still_moves_no_goods_across():
    ship = _ship(cell="far")
    link = {
        "id": "lift", "kind": "lift", "side": "eu", "cells": ["home", "far"],
        "fleet_id": "hulls", "payload_t": 5, "payload_l": 1, "cargo_id": "steel",
        "distance_km": 10, "speed_km_per_day": 10, "continent": "europe",
        "from_continent": "europe", "to_continent": "europe",
    }
    c = _war([ship], [_coast(), _coast("far")], fleets={"hulls": {"count": 1}}, links=[link], stocks={"steel": 5})
    step_day(c)
    assert link["open"] is True
    assert c.in_transit
    closed = dict(link)
    elsewhere = {"id": "elsewhere", "surface": "sea", "x_mm": 3 * CELL, "y_mm": 0}
    c2 = _war([_ship(cell="elsewhere")], [_coast(), _coast("far"), elsewhere],
              fleets={"hulls": {"count": 1}}, links=[closed], stocks={"steel": 5})
    step_day(c2)
    assert closed["open"] is False
    assert c2.in_transit == []
    empty = dict(link)
    c3 = _war([ship], [_coast(), _coast("far")], fleets={"hulls": {"count": 0}}, links=[empty], stocks={"steel": 5})
    step_day(c3)
    assert empty["open"] is False
    abroad = dict(link)
    abroad["to_continent"] = "africa"
    c4 = _war([_ship(cell="far")], [_coast(), _coast("far")], fleets={"hulls": {"count": 1}},
              links=[abroad], stocks={"steel": 5})
    step_day(c4)
    assert c4.continent_stocks["africa"]["steel"] == 0
    assert c4.in_transit == []


def test_longer_cell_costs_more_bunker_and_the_four_names_are_data():
    ship = _ship(bunker=2)
    far = {"id": "far", "surface": "sea", "x_mm": CELL, "y_mm": 0, "owner": None, "distance_km": 3}
    gen = _general({"courses": [{"unit_id": "ship", "cells": ["far"], "issue_day": 0}]}, ["ship"])
    c = _war([ship], [_coast(), far], [gen])
    step_day(c)
    assert ship["cell_id"] == "home"
    assert ship["bunker"] == 2
    assert ship["gate"] == "no_bunker"
    short = dict(far)
    short["distance_km"] = 2
    ship2 = _ship(bunker=2)
    gen2 = _general({"courses": [{"unit_id": "ship", "cells": ["far"], "issue_day": 0}]}, ["ship"])
    c2 = _war([ship2], [_coast(), short], [gen2])
    step_day(c2)
    assert ship2["cell_id"] == "far"
    assert ship2["bunker"] == 0
    import yaml
    named = yaml.safe_load(open("catalogs/straits.yaml"))
    ids = {row["id"] for row in named["links"]}
    assert ids >= {"suez", "gibraltar", "bab_el_mandeb", "cape"}
    by_id = {row["id"]: row for row in named["links"]}
    assert int(by_id["cape"]["distance_km"]) > int(by_id["suez"]["distance_km"])


def test_a_gun_in_the_cell_shoots_with_no_sensor_and_a_coast_gun_covers_the_strait():
    ship = _ship(cell="strait")
    ship["x_mm"] = CELL
    ship["integrity"] = 80
    ship["Physical"]["integrity"] = 80
    gunboat = _ship("gunboat", "af", "strait")
    gunboat["x_mm"] = CELL
    gunboat["sensor_range_mm"] = 0
    gunboat["Crew"] = {"billets": [{"role": "gunner", "count": 1, "skill": 100}]}
    gunboat["WeaponMount"] = [_gun()]
    cells = [
        _coast(),
        {"id": "strait", "surface": "strait", "x_mm": CELL, "y_mm": 0, "owner": "af"},
    ]
    c = _war([ship, gunboat], cells, [])
    step_day(c)
    assert ship["Physical"]["integrity"] < 80
    hidden = _ship("sub", "eu", "strait")
    hidden["posture"] = "submerged"
    hidden["x_mm"] = CELL
    hunter = _ship("hunter", "af", "strait")
    hunter["x_mm"] = CELL
    hunter["sees_submerged"] = False
    hunter["WeaponMount"] = [_gun()]
    c2 = _war([hidden, hunter], cells, [])
    step_day(c2)
    assert not any(row["target"] == "sub" for row in c2.contacts)
    battery = _boot("battery", "shore")
    battery["side"] = "af"
    battery["sensor_range_mm"] = 0
    battery["Crew"] = {"billets": [{"role": "gunner", "count": 1, "skill": 100}]}
    battery["WeaponMount"] = [_gun()]
    shore = {"id": "shore", "surface": "land", "x_mm": 0, "y_mm": 0, "owner": "af", "covers": ["strait"]}
    prey = _ship(cell="strait")
    prey["x_mm"] = CELL
    prey["integrity"] = 80
    prey["Physical"]["integrity"] = 80
    c3 = _war([battery, prey], [shore, cells[1]], [])
    step_day(c3)
    assert prey["Physical"]["integrity"] < 80


def test_patrol_finds_a_ship_in_the_cell_and_a_storm_hides_one_at_range():
    watcher = _ship("watcher", "eu", "home")
    watcher["sensor_range_mm"] = 0
    watcher["posture"] = "patrol"
    other = _ship("other", "af", "home")
    c = _war([watcher, other], [_coast()], [])
    step_day(c)
    assert any(row["target"] == "other" for row in c.contacts)
    idle = _ship("idle", "eu", "home")
    idle["sensor_range_mm"] = 0
    c2 = _war([idle, _ship("other", "af", "home")], [_coast()], [])
    step_day(c2)
    assert not any(row["target"] == "other" for row in c2.contacts)
    seeker = _ship("seeker", "eu", "home")
    seeker["sensor_range_mm"] = 80_000_000
    far = _ship("far", "af", "away")
    far["x_mm"] = CELL
    storm = _coast()
    storm["sea_state"] = 1000
    away = {"id": "away", "surface": "sea", "x_mm": CELL, "y_mm": 0, "sea_state": 1000}
    c3 = _war([seeker, far], [storm, away], [])
    step_day(c3)
    assert not any(row["target"] == "far" for row in c3.contacts)


def test_a_missed_contact_becomes_last_known_and_does_not_shoot():
    seeker = _ship("seeker", "eu", "home")
    seeker["sensor_range_mm"] = 80_000_000
    far = _ship("far", "af", "home")
    far["integrity"] = 80
    far["Physical"]["integrity"] = 80
    c = _war([seeker, far], [_coast()], [])
    step_day(c)
    seeker["WeaponMount"] = [_gun()]
    seeker["Crew"] = {"billets": [{"role": "gunner", "count": 1, "skill": 100}]}
    far["x_mm"] = 500 * CELL
    far["cell_id"] = "away"
    step_day(c)
    assert any(row["target"] == "far" and row["quality"] == "last_known" for row in c.contacts)
    assert far["Physical"]["integrity"] == 80


def test_storm_cuts_the_shot_and_calm_does_not():
    def fight(sea_state):
        attacker = _ship("attacker", "af", "home")
        attacker["Crew"] = {"billets": [{"role": "gunner", "count": 1, "skill": 100}]}
        attacker["WeaponMount"] = [_gun()]
        target = _ship()
        target["integrity"] = 80
        target["Physical"]["integrity"] = 80
        cell = _coast(owner="af", sea_state=sea_state)
        c = _war([attacker, target], [cell], [])
        step_day(c)
        return target["Physical"]["integrity"]
    assert fight(1000) == 80
    assert fight(0) < 80


def test_a_ship_can_lay_and_sweep_and_a_depth_charge_needs_the_same_cell():
    layer = _ship()
    layer["WeaponMount"] = [_gun("mine", qty=2)]
    gen = _general({"lays": [{"unit_id": "ship", "qty": 1, "issue_day": 0}]}, ["ship"])
    c = _war([layer], [_coast()], [gen])
    step_day(c)
    assert any(row.get("owner") == "eu" and row.get("qty") == 1 for row in c.mines)
    assert layer["WeaponMount"][0]["ammo"][0]["qty"] == 1
    sweeper = _ship("sweeper", "eu", "far")
    sweeper["WeaponMount"] = [_gun("minesweep", qty=1)]
    mines = [
        {"id": "hostile", "cell_id": "far", "owner": "af", "qty": 2, "damage": 7},
        {"id": "own", "cell_id": "far", "owner": "eu", "qty": 2, "damage": 7},
    ]
    gen2 = _general({"sweeps": [{"unit_id": "sweeper", "issue_day": 0}]}, ["sweeper"])
    c2 = _war([sweeper], [_coast(), {"id": "far", "surface": "sea", "x_mm": CELL, "y_mm": 0}], [gen2], mines=mines)
    step_day(c2)
    assert mines[0]["qty"] == 1
    assert mines[1]["qty"] == 2
    hunter = _ship("hunter", "eu", "home")
    hunter["sees_submerged"] = True
    hunter["sensor_range_mm"] = 80_000_000
    hunter["WeaponMount"] = [_gun("depth_charge")]
    hunter["Crew"] = {"billets": [{"role": "gunner", "count": 1, "skill": 100}]}
    sub = _ship("sub", "af", "far")
    sub["posture"] = "submerged"
    sub["x_mm"] = CELL
    sub["Physical"]["signature"]["submerged"] = 1000
    c3 = _war([hunter, sub], [_coast(), {"id": "far", "surface": "sea", "x_mm": CELL, "y_mm": 0}], [])
    step_day(c3)
    assert hunter["WeaponMount"][0]["ammo"][0]["qty"] == 1
    sub["cell_id"] = "home"
    sub["x_mm"] = 0
    sub["Physical"]["integrity"] = 40
    hunter["WeaponMount"][0]["ammo"][0]["qty"] = 1
    step_day(c3)
    assert hunter["WeaponMount"][0]["ammo"][0]["qty"] == 0
    assert sub["Physical"]["integrity"] < 40


def test_a_torpedo_does_not_shoot_at_land():
    boat = _ship()
    boat["sensor_range_mm"] = 80_000_000
    boat["WeaponMount"] = [_gun("torpedo")]
    boat["Crew"] = {"billets": [{"role": "gunner", "count": 1, "skill": 100}]}
    boot = _boot()
    boot["side"] = "af"
    c = _war([boat, boot], [_coast()], [])
    step_day(c)
    assert boat["WeaponMount"][0]["ammo"][0]["qty"] == 1


def test_one_escort_does_not_screen_every_merchant():
    m1 = _ship("m1", "eu", "far")
    m2 = _ship("m2", "eu", "far")
    m1["role"] = "merchant"
    m2["role"] = "merchant"
    m1["x_mm"] = CELL
    m2["x_mm"] = CELL
    escort = _ship("escort", "eu", "far")
    escort["role"] = "escort"
    escort["x_mm"] = CELL
    escort["detectable"] = False
    attacker = _ship("attacker", "af", "far")
    attacker["x_mm"] = CELL
    attacker["sensor_range_mm"] = 80_000_000
    attacker["Crew"] = {"billets": [{"role": "gunner", "count": 1, "skill": 100}]}
    attacker["WeaponMount"] = [_gun(rounds=2, qty=2)]
    cell = {"id": "far", "surface": "sea", "x_mm": CELL, "y_mm": 0}
    c = _war([m1, m2, escort, attacker], [cell], [])
    step_day(c)
    assert cell["escort_ratio_milli"] == 500
    assert m1["screened"] is True
    assert m2["screened"] is False
    defenders = {row["defender"]["id"] for row in c.engagements}
    assert "escort" in defenders
    assert "m2" in defenders
    assert "m1" not in defenders


def test_a_bombed_port_does_not_refill_and_a_captured_port_starts_damaged():
    port = _ship("port", "af", "home")
    port["domain"] = "port"
    port["integrity"] = 5
    port["Physical"]["integrity"] = 5
    attacker = _ship("attacker", "eu", "home")
    attacker["sensor_range_mm"] = 80_000_000
    attacker["Crew"] = {"billets": [{"role": "gunner", "count": 1, "skill": 100}]}
    attacker["WeaponMount"] = [_gun()]
    cell = _coast(owner="af")
    c = _war([port, attacker], [cell], [])
    step_day(c)
    assert cell["damage_milli"] == 1000
    friend = _ship("friend", "af", "home", bunker=0)
    c.units.append(friend)
    c.factions["af"]["fuel"]["bunker"] = 9
    step_day(c)
    assert friend["bunker"] == 0
    taken = _coast("haven", owner="af")
    boot = _boot("boot", "haven")
    gen = _general({"takes": [{"cell_id": "haven", "issue_day": 0}]}, ["boot"])
    c2 = _war([boot], [taken], [gen])
    step_day(c2)
    assert taken["owner"] == "eu"
    assert taken["damage_milli"] == 1000


def test_a_yard_builds_a_hull_and_nobody_else_can():
    plant = {
        "id": "yard", "owner": "eu", "side": "eu", "continent": "europe", "strain_milli": 0,
        "dud_base": 0, "skilled_labor": 2, "power_mw": 10, "tools": 2, "civilian_share_milli": 0,
        "capabilities": [], "node_id": "yard", "labor": {"fitter": 2},
        "lines": [{"id": "line", "output": "none", "power_mw_need": 1, "tools_need": 1,
                   "skilled_need": 1, "damage_milli": 0, "daily_cap": 0, "powder_local": True}],
    }
    leader = {
        "id": "ldr", "name": "Fixture Head", "source": "fixture", "state": "eu",
        "from_day": 0, "to_day": 9,
        "policy": {"hulls": [{
            "plant_id": "yard", "issue_day": 0, "days": 1, "skill": "fitter",
            "inputs": {"steel": 5},
            "hull": {"id": "newhull", "domain": "sea", "role": "ship"},
        }]},
    }
    c = Campaign(
        day=0,
        nodes=[{"id": "pit", "continent": "europe", "good": "steel", "stock_t": 5, "nameplate_t": 0, "reserve_t": 0}],
        plants=[plant], lots=[], fleets={"trucks": {"count": 1}},
        links=[{
            "id": "rail_1", "kind": "rail", "from_node": "pit", "to_node": "yard",
            "open": True, "capacity_t": 10, "cargo_id": "none", "fleet_id": "trucks",
            "payload_t": 1, "payload_l": 1, "distance_km": 0,
            "continent": "europe", "from_continent": "europe", "to_continent": "europe",
        }],
        in_transit=[], imports=[],
        factions={"eu": _fac(), "af": _fac("af")},
        victory_rules=[], history=[], victory=None, stocks={},
        units=[{"id": "u1", "side": "eu", "alive": True, "foot": True, "x_mm": 0, "y_mm": 0,
                "speed_mm_per_day": 0, "equipment": {}}],
        engagements=[], contacts=[], cells=[], mines=[], generals=[], at_war=[],
        continent_stocks={"europe": {}, "africa": {}}, leaders=[leader],
    )
    step_day(c)
    assert not any(row["id"] == "newhull" for row in c.units)
    step_day(c)
    built = next(row for row in c.units if row["id"] == "newhull")
    assert built["domain"] == "sea"
    assert built["side"] == "eu"
    assert c.nodes[0]["stock_t"] == 0
    assert c.continent_stocks["europe"].get("steel", 0) == 0


def test_repair_clears_a_port_only_while_an_engineer_is_there():
    cell = _coast()
    cell["damage_milli"] = 1000
    leader = {
        "id": "ldr", "name": "Fixture Head", "source": "fixture", "state": "eu",
        "from_day": 0, "to_day": 9,
        "policy": {"repairs": [{"cell_id": "home", "days": 1, "issue_day": 0}]},
    }
    c = _war([_boot()], [cell], [], leaders=[leader])
    step_day(c)
    assert cell["damage_milli"] == 1000
    engineer = _boot("eng")
    engineer["role"] = "engineer"
    c2 = _war([engineer], [_coast(damage_milli=1000)], [], leaders=[leader])
    step_day(c2)
    assert c2.cells[0]["damage_milli"] == 0


def test_a_sortie_spends_fuel_and_can_sink_and_a_free_modifier_is_not_a_mission():
    wing = {
        "id": "wing", "side": "eu", "domain": "air", "alive": True, "cell_id": "far",
        "x_mm": CELL, "y_mm": 0, "speed_mm_per_day": 0, "foot": True, "equipment": {},
        "sortie_fuel": 1, "fuel_grade": "avgas", "sensor_range_mm": 80_000_000,
        "Crew": {"billets": [{"role": "gunner", "count": 1, "skill": 100}]},
        "WeaponMount": [_gun()],
    }
    deck = _ship("deck", "eu", "far")
    deck["role"] = "carrier"
    deck["x_mm"] = CELL
    deck["deck_sorties"] = 1
    deck["deck_range_mm"] = CELL
    enemy = _ship("enemy", "af", "far")
    enemy["x_mm"] = CELL
    enemy["integrity"] = 20
    enemy["Physical"]["integrity"] = 20
    cell = {"id": "far", "surface": "sea", "x_mm": CELL, "y_mm": 0}
    c = _war([wing, deck, enemy], [cell], [])
    c.factions["eu"]["fuel"]["avgas"] = 3
    step_day(c)
    assert wing["sortie_flown"] is True
    assert c.factions["eu"]["fuel"]["avgas"] == 2
    assert enemy["Physical"]["integrity"] < 20
    assert any(row["domain"] == "air" and row["fuel_spent"].get("avgas") == 1 for row in c.mission_days)
    dry = dict(wing)
    dry["id"] = "dry"
    deck2 = _ship("deck2", "eu", "far")
    deck2["role"] = "carrier"
    deck2["x_mm"] = CELL
    deck2["deck_sorties"] = 1
    c2 = _war([dry, deck2], [cell], [])
    step_day(c2)
    assert dry["sortie_flown"] is False
    assert deck2["deck_sorties"] == 1
    cap = dict(wing)
    cap["id"] = "cap"
    cap["posture"] = "cap"
    cap["cell_id"] = "field"
    field = {"id": "field", "surface": "land", "x_mm": 0, "y_mm": 0, "airfield": True, "owner": "eu"}
    c3 = _war([cap], [field], [])
    c3.factions["eu"]["fuel"]["avgas"] = 4
    step_day(c3)
    assert cap["sortie_flown"] is True
    assert c3.factions["eu"]["fuel"]["avgas"] == 3
    assert c3.engagements == []
    c4 = _war([_ship()], [_coast()], [])
    c4.air_missions = [{"kind": "cas", "side": "eu", "target": "ship", "attack_milli": 150}]
    step_day(c4)
    assert not any(row.get("domain") == "air" for row in getattr(c4, "mission_days", []))
