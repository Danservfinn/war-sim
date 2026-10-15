"""Shot employment. Fails until sim.systems.employment exists."""

from sim.systems.combat import hit_chance
from sim.systems.employment import (
    apply_engagement,
    classify_kill,
    legal_payload,
    proximity_damage,
    will_fire,
)


def test_cover_fatigue_and_experience_scale_the_product():
    base = hit_chance(1000, 100, 1000, 1000, 1000)
    scaled = apply_engagement(base, cover=500, fatigue=40, experience=50, night_mod=1000)
    # fatigue mod 800, experience mod 750, cover 500
    assert scaled == base * 500 // 1000 * 800 // 1000 * 750 // 1000


def test_suppression_and_broken_morale_block_fire():
    assert will_fire(morale=10, posture="exposed", suppressed_s=0) is False
    assert will_fire(morale=10, posture="dug_in", suppressed_s=0) is True
    assert will_fire(morale=80, posture="exposed", suppressed_s=3) is False


def test_proximity_damages_inside_radius_without_penetration():
    assert proximity_damage(blast=40, radius_m=30, dist_m=15, blast_mod=1000) == 20
    assert proximity_damage(blast=40, radius_m=30, dist_m=30, blast_mod=1000) == 0


def test_mobility_pool_is_not_catastrophic():
    flags = classify_kill(integrity=40, mobility_hp=0, firepower_hp=10, crew=4)
    assert flags["mobility_kill"] is True
    assert flags["catastrophic"] is False


def test_hardpoint_conflict_and_fuel_share_the_payload():
    stations = [
        {"station_id": "a", "load_id": "bomb", "mass_kg": 200, "incompatible_with": ["b"]},
        {"station_id": "b", "load_id": "tank", "mass_kg": 100, "incompatible_with": ["a"]},
    ]
    assert legal_payload(stations, fuel_kg=50, payload_cap_kg=400) is False
    ok = [{"station_id": "a", "load_id": "bomb", "mass_kg": 200, "incompatible_with": []}]
    assert legal_payload(ok, fuel_kg=250, payload_cap_kg=400) is False
    assert legal_payload(ok, fuel_kg=150, payload_cap_kg=400) is True
