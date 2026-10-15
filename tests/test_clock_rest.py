"""The day step moves the unit, writes the contact, and the shot splashes."""

from sim.campaign.step import Campaign, step_day
from sim.systems.combat import resolve_shot


def _mover():
    return Campaign(
        day=0, nodes=[], plants=[], lots=[], fleets={}, links=[], in_transit=[], imports=[],
        factions={"side_a": {"cohesion": 5, "manpower": 1, "trainees": 0, "training_cap_per_day": 0,
                             "food_t": 1, "food_burn_t": 0, "water_t": 0, "water_burn_t": 0,
                             "fuel": {"diesel": 0}, "loss_hold_days": 0, "cohesion_loss_per_day": 0}},
        victory_rules=[], history=[], victory=None, stocks={},
        units=[{"id": "u1", "side": "side_a", "alive": True, "foot": True,
                "x_mm": 0, "y_mm": 0, "speed_mm_per_day": 5_000_000, "heading": "east",
                "in_bubble": False, "sensor_range_mm": 20_000_000,
                "equipment": {}, "organization": 10}],
        contacts=[],
    )


def test_unit_without_a_course_does_not_march():
    c = _mover()
    step_day(c)
    assert c.units[0]["x_mm"] == 0
    c.units[0]["speed_mm_per_day"] = 25_000_000
    step_day(c)
    assert c.units[0]["x_mm"] == 0


def test_bubble_without_a_course_does_not_move():
    c = _mover()
    c.units[0]["in_bubble"] = True
    c.units[0]["speed_mm_per_day"] = 250_000
    step_day(c)
    assert c.units[0]["x_mm"] == 0


def test_retired_speed_cut_is_not_a_march():
    c = _mover()
    c.units[0]["foot"] = False
    c.units[0]["fuel_grade"] = "diesel"
    c.units[0]["in_bubble"] = True
    c.units[0]["speed_mm_per_day"] = 1_000_000
    step_day(c)
    assert c.units[0]["x_mm"] == 0
    c.units[0]["foot"] = True
    c.units[0]["x_mm"] = 0
    step_day(c)
    assert c.units[0]["x_mm"] == 0


def test_detection_writes_a_contact_inside_sensor_range():
    c = _mover()
    c.units.append({"id": "u2", "side": "side_b", "alive": True, "x_mm": 1_000_000, "y_mm": 0,
                    "speed_mm_per_day": 0, "in_bubble": False, "sensor_range_mm": 0, "equipment": {}})
    step_day(c)
    seen = [row for row in c.contacts if row["observer"] == "u1" and row["target"] == "u2"]
    assert seen and seen[0]["quality"] == "detected"


def test_shot_splashes_a_neighbor():
    attacker = {"WeaponMount": [{"mount_id": "gun", "ammo": [
        {"ammo_id": "he", "qty": 2, "warhead": "he", "penetration_mm": 10, "blast": 6, "splash_mm": 4, "guidance": "none"}
    ], "range_bands": [{"max_m": 1000, "accuracy": 1000}]}], "Crew": {"billets": [{"role": "gunner", "count": 1, "skill": 90}]}}
    defender = {"Physical": {"integrity": 20, "signature": {"visual": 1000},
                             "armor": [{"aspect": "front", "thickness_mm": 0, "ke_mod": 1000}]}}
    neighbor = {"id": "n1", "distance_mm": 1000, "Physical": {"integrity": 9}}

    class Roll:
        def roll(self, n):
            return 0

    result = resolve_shot(attacker, defender, 100, 1000, "front", Roll(), neighbors=[neighbor])
    assert result["outcome"] == "penetrated"
    assert neighbor["Physical"]["integrity"] == 5  # 9 - 4
