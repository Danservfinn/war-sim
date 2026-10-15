"""Section 10. A course is the order. Heading is not."""

from sim.campaign.step import Campaign, step_day


CELL = 10_000_000


def _pair():
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
            "fuel": {"diesel": 50}, "loss_hold_days": 0, "cohesion_loss_per_day": 0,
            "stockpile": {},
        }, "b": {
            "cohesion": 50, "manpower": 1, "trainees": 0, "training_cap_per_day": 0,
            "food_t": 1, "food_burn_t": 0, "water_t": 0, "water_burn_t": 0,
            "fuel": {}, "loss_hold_days": 0, "cohesion_loss_per_day": 0, "stockpile": {},
        }},
        victory_rules=[],
        history=[],
        victory=None,
        stocks={},
        units=[
            {
                "id": "mover", "side": "a", "alive": True, "foot": True,
                "x_mm": 0, "y_mm": 0, "speed_mm_per_day": 25_000_000, "heading": "east",
                "in_bubble": False, "sensor_range_mm": 0, "equipment": {},
            },
            {
                "id": "far", "side": "b", "alive": True, "foot": True,
                "x_mm": 100 * CELL, "y_mm": 0, "speed_mm_per_day": 25_000_000, "heading": "west",
                "in_bubble": False, "sensor_range_mm": 0, "equipment": {},
            },
        ],
        contacts=[],
        engagements=[],
        march_orders=[],
        generals=[{
            "id": "gen",
            "name": "Fixture",
            "source": "fixture",
            "command": ["mover"],
            "from_day": 0,
            "to_day": 9,
        }],
    )


def _order(x=CELL, active_day=0):
    return {
        "id": "march-1",
        "entity_id": "mover",
        "issued_day": 0,
        "active_day": active_day,
        "course": [{"x_mm": x, "y_mm": 0}],
        "waypoint": 0,
    }


def test_a_legal_step_without_a_signer_does_not_move():
    campaign = _pair()
    campaign.generals = []
    campaign.leaders = [{
        "id": "head", "name": "Head", "source": "fixture",
        "from_day": 0, "to_day": 9, "command": ["mover"],
    }]
    campaign.march_orders = [_order(x=CELL)]
    step_day(campaign)
    assert campaign.units[0]["x_mm"] == 0
    assert campaign.units[0]["y_mm"] == 0
    assert campaign.march_orders[0].get("gate") == "no_signer"
    sentences = [row["sentence"] for row in getattr(campaign, "events", []) or [] if row["kind"] == "march_refused"]
    assert sentences == ["March mover refused. Gate no_signer."]


def test_heading_and_speed_are_not_an_order():
    campaign = _pair()
    step_day(campaign)
    assert campaign.units[0]["x_mm"] == 0
    assert campaign.units[1]["x_mm"] == 100 * CELL


def test_course_waits_until_active_day():
    campaign = _pair()
    campaign.march_orders = [_order(active_day=2)]
    step_day(campaign)
    assert campaign.units[0]["x_mm"] == 0


def test_outside_a_bubble_one_cell_toward_the_waypoint():
    campaign = _pair()
    campaign.march_orders = [_order(x=25_000_000)]
    step_day(campaign)
    assert campaign.units[0]["x_mm"] == CELL
    assert campaign.march_orders[0]["waypoint"] == 0


def test_remainder_under_10_km_does_not_move():
    campaign = _pair()
    campaign.march_orders = [_order(x=7_000_000)]
    step_day(campaign)
    assert campaign.units[0]["x_mm"] == 0


def test_inside_a_bubble_the_step_is_millimetres_and_not_a_grid_snap():
    campaign = _pair()
    campaign.units[0]["in_bubble"] = True
    campaign.units[0]["speed_mm_per_day"] = 123_456
    campaign.march_orders = [{
        "id": "march-1",
        "entity_id": "mover",
        "issued_day": 0,
        "active_day": 0,
        "course": [{"x_mm": 0, "y_mm": 1_000_000}],
        "waypoint": 0,
    }]
    step_day(campaign)
    assert campaign.units[0]["x_mm"] == 0
    assert campaign.units[0]["y_mm"] == 123_456


