"""A course consumes a measured cell. No coast, no water crossing. The refusal is a sentence."""

from sim.campaign.step import Campaign, step_day

CELL = 10_000_000


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
            "id": "mover", "side": "a", "alive": True, "foot": True, "domain": "land",
            "x_mm": 0, "y_mm": 0, "cell_id": "shore",
            "speed_mm_per_day": 25_000_000, "in_bubble": False, "equipment": {},
        }],
        cells=[
            {"id": "shore", "surface": "land", "x_mm": 0, "y_mm": 0, "source": "fixture"},
            {"id": "water", "surface": "sea", "x_mm": CELL, "y_mm": 0, "source": "fixture"},
            {"id": "far", "surface": "land", "x_mm": 2 * CELL, "y_mm": 0, "source": "fixture"},
            {"id": "inland", "surface": "land", "x_mm": 0, "y_mm": CELL, "source": "fixture"},
        ],
        march_orders=[{
            "id": "march-1",
            "entity_id": "mover",
            "issued_day": 0,
            "active_day": 0,
            "course": [{"cell_id": "far", "x_mm": 2 * CELL, "y_mm": 0}],
            "waypoint": 0,
        }],
    )


def test_a_water_crossing_with_no_coast_is_logged_and_not_walked():
    campaign = _campaign()
    assert not any(row.get("surface") == "coast" for row in campaign.cells)
    step_day(campaign)
    assert campaign.units[0]["x_mm"] == 0
    assert campaign.units[0]["y_mm"] == 0
    assert campaign.march_orders[0].get("gate") == "no_surface"
    sentences = [row["sentence"] for row in campaign.events if row["kind"] == "march_refused"]
    assert sentences == ["March mover refused. Gate no_surface."]


def test_a_land_cell_on_the_course_is_consumed():
    campaign = _campaign()
    campaign.march_orders[0]["course"] = [{"cell_id": "inland", "x_mm": 0, "y_mm": CELL}]
    step_day(campaign)
    assert campaign.units[0]["x_mm"] == 0
    assert campaign.units[0]["y_mm"] == CELL
    assert campaign.units[0]["cell_id"] == "inland"
    assert campaign.march_orders[0]["waypoint"] == 1
    assert campaign.march_orders[0].get("gate") != "no_surface"
