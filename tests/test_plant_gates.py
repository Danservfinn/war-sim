"""A new munition needs reachable stock, the named skill, and a live road or rail. Every day."""

from sim.campaign.step import Campaign, step_day


def _plant(labor=None):
    return {
        "id": "guns",
        "owner": "za",
        "continent": "africa",
        "node_id": "yard",
        "strain_milli": 0,
        "dud_base": 10,
        "skilled_labor": 50,
        "labor": {"machinist": 4} if labor is None else labor,
        "power_mw": 10,
        "tools": 2,
        "civilian_share_milli": 0,
        "capabilities": ["rifle"],
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


def _leader():
    return {
        "id": "ldr",
        "name": "Fixture Head",
        "state": "za",
        "from_day": 0,
        "to_day": 10,
        "source": "fixture",
        "policy": {"conversions": [{
            "plant_id": "guns",
            "output": "shell",
            "days": 2,
            "capacity_milli": 1000,
            "issue_day": 0,
            "skill": "chemist",
            "inputs": {"steel": 1},
        }]},
    }


def _war(nodes, links, labor=None, stocks=None):
    return Campaign(
        day=0,
        nodes=nodes,
        refiners=[],
        plants=[_plant(labor)],
        lots=[],
        fleets={"trucks": {"count": 1}},
        links=links,
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
        stocks=stocks or {},
        units=[{"id": "u1", "side": "za", "alive": True, "posture": "hold", "foot": True,
                "x_mm": 0, "y_mm": 0, "speed_mm_per_day": 0, "equipment": {}}],
        engagements=[],
        research=[{"id": "gps", "days_left": 1, "unlocked": False}],
        leaders=[_leader()],
        continent_stocks={"africa": {"steel": 1000}},
    )


def _rail(open_=True, capacity=10):
    return {
        "id": "line_1",
        "kind": "rail",
        "from_node": "pit",
        "to_node": "yard",
        "open": open_,
        "capacity_t": capacity,
        "cargo_id": "none",
        "fleet_id": "trucks",
        "payload_t": 1,
        "payload_l": 1,
        "distance_km": 0,
        "continent": "africa",
        "from_continent": "africa",
        "to_continent": "africa",
    }


def _pit(stock=20):
    return {
        "id": "pit",
        "continent": "africa",
        "good": "steel",
        "stock_t": stock,
        "nameplate_t": 0,
        "reserve_t": 0,
    }


def test_no_road_or_rail_refuses_the_munition():
    c = _war([_pit()], [], labor={"chemist": 2})
    for _ in range(3):
        step_day(c)
    assert "shell" not in c.plants[0]["capabilities"]
    assert c.conversions == []
    assert c.research[0]["unlocked"] is False


def test_stock_on_the_continent_does_not_reach_a_plant_with_no_link():
    c = _war([], [_rail()], labor={"chemist": 2})
    for _ in range(3):
        step_day(c)
    assert "shell" not in c.plants[0]["capabilities"]


def test_wrong_skill_refuses_even_with_a_rail_and_steel():
    c = _war([_pit()], [_rail()], labor={"machinist": 9})
    for _ in range(3):
        step_day(c)
    assert "shell" not in c.plants[0]["capabilities"]
    assert c.plants[0]["labor"]["machinist"] == 9


def test_open_rail_named_skill_and_reachable_steel_retool():
    c = _war([_pit()], [_rail()], labor={"chemist": 2})
    step_day(c)
    assert "shell" not in c.plants[0]["capabilities"]
    step_day(c)
    step_day(c)
    assert "shell" in c.plants[0]["capabilities"]
    assert any(lot["ammo_id"] == "shell" and lot["qty"] == 4 for lot in c.lots)
    assert c.research[0]["unlocked"] is False


def test_a_road_is_enough_when_the_rail_is_shut():
    road = _rail()
    road["id"] = "road_1"
    road["kind"] = "road"
    c = _war([_pit()], [road, _rail(open_=False)], labor={"chemist": 1})
    for _ in range(3):
        step_day(c)
    assert "shell" in c.plants[0]["capabilities"]


def test_rail_capacity_caps_the_day_the_network_is_open():
    c = _war([_pit(20)], [_rail(capacity=2)], labor={"chemist": 2})
    for _ in range(3):
        step_day(c)
    shells = [lot for lot in c.lots if lot["ammo_id"] == "shell"]
    assert shells[-1]["qty"] == 2
    assert c.nodes[0]["stock_t"] == 18


def test_a_cut_network_pauses_tooling_and_stops_later_output():
    c = _war([_pit()], [_rail()], labor={"chemist": 2})
    step_day(c)
    assert c.conversions[0]["days_left"] == 1
    c.links[0]["open"] = False
    step_day(c)
    assert c.conversions[0]["days_left"] == 1
    assert c.plants[0]["gate"] == "no_access"
    c.links[0]["open"] = True
    step_day(c)
    step_day(c)
    assert "shell" in c.plants[0]["capabilities"]
    made = sum(lot["qty"] for lot in c.lots if lot["ammo_id"] == "shell")
    c.links[0]["open"] = False
    step_day(c)
    assert sum(lot["qty"] for lot in c.lots if lot["ammo_id"] == "shell") == made
    assert c.plants[0]["military_out"] == 0
    assert c.plants[0]["gate"] == "no_access"
