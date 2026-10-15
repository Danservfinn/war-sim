"""Continent wall, refining, one clock, victory. No tech bailout."""

from sim.campaign.step import Campaign, step_day
from sim.systems.combat import resolve_shot


def _war():
    return Campaign(
        day=0,
        nodes=[{"id": "pit", "continent": "africa", "good": "ore_iron", "nameplate_t": 10,
                "reserve_t": 100, "stock_t": 0}],
        refiners=[{"id": "smelter", "continent": "africa", "consumes": "ore_iron",
                   "makes": "steel", "ratio_milli": 500, "daily_cap": 4}],
        plants=[{"id": "guns", "continent": "africa", "strain_milli": 0, "dud_base": 10,
                 "skilled_labor": 2, "power_mw": 10, "tools": 2, "civilian_share_milli": 0,
                 "input_good": "steel", "input_per": 1,
                 "lines": [{"id": "rifles", "power_mw_need": 1, "tools_need": 1, "skilled_need": 1,
                            "damage_milli": 0, "daily_cap": 5, "powder_local": True}]}],
        lots=[],
        fleets={"trucks": {"count": 10}},
        links=[{"id": "haul", "continent": "africa", "from_continent": "africa", "to_continent": "africa",
                "fleet_id": "trucks", "payload_t": 5, "payload_l": 1000, "empties_milli": 0,
                "port_slots_t": 0, "distance_km": 100, "speed_km_per_day": 100,
                "self_consume_milli": 0, "cargo_id": "steel"}],
        in_transit=[],
        imports=[{"good": "gps_kit", "from_continent": "europe", "to_continent": "africa",
                  "embargo_day": None, "schedule": [{"day": 1, "qty_t": 9}], "received_t": 0}],
        factions={"side_a": {"cohesion": 50, "manpower": 10, "trainees": 0, "training_cap_per_day": 0,
                             "food_t": 10, "food_burn_t": 0, "water_t": 0, "water_burn_t": 0,
                             "fuel": {}, "loss_hold_days": 0, "cohesion_loss_per_day": 0,
                             "continent": "africa", "stockpile": {"gps_kit": 2}}},
        victory_rules=[],
        history=[],
        victory=None,
        stocks={"steel": 0},
        units=[{"id": "u1", "side": "side_a", "continent": "africa", "equipment": {"rifle": 1},
                "ammo": {"ball": 3}, "alive": True}],
        engagements=[],
    )


def test_cross_continent_import_is_refused():
    c = _war()
    step_day(c)
    step_day(c)
    assert c.imports[0]["received_t"] == 0
    assert c.stocks.get("gps_kit", 0) == 0


def test_ore_is_not_steel():
    c = _war()
    step_day(c)
    assert c.nodes[0]["last_output_t"] == 10
    assert c.nodes[0]["stock_t"] == 2  # 10 mined, 8 eaten by the smelter to make 4
    assert c.refiners[0]["out_t"] == 4  # 10 ore * 500/1000, capped at 4
    assert c.plants[0]["military_out"] == 0  # no node, so the pile is not a plant input
    assert c.continent_stocks["africa"]["steel"] == 4
    assert c.stocks.get("steel", 0) == 0


def test_sahara_haul_binds_without_an_import():
    c = _war()
    c.stocks["steel"] = 5000
    c.links = [
        {"id": "cape", "continent": "africa", "from_continent": "africa", "to_continent": "africa",
         "fleet_id": "trucks", "payload_t": 50, "payload_l": 100000, "empties_milli": 0,
         "port_slots_t": 0, "distance_km": 100, "speed_km_per_day": 100, "self_consume_milli": 0,
         "cargo_id": "steel"},
        {"id": "sahara", "continent": "africa", "from_continent": "africa", "to_continent": "africa",
         "fleet_id": "trucks", "payload_t": 5, "payload_l": 1000, "empties_milli": 400,
         "port_slots_t": 0, "distance_km": 2000, "speed_km_per_day": 100, "self_consume_milli": 0,
         "cargo_id": "steel"},
    ]
    step_day(c)
    sent = [row for row in c.in_transit if row["link_id"] == "sahara"]
    assert sent and sent[0]["qty_t"] == 30  # 10 trucks * 5 t * 600/1000


def test_one_clock_resolves_the_shot_and_spends_the_round():
    c = _war()
    c.engagements = [{
        "day": 0,
        "attacker": {"id": "u1", "WeaponMount": [{
            "mount_id": "gun",
            "ammo": [{"ammo_id": "ball", "qty": 4, "warhead": "ke", "penetration_mm": 20,
                      "guidance": "none", "blast": 5}],
            "range_bands": [{"max_m": 1000, "accuracy": 1000}],
        }], "Crew": {"billets": [{"role": "gunner", "count": 1, "skill": 80}]}},
        "defender": {"id": "u2", "side": "side_b", "alive": True,
                     "Physical": {"integrity": 10, "signature": {"visual": 1000},
                                  "armor": [{"aspect": "front", "thickness_mm": 0, "ke_mod": 1000}]}},
        "distance_m": 100,
        "weather": 1000,
        "aspect": "front",
    }]
    step_day(c)
    assert c.engagements[0]["resolved"] is True
    assert c.engagements[0]["attacker"]["WeaponMount"][0]["ammo"][0]["qty"] == 3


def test_dead_units_do_not_end_the_war():
    c = _war()
    c.units[0]["alive"] = False
    c.research = [{"id": "gps", "days_left": 1, "unlocked": False}]
    step_day(c)
    assert c.victory is None
    assert c.research[0]["unlocked"] is False


def test_cited_african_plants_cannot_replace_a_modern_kit():
    import yaml
    from pathlib import Path
    rows = yaml.safe_load(Path("catalogs/africa_capacity.yaml").read_text())["plants"]
    caps = {row["id"]: row for row in rows}
    assert caps["rdm_boksburg"]["daily_cap"] == 277
    assert caps["dicon_kaduna"]["powder_local"] is False
    c = _war()
    c.plants[0]["lines"][0]["daily_cap"] = caps["dicon_kaduna"]["daily_cap"]
    c.plants[0]["lines"][0]["powder_local"] = caps["dicon_kaduna"]["powder_local"]
    c.plants[0]["lines"][0]["good"] = "gps_kit"
    step_day(c)
    assert c.plants[0]["military_out"] == 0
    assert c.factions["side_a"]["stockpile"]["gps_kit"] == 2
    c = _war()
    c.plants[0]["lines"][0]["good"] = "gps_kit"
    c.plants[0]["lines"][0]["powder_local"] = False
    c.plants[0]["input_good"] = "electronics"
    step_day(c)
    assert c.plants[0]["military_out"] == 0
    assert c.factions["side_a"]["stockpile"]["gps_kit"] == 2
