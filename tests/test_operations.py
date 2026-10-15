"""A campaign is an accepted operation. A head of state does not open one."""

from sim.campaign.step import Campaign, step_day


def _campaign():
    return Campaign(
        day=0,
        nodes=[],
        plants=[],
        lots=[],
        fleets={},
        links=[],
        in_transit=[],
        imports=[],
        factions={"a": {
            "cohesion": 50, "manpower": 1, "trainees": 0, "training_cap_per_day": 0,
            "food_t": 1, "food_burn_t": 0, "water_t": 0, "water_burn_t": 0,
            "fuel": {}, "loss_hold_days": 0, "cohesion_loss_per_day": 0, "stockpile": {},
        }},
        victory_rules=[],
        history=[],
        victory=None,
        stocks={},
        units=[{
            "id": "mover", "side": "a", "alive": True, "foot": True,
            "x_mm": 0, "y_mm": 0, "speed_mm_per_day": 0, "equipment": {},
        }],
        points=[{"id": "pad", "side": "a", "x_mm": 0, "y_mm": 0, "hold_mm": 1}],
        cells=[],
        operations=[{
            "id": "op-1",
            "name": "Hold the point",
            "owner": "a",
            "objective_point": "pad",
            "unit_ids": ["mover"],
            "issued_day": 0,
            "active_day": 0,
        }],
    )


def test_a_head_of_state_does_not_open_a_campaign():
    c = _campaign()
    c.leaders = [{
        "id": "head", "name": "Head", "source": "fixture",
        "from_day": 0, "to_day": 2, "command": ["mover"],
    }]
    c.generals = []
    step_day(c)
    assert c.campaigns == []


def test_a_seated_general_opens_the_operation_he_commands():
    c = _campaign()
    c.generals = [{
        "id": "gen", "name": "Fixture", "source": "fixture",
        "command": ["mover"], "from_day": 0, "to_day": 2,
    }]
    step_day(c)
    assert len(c.campaigns) == 1
    row = c.campaigns[0]
    assert row["id"] == "op-1"
    assert row["name"] == "Hold the point"
    assert row["opened_day"] == 0
    assert row["closed_day"] is None
    assert row["result"] == "open"
    assert row["battles"] == []
    sentence = next(item["sentence"] for item in c.events if item["kind"] == "campaign_open")
    assert sentence == "Campaign op-1 opened."
    assert "1939" not in sentence and "modern" not in sentence
