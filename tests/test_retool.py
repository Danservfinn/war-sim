"""A seated leader can retool a plant that already exists. Nobody else can."""

from sim.campaign.step import Campaign, step_day


def _plant(cap: int = 4) -> dict:
    return {
        "id": "guns",
        "owner": "za",
        "continent": "africa",
        "strain_milli": 0,
        "dud_base": 10,
        "skilled_labor": 2,
        "power_mw": 10,
        "tools": 2,
        "civilian_share_milli": 0,
        "capabilities": ["rifle"],
        "node_id": "yard",
        "labor": {"chemist": 2},
        "lines": [{
            "id": "line",
            "output": "rifle",
            "power_mw_need": 1,
            "tools_need": 1,
            "skilled_need": 1,
            "damage_milli": 0,
            "daily_cap": cap,
            "powder_local": True,
        }],
    }


def _leader(from_day: int = 0, to_day: int = 10, source: str = "fixture") -> dict:
    return {
        "id": "ldr",
        "name": "Fixture Head",
        "state": "za",
        "from_day": from_day,
        "to_day": to_day,
        "source": source,
        "policy": {
            "conversions": [{
                "plant_id": "guns",
                "output": "shell",
                "days": 2,
                "capacity_milli": 1000,
                "issue_day": 0,
                "skill": "chemist",
                "inputs": {"steel": 1},
            }],
            "tactical": [{
                "unit_id": "u1",
                "posture": "attack",
                "issue_day": 0,
            }],
        },
    }


def _campaign(leader, cap: int = 4) -> Campaign:
    return Campaign(
        day=0,
        nodes=[{
            "id": "pit", "continent": "africa", "good": "steel", "stock_t": 20,
            "nameplate_t": 0, "reserve_t": 0,
        }],
        refiners=[],
        plants=[_plant(cap)],
        lots=[],
        fleets={"trucks": {"count": 1}},
        links=[{
            "id": "rail_1", "kind": "rail", "from_node": "pit", "to_node": "yard",
            "open": True, "capacity_t": 10, "cargo_id": "none", "fleet_id": "trucks",
            "payload_t": 1, "payload_l": 1, "distance_km": 0,
            "continent": "africa", "from_continent": "africa", "to_continent": "africa",
        }],
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
        units=[{"id": "u1", "side": "za", "alive": True, "posture": "hold", "foot": True,
                "x_mm": 0, "y_mm": 0, "speed_mm_per_day": 0, "equipment": {}}],
        engagements=[],
        research=[{"id": "gps", "days_left": 1, "unlocked": False}],
        leaders=[] if leader is None else [leader],
    )


def test_no_leader_choice_does_not_create_the_munition():
    c = _campaign(None)
    for _ in range(3):
        step_day(c)
    assert "shell" not in c.plants[0]["capabilities"]
    assert all(lot["ammo_id"] != "shell" for lot in c.lots)
    assert c.research[0]["unlocked"] is False


def test_seated_leader_retools_existing_capacity_after_the_projected_days():
    c = _campaign(_leader())
    step_day(c)
    assert "shell" not in c.plants[0]["capabilities"]
    assert c.plants[0]["military_out"] == 0
    step_day(c)
    assert "shell" not in c.plants[0]["capabilities"]
    step_day(c)
    assert "shell" in c.plants[0]["capabilities"]
    assert any(lot["ammo_id"] == "shell" and lot["qty"] == 4 for lot in c.lots)
    assert c.research[0]["unlocked"] is False
    assert c.units[0]["posture"] == "hold"


def test_leader_out_of_office_cannot_order_the_conversion_or_the_posture():
    c = _campaign(_leader(from_day=5, to_day=9))
    for _ in range(3):
        step_day(c)
    assert "shell" not in c.plants[0]["capabilities"]
    assert c.units[0]["posture"] == "hold"


def test_empty_source_is_not_a_leader():
    c = _campaign(_leader(source=""))
    for _ in range(3):
        step_day(c)
    assert "shell" not in c.plants[0]["capabilities"]


def test_a_plant_with_no_capacity_cannot_be_repurposed():
    c = _campaign(_leader(), cap=0)
    for _ in range(3):
        step_day(c)
    assert "shell" not in c.plants[0]["capabilities"]
