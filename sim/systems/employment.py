"""Employment mods on top of the shot product. No year and no region."""

from __future__ import annotations


def apply_engagement(base: int, cover: int, fatigue: int, experience: int, night_mod: int = 1000) -> int:
    fatigue_mod = 1000 - int(fatigue) * 5
    experience_mod = 500 + int(experience) * 5
    value = int(base)
    for mod in (int(cover), fatigue_mod, experience_mod, int(night_mod)):
        value = value * mod // 1000
    return value


def will_fire(morale: int, posture: str, suppressed_s: int, break_at: int = 20) -> bool:
    if int(suppressed_s) > 0:
        return False
    if int(morale) < int(break_at) and posture != "dug_in":
        return False
    return True


def proximity_damage(blast: int, radius_m: int, dist_m: int, blast_mod: int) -> int:
    if int(radius_m) <= 0 or int(dist_m) >= int(radius_m):
        return 0
    return int(blast) * (int(radius_m) - int(dist_m)) // int(radius_m) * int(blast_mod) // 1000


def classify_kill(integrity: int, mobility_hp: int, firepower_hp: int, crew: int) -> dict:
    catastrophic = int(integrity) <= 0 or (int(mobility_hp) <= 0 and int(firepower_hp) <= 0 and int(crew) <= 0)
    return {
        "mobility_kill": int(mobility_hp) <= 0 and not catastrophic,
        "firepower_kill": int(firepower_hp) <= 0 and not catastrophic,
        "crew_kill": int(crew) <= 0 and not catastrophic,
        "catastrophic": catastrophic,
    }


def legal_payload(stations: list[dict], fuel_kg: int, payload_cap_kg: int) -> bool:
    loaded = [row for row in stations if row.get("load_id")]
    occupied = {row["station_id"] for row in loaded}
    for row in loaded:
        for other in row.get("incompatible_with") or []:
            if other in occupied:
                return False
    mass = int(fuel_kg) + sum(int(row["mass_kg"]) for row in loaded)
    return mass <= int(payload_cap_kg)
