"""Combat math. Fails until sim.systems.combat exists."""

from sim.rng.streams import Stream
from sim.systems.combat import hit_chance, penetration_margin, resolve_shot, select_ammo


def _stream():
    return Stream(scenario_seed=1939, tick=1, name="combat")


def test_empty_precision_stock_fires_next_ammo_same_formula():
    mount = {
        "mount_id": "bay",
        "ammo": [
            {"ammo_id": "gps_bomb", "qty": 0, "guidance": "gps", "penetration_mm": 0, "blast": 40},
            {"ammo_id": "unguided_he", "qty": 4, "guidance": "none", "penetration_mm": 20, "blast": 30},
        ],
    }
    picked = select_ammo(mount)
    assert picked["ammo_id"] == "unguided_he"


def test_hit_chance_is_product_of_factors_not_era():
    # 800 * 700 * 1000 * 1000 * 500 / 1000**4 = 280
    p = hit_chance(
        accuracy=800,
        skill=70,
        weather=1000,
        guidance=1000,
        signature=500,
    )
    assert p == 280


def test_miss_does_not_damage_and_round_is_spent():
    attacker = {
        "WeaponMount": [{
            "mount_id": "gun",
            "rof_per_min": 60,
            "range_bands": [{"max_m": 1000, "accuracy": 0, "penetration_mm": 100, "blast": 20}],
            "ammo": [{"ammo_id": "ap", "qty": 2, "guidance": "none", "penetration_mm": 100, "blast": 20}],
        }],
        "Crew": {"billets": [{"role": "gunner", "count": 1, "skill": 80}], "casualty_bias": 500},
    }
    defender = {
        "Physical": {
            "integrity": 40,
            "integrity_max": 40,
            "armor": [{"aspect": "front", "thickness_mm": 10, "ke_mod": 1000, "heat_mod": 1000}],
            "signature": {"visual": 1000},
        },
        "Defenses": {"point_defense": 0, "decoys": 0},
        "Crew": {"billets": [{"role": "rifle", "count": 4, "skill": 40}], "casualty_bias": 500},
    }
    result = resolve_shot(attacker, defender, distance_m=100, weather=1000, aspect="front", stream=_stream())
    assert result["outcome"] == "miss"
    assert defender["Physical"]["integrity"] == 40
    assert attacker["WeaponMount"][0]["ammo"][0]["qty"] == 1


def test_fail_to_penetrate_spends_round_and_skips_structure():
    attacker = {
        "WeaponMount": [{
            "mount_id": "gun",
            "rof_per_min": 60,
            "range_bands": [{"max_m": 1000, "accuracy": 1000, "penetration_mm": 30, "blast": 50}],
            "ammo": [{"ammo_id": "ap", "qty": 1, "guidance": "none", "penetration_mm": 30, "blast": 50, "warhead": "ke"}],
        }],
        "Crew": {"billets": [{"role": "gunner", "count": 1, "skill": 100}], "casualty_bias": 0},
    }
    defender = {
        "Physical": {
            "integrity": 40,
            "integrity_max": 40,
            "armor": [{"aspect": "front", "thickness_mm": 80, "ke_mod": 1000, "heat_mod": 1000}],
            "signature": {"visual": 1000},
        },
        "Defenses": {"point_defense": 0, "decoys": 0},
        "Crew": {"billets": [{"role": "rifle", "count": 2, "skill": 40}], "casualty_bias": 800},
    }
    result = resolve_shot(attacker, defender, distance_m=100, weather=1000, aspect="front", stream=_stream())
    assert result["outcome"] == "hit_no_penetration"
    assert result["margin_mm"] < 0
    assert defender["Physical"]["integrity"] == 40
    assert defender["Crew"]["billets"][0]["count"] == 2


def test_penetration_marks_integrity_with_blast_plus_margin():
    attacker = {
        "WeaponMount": [{
            "mount_id": "gun",
            "rof_per_min": 60,
            "range_bands": [{"max_m": 2000, "accuracy": 1000, "penetration_mm": 100, "blast": 15}],
            "ammo": [{"ammo_id": "ap", "qty": 3, "guidance": "none", "penetration_mm": 100, "blast": 15, "warhead": "ke"}],
        }],
        "Crew": {"billets": [{"role": "gunner", "count": 1, "skill": 100}], "casualty_bias": 0},
    }
    defender = {
        "Physical": {
            "integrity": 80,
            "integrity_max": 80,
            "armor": [{"aspect": "front", "thickness_mm": 40, "ke_mod": 1000, "heat_mod": 1000}],
            "signature": {"visual": 1000},
        },
        "Defenses": {"point_defense": 0, "decoys": 0},
        "Crew": {"billets": [{"role": "rifle", "count": 4, "skill": 40}], "casualty_bias": 0},
    }
    result = resolve_shot(attacker, defender, distance_m=500, weather=1000, aspect="front", stream=_stream())
    assert result["outcome"] == "penetrated"
    assert result["margin_mm"] == 60
    assert defender["Physical"]["integrity"] == 5  # 80 - (15 + 60)