def test_stop_on_the_waypoint_and_the_next_starts_tomorrow():
    campaign = _pair()
    campaign.units[0]["in_bubble"] = True
    campaign.units[0]["speed_mm_per_day"] = 5_000_000
    campaign.march_orders = [{
        "id": "march-1",
        "entity_id": "mover",
        "issued_day": 0,
        "active_day": 0,
        "course": [{"x_mm": 1_000_000, "y_mm": 0}, {"x_mm": 2_000_000, "y_mm": 0}],
        "waypoint": 0,
    }]
    step_day(campaign)
    assert campaign.units[0]["x_mm"] == 1_000_000
    assert campaign.march_orders[0]["waypoint"] == 1
    step_day(campaign)
    assert campaign.units[0]["x_mm"] == 2_000_000
    assert campaign.units[0]["y_mm"] == 0


def test_empty_course_does_not_keep_the_heading():
    campaign = _pair()
    order = _order()
    order["course"] = []
    campaign.march_orders = [order]
    step_day(campaign)
    assert campaign.units[0]["x_mm"] == 0


def test_dry_vehicle_does_not_step_and_foot_ignores_fuel():
    campaign = _pair()
    mover = campaign.units[0]
    mover["foot"] = False
    mover["fuel_grade"] = "diesel"
    mover["fuel_need"] = 2
    mover["fuel_buffer"] = 0
    mover["in_bubble"] = True
    mover["speed_mm_per_day"] = 1_000_000
    campaign.march_orders = [_order(x=1_000_000)]
    step_day(campaign)
    assert mover["x_mm"] == 0
    assert campaign.factions["a"]["fuel"]["diesel"] == 50
    mover["foot"] = True
    step_day(campaign)
    assert mover["x_mm"] == 1_000_000
    assert campaign.factions["a"]["fuel"]["diesel"] == 50


def test_delivered_fuel_is_spent_before_the_step_not_from_the_faction_pile():
    campaign = _pair()
    mover = campaign.units[0]
    mover["foot"] = False
    mover["fuel_grade"] = "diesel"
    mover["fuel_need"] = 2
    mover["fuel_buffer"] = 5
    mover["in_bubble"] = True
    mover["speed_mm_per_day"] = 1_000_000
    campaign.march_orders = [_order(x=1_000_000)]
    step_day(campaign)
    assert mover["x_mm"] == 1_000_000
    assert mover["fuel_buffer"] == 3
    assert campaign.factions["a"]["fuel"]["diesel"] == 50


def test_path_delivery_is_the_only_fuel_that_reaches_a_marching_unit():
    campaign = _pair()
    mover = campaign.units[0]
    mover["foot"] = False
    mover["fuel_grade"] = "diesel"
    mover["fuel_need"] = 3
    mover["fuel_buffer"] = 0
    mover["supply_source_t"] = 10
    mover["supply_links"] = [{"capacity_t": 10, "self_consume_milli": 0}]
    mover["in_bubble"] = True
    mover["speed_mm_per_day"] = 1_000_000
    campaign.march_orders = [_order(x=1_000_000)]
    step_day(campaign)
    assert mover["x_mm"] == 1_000_000
    assert mover["fuel_buffer"] == 7
    assert mover["supply_source_t"] == 0
    assert campaign.factions["a"]["fuel"]["diesel"] == 50


def test_out_of_contact_march_is_not_a_scheduled_shot():
    campaign = _pair()
    campaign.units[0]["sensor_range_mm"] = CELL
    campaign.march_orders = [_order(x=100 * CELL)]
    step_day(campaign)
    assert campaign.units[0]["x_mm"] == CELL
    assert campaign.units[1]["x_mm"] == 100 * CELL
    assert campaign.contacts == []
    assert campaign.engagements == []
