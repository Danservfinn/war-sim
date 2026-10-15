"""A failed air gate does not call a shot. The band fixture has no year field."""

from sim.campaign.step import Campaign, step_day


def test_a_failed_air_gate_does_not_call_resolve_shot():
    ammo = {"ammo_id": "missile", "qty": 2, "guidance": "radar", "guidance_match": 1000,
            "penetration_mm": 40, "blast": 20, "warhead": "ke"}
    wing = {
        "id": "radar", "side": "a", "domain": "air", "alive": True, "sortie_flown": True,
        "cell_id": "field", "sortie_fuel": 1, "mission": {"kind": "cap"}, "fuel_grade": "avgas",
        "WeaponMount": [{"mount_id": "rack", "rounds_per_day": 2, "ammo": [ammo],
                         "range_bands": [{"max_m": 20000, "accuracy": 1000}]}],
        "Crew": {"billets": [{"role": "pilot", "count": 1, "trained_days": 0, "skill": 80}]},
    }
    defender = {
        "id": "optic", "side": "b", "alive": True,
        "Physical": {"integrity": 10, "signature": {"visual": 1000},
                     "armor": [{"aspect": "front", "thickness_mm": 0, "ke_mod": 1000}]},
    }
    c = Campaign(
        day=0, nodes=[], plants=[], lots=[], fleets={}, links=[], in_transit=[], imports=[],
        factions={"a": {"cohesion": 50, "manpower": 1, "trainees": 0, "training_cap_per_day": 0,
                        "food_t": 1, "food_burn_t": 0, "water_t": 0, "water_burn_t": 0,
                        "fuel": {"avgas": 9}, "loss_hold_days": 0, "cohesion_loss_per_day": 0,
                        "stockpile": {}},
                  "b": {"cohesion": 50, "manpower": 1, "trainees": 0, "training_cap_per_day": 0,
                        "food_t": 1, "food_burn_t": 0, "water_t": 0, "water_burn_t": 0,
                        "fuel": {}, "loss_hold_days": 0, "cohesion_loss_per_day": 0, "stockpile": {}}},
        victory_rules=[], history=[], victory=None, stocks={},
        units=[wing, defender], engagements=[{
            "day": 0, "attacker": wing, "defender": defender,
            "distance_m": 1000, "weather": 1000, "aspect": "front",
        }],
        generals=[], cells=[{"id": "field", "surface": "land", "airfield": True, "damage_milli": 0, "x_mm": 0, "y_mm": 0}],
    )
    step_day(c)
    assert ammo["qty"] == 2
    assert not any(row.get("kind") == "shot" for row in getattr(c, "events", []) or [])
