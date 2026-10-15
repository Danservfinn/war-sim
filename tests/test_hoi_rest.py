"""HoI-shaped day rules. Path stays. No focus trees."""

from sim.campaign.step import step_day
from tests.test_campaign import _base


def _war():
    c = _base()
    c.victory_rules = []
    c.factions["side_b"]["food_t"] = 100
    c.factions["side_b"]["food_burn_t"] = 0
    c.factions["side_b"]["fuel"] = {"diesel": 10}
    c.factions["side_b"]["stockpile"] = {"rifle": 100, "truck": 4}
    c.factions["side_b"]["manpower_law"] = "limited"
    c.factions["side_b"]["consumer_goods_milli"] = 200
    c.factions["side_b"]["victory_points"] = 20
    c.factions["side_b"]["surrender_points"] = 10
    c.units = [{
        "id": "div",
        "side": "side_b",
        "domain": "ground",
        "foot": False,
        "fuel_grade": "diesel",
        "fuel_need": 1,
        "hub_id": "hub",
        "in_hub_range": True,
        "organization": 100,
        "organization_max": 100,
        "equipment_need": {"rifle": 10},
        "equipment": {"rifle": 10},
        "planning": 0,
        "entrenchment": 0,
        "order_days": 0,
        "stationary_days": 0,
        "posture": "attack",
        "reliability_milli": 100,
    }]
    c.hubs = [{"id": "hub", "side": "side_b", "rail_level": 2, "trucks": 5, "throughput_t": 0}]
    c.plants[0]["kind"] = "military"
    c.plants[0]["efficiency_milli"] = 200
    c.plants[0]["efficiency_cap_milli"] = 500
    c.plants[0]["lines"][0]["model"] = "rifle"
    c.plants[0]["lines"][0]["power_draw"] = 5
    c.states = [{
        "id": "home",
        "owner": "side_b",
        "power_plants": 1,
        "terrain_power": 4,
        "coal_boost": 0,
        "industry_power": 2,
        "victory_points": 8,
        "occupied": False,
        "resistance": 0,
        "garrison_need": 2,
    }]
    c.research = [{"id": "tank", "side": "side_b", "days_left": 2, "ahead_penalty_days": 0, "unlocked": False}]
    c.commanders = [{"id": "cdr", "side": "side_b", "skill": 1, "captured": False, "attack_milli": 50}]
    c.doctrine = {"side_b": {"supply_use_milli": 1000, "attack_milli": 100}}
    c.air_missions = []
    c.fleets["trucks"]["home_port"] = None
    c.construction = []
    return c


def test_hub_range_is_not_a_stop():
    c = _war()
    c.units[0]["in_hub_range"] = False
    step_day(c)
    unit = c.units[0]
    assert unit["supply_status_milli"] == 0
    assert unit["organization"] < 100
    assert unit["attrition_qty"] > 0
    assert unit["attack_mod_milli"] < 1000


def test_out_of_fuel_cuts_stats_and_speed():
    c = _war()
    c.factions["side_b"]["fuel"]["diesel"] = 0
    step_day(c)
    assert c.units[0]["fuel_stat_milli"] == 100
    assert c.units[0]["fuel_speed_milli"] == 600


def test_foot_ignores_fuel():
    c = _war()
    c.units[0]["foot"] = True
    c.factions["side_b"]["fuel"]["diesel"] = 0
    step_day(c)
    assert c.units[0]["fuel_stat_milli"] == 1000
    assert c.units[0]["fuel_speed_milli"] == 1000


def test_air_drop_moves_supply_not_fuel():
    c = _war()
    c.air_missions = [{"kind": "supply_drop", "side": "side_b", "target": "div", "supply_t": 3, "fuel_t": 9}]
    c.units[0]["in_hub_range"] = False
    c.units[0]["fuel_need"] = 0
    before = c.factions["side_b"]["fuel"]["diesel"]
    step_day(c)
    assert c.units[0]["air_supply_t"] == 3
    assert c.factions["side_b"]["fuel"]["diesel"] == before


