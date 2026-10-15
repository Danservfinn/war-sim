"""Defects that distort a day. No new formula."""

from sim.campaign.step import Campaign, step_day
from sim.systems.combat import resolve_shot


def _plant(**extra) -> dict:
    row = {
        "id": "guns",
        "owner": "za",
        "continent": "africa",
        "strain_milli": 0,
        "dud_base": 0,
        "skilled_labor": 2,
        "power_mw": 10,
        "tools": 2,
        "civilian_share_milli": 0,
        "capabilities": ["rifle"],
        "input_good": "steel",
        "input_per": 1,
        "lines": [{
            "id": "line",
            "output": "rifle",
            "power_mw_need": 1,
            "tools_need": 1,
            "skilled_need": 1,
            "damage_milli": 0,
            "daily_cap": 4,
            "powder_local": True,
        }],
    }
    row.update(extra)
    return row


def _bare(**kwargs) -> Campaign:
    base = dict(
        day=0,
        nodes=[],
        refiners=[],
        plants=[_plant()],
        lots=[],
        fleets={},
        links=[],
        in_transit=[],
        imports=[],
        factions={"za": {
            "cohesion": 50, "manpower": 10, "trainees": 0, "training_cap_per_day": 0,
            "food_t": 10, "food_burn_t": 0, "water_t": 0, "water_burn_t": 0,
            "fuel": {}, "loss_hold_days": 0, "cohesion_loss_per_day": 0, "stockpile": {},
        }},
        victory_rules=[],
        history=[],
        victory=None,
        stocks={},
        units=[],
        engagements=[],
        leaders=[],
        continent_stocks={"africa": {"steel": 10}, "europe": {"steel": 10}},
    )
    base.update(kwargs)
    return Campaign(**base)


def test_plant_without_a_node_does_not_draw_the_continent_pile():
    c = _bare()
    step_day(c)
    assert c.continent_stocks["africa"]["steel"] == 10
    assert c.plants[0]["military_out"] == 0


def test_plant_draws_only_a_connected_node_on_the_same_continent():
    c = _bare(
        plants=[_plant(node_id="yard")],
        nodes=[
            {"id": "pit", "continent": "africa", "good": "steel", "stock_t": 5, "nameplate_t": 0, "reserve_t": 0},
            {"id": "yard", "continent": "africa", "good": "none", "stock_t": 0, "nameplate_t": 0, "reserve_t": 0},
            {"id": "ruhr", "continent": "europe", "good": "steel", "stock_t": 9, "nameplate_t": 0, "reserve_t": 0},
        ],
        links=[{
            "id": "road", "kind": "road", "from_node": "pit", "to_node": "yard",
            "open": True, "capacity_t": 8, "cargo_id": "none",
            "fleet_id": "trucks", "payload_t": 1, "payload_l": 1, "distance_km": 0,
        }],
        fleets={"trucks": {"count": 1}},
    )
    step_day(c)
    assert c.nodes[0]["stock_t"] == 1
    assert c.continent_stocks["africa"]["steel"] == 10
    assert c.continent_stocks["europe"]["steel"] == 10
    assert c.nodes[2]["stock_t"] == 9
    assert c.plants[0]["military_out"] == 4


def test_a_foreign_node_does_not_feed_the_plant():
    c = _bare(
        plants=[_plant(node_id="yard")],
        nodes=[
            {"id": "yard", "continent": "africa", "good": "none", "stock_t": 0, "nameplate_t": 0, "reserve_t": 0},
            {"id": "ruhr", "continent": "europe", "good": "steel", "stock_t": 9, "nameplate_t": 0, "reserve_t": 0},
        ],
        links=[{
            "id": "road", "kind": "road", "from_node": "ruhr", "to_node": "yard",
            "open": True, "capacity_t": 8, "cargo_id": "none",
            "fleet_id": "trucks", "payload_t": 1, "payload_l": 1, "distance_km": 0,
        }],
        fleets={"trucks": {"count": 1}},
    )
    step_day(c)
    assert c.plants[0]["military_out"] == 0
    assert c.nodes[1]["stock_t"] == 9
    assert c.continent_stocks["europe"]["steel"] == 10


class _Roll:
    def roll(self, n: int) -> int:
        return 500


def _shot(guidance: str, illumination=None) -> dict:
    attacker = {
        "WeaponMount": [{
            "mount_id": "gun",
            "range_bands": [{"max_m": 1000, "accuracy": 1000, "penetration_mm": 40, "blast": 10}],
            "ammo": [{"ammo_id": "ap", "qty": 1, "guidance": guidance, "penetration_mm": 40, "blast": 10}],
        }],
        "Crew": {"billets": [{"role": "gunner", "count": 1, "skill": 100}]},
    }
    if illumination:
        attacker["illumination"] = illumination
    defender = {
        "Physical": {
            "integrity": 40,
            "armor": [{"aspect": "front", "thickness_mm": 1, "ke_mod": 1000, "heat_mod": 1000}],
            "signature": {"visual": 1000},
        },
    }
    return resolve_shot(attacker, defender, 100, 1000, "front", _Roll())


def test_optical_shot_takes_the_flat_night_cut_once():
    optical = _shot("optical")
    assert optical["outcome"] == "miss"
    assert optical["hit_chance"] == 1000 * 8 // 24


def test_illumination_keeps_the_optical_shot_at_daylight():
    shot = _shot("optical", illumination="flare")
    assert shot["outcome"] == "penetrated"


def test_a_non_optical_shot_is_not_cut():
    shot = _shot("none")
    assert shot["outcome"] == "penetrated"


def test_the_clock_still_advances_one_day():
    c = _bare(plants=[])
    step_day(c)
    assert c.day == 1


def test_head_of_state_does_not_set_a_land_posture():
    c = _bare(
        plants=[],
        units=[{"id": "u1", "side": "za", "alive": True, "posture": "hold", "foot": True,
                "x_mm": 0, "y_mm": 0, "speed_mm_per_day": 0, "equipment": {}}],
        leaders=[{
            "id": "ldr", "name": "Fixture Head", "state": "za",
            "from_day": 0, "to_day": 10, "source": "fixture",
            "policy": {"tactical": [{"unit_id": "u1", "posture": "attack", "issue_day": 0}]},
        }],
    )
    step_day(c)
    assert c.units[0]["posture"] == "hold"


def test_seated_general_on_the_command_list_sets_the_posture():
    c = _bare(
        plants=[],
        units=[{"id": "u1", "side": "za", "alive": True, "posture": "hold", "foot": True,
                "x_mm": 0, "y_mm": 0, "speed_mm_per_day": 0, "equipment": {}}],
        generals=[{
            "id": "gen", "name": "Fixture General", "state": "za", "office": "general",
            "from_day": 0, "to_day": 10, "source": "fixture", "captured": False,
            "command": ["u1"],
            "policy": {"tactical": [{"unit_id": "u1", "posture": "attack", "issue_day": 0}]},
        }],
    )
    step_day(c)
    assert c.units[0]["posture"] == "attack"


def test_cas_does_not_write_air_attack_milli():
    c = _bare(
        plants=[],
        units=[{"id": "div", "side": "za", "alive": True, "posture": "hold", "foot": True,
                "equipment": {}}],
        air_missions=[{"kind": "cas", "side": "za", "target": "div", "attack_milli": 150}],
    )
    step_day(c)
    assert "air_attack_milli" not in c.units[0]
