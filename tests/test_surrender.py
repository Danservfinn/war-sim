"""Victory is complete and total surrender. A partial loss is not the end."""

from sim.campaign.step import step_day
from tests.test_campaign import _base


def _side():
    c = _base()
    c.victory_rules = []
    c.factions["side_a"] = {
        "cohesion": 50, "manpower": 10, "trainees": 0, "training_cap_per_day": 0,
        "food_t": 10, "food_burn_t": 0, "water_t": 0, "water_burn_t": 0,
        "fuel": {}, "loss_hold_days": 0, "cohesion_loss_per_day": 0,
        "victory_points": 4, "stockpile": {"rifle": 3},
    }
    c.factions["side_b"]["victory_points"] = 2
    c.factions["side_b"]["stockpile"] = {}
    c.factions["side_b"]["surrender_hold_days"] = 1
    c.units = [{"id": "b1", "side": "side_b", "alive": True, "equipment": {"rifle": 1}}]
    return c


def test_a_partial_point_loss_is_not_surrender():
    c = _side()
    c.factions["side_b"]["victory_points"] = 5
    c.factions["side_b"]["surrender_points"] = 10
    step_day(c)
    assert c.victory is None


def test_dead_units_are_not_surrender_while_a_plant_still_mints():
    c = _side()
    c.units[0]["alive"] = False
    c.factions["side_b"]["victory_points"] = 0
    step_day(c)
    assert c.plants[0]["military_out"] > 0
    assert c.victory is None


def test_total_surrender_needs_no_points_no_units_and_no_output():
    c = _side()
    c.units[0]["alive"] = False
    c.factions["side_b"]["victory_points"] = 0
    c.factions["side_b"]["stockpile"] = {}
    c.plants[0]["lines"][0]["powder_local"] = False
    step_day(c)
    assert c.victory["reason"] == "total_surrender"
    assert c.victory["lost"] == "side_b"
    assert c.victory["winner"] == "side_a"