def test_line_switch_crashes_efficiency():
    c = _war()
    step_day(c)
    climbed = c.plants[0]["efficiency_milli"]
    assert climbed > 200
    c.plants[0]["lines"][0]["model"] = "gun"
    step_day(c)
    assert c.plants[0]["efficiency_milli"] < climbed
    assert c.plants[0]["efficiency_milli"] <= 100


def test_power_is_state_and_recipe_draws_it():
    c = _war()
    c.states[0]["coal_boost"] = 3
    c.plants[0]["lines"][0]["power_draw"] = 100
    step_day(c)
    assert c.states[0]["power_out"] == 4 + 3 + 2
    assert c.plants[0]["energy_ratio_milli"] < 1000
    assert c.plants[0]["military_out"] < c.plants[0]["lines"][0]["daily_cap"]


def test_quiet_day_still_deletes_equipment():
    c = _war()
    step_day(c)
    assert c.units[0]["equipment"]["rifle"] < 10
    assert c.factions["side_b"]["stockpile"]["rifle"] < 100


def test_research_is_frozen():
    c = _war()
    step_day(c)
    step_day(c)
    assert c.research[0]["unlocked"] is False


def test_planning_and_entrenchment_are_days():
    c = _war()
    c.units[0]["order_days"] = 4
    c.units[0]["planning"] = 4
    c.units[0]["posture"] = "defend"
    c.units[0]["stationary_days"] = 6
    c.units[0]["entrenchment"] = 6
    step_day(c)
    assert c.units[0]["planning"] == 5
    assert c.units[0]["entrenchment"] == 7


def test_cas_does_not_write_an_attack_modifier():
    c = _war()
    c.air_missions = [{"kind": "cas", "side": "side_a", "target": "div", "attack_milli": 150}]
    step_day(c)
    assert "air_attack_milli" not in c.units[0]


def test_convoy_raid_deletes_in_transit():
    c = _war()
    c.links = []
    c.in_transit = [{"id": "ship-1", "link_id": "sand", "cargo_id": "food", "qty_t": 8, "depart_day": 0, "arrive_day": 9, "convoy": True}]
    c.raids = [{"day": 0, "target": "ship-1", "sink_milli": 1000}]
    step_day(c)
    assert c.in_transit == []


def test_occupation_cuts_output_and_needs_garrison():
    c = _war()
    c.factions["side_a"] = {"food_t": 10, "food_burn_t": 0, "cohesion": 50, "cohesion_loss_per_day": 0, "loss_hold_days": 0, "trainees": 0, "training_cap_per_day": 0, "manpower": 20, "fuel": {}, "garrison_manpower": 0, "stockpile": {}}
    c.states[0]["occupied"] = True
    c.states[0]["resistance"] = 400
    c.states[0]["owner"] = "side_a"
    step_day(c)
    assert c.states[0]["output_milli"] == 600
    assert c.factions["side_a"]["garrison_manpower"] == 2


def test_a_point_threshold_does_not_surrender():
    c = _war()
    c.factions["side_b"]["victory_points"] = 5
    c.factions["side_b"]["surrender_points"] = 10
    step_day(c)
    assert c.victory is None


def test_captured_stock_credits_the_taker():
    c = _war()
    c.factions["side_a"] = {"food_t": 10, "food_burn_t": 0, "cohesion": 50, "cohesion_loss_per_day": 0, "loss_hold_days": 0, "trainees": 0, "training_cap_per_day": 0, "manpower": 20, "fuel": {}, "stockpile": {}}
    c.depots = [{"id": "dump", "side": "side_b", "stock": {"rifle": 30}, "captured_by": "side_a", "captured_day": 0}]
    step_day(c)
    assert c.factions["side_a"]["stockpile"]["rifle"] == 30
    assert c.depots[0]["stock"]["rifle"] == 0


def test_construction_raises_rail_after_days():
    c = _war()
    c.construction = [{"id": "rail", "kind": "rail", "target": "hub", "days_left": 1, "levels": 1}]
    step_day(c)
    assert c.hubs[0]["rail_level"] == 3
    assert c.construction == []
