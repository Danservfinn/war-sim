"""Combat resolution. Numbers only. No side, year, or region branch."""

from __future__ import annotations


def select_ammo(mount: dict) -> dict | None:
    for ammo in mount.get("ammo") or []:
        if int(ammo.get("qty", 0)) > 0:
            return ammo
    return None


def hit_chance(accuracy: int, skill: int, weather: int, guidance: int, signature: int) -> int:
    """Thousandths. Skill is 0-100. Other inputs are already thousandths."""
    skill_milli = int(skill) * 10
    numerator = int(accuracy) * skill_milli * int(weather) * int(guidance) * int(signature)
    return numerator // (1000 ** 4)


def penetration_margin(pen_mm: int, armor: list[dict], aspect: str, warhead: str) -> int:
    plate = next(row for row in armor if row["aspect"] == aspect)
    mod_key = "heat_mod" if warhead == "heat" else "ke_mod"
    effective = int(plate["thickness_mm"]) * int(plate.get(mod_key, 1000)) // 1000
    return int(pen_mm) - effective


def _gunner_skill(attacker: dict) -> int:
    billets = (attacker.get("Crew") or {}).get("billets") or []
    gunners = [b for b in billets if b.get("role") == "gunner" and int(b.get("count", 0)) > 0]
    pool = gunners or billets
    if not pool:
        return 0
    return int(pool[0].get("skill", 0))


def _band(mount: dict, distance_m: int) -> dict | None:
    bands = sorted(mount.get("range_bands") or [], key=lambda row: int(row["max_m"]))
    for band in bands:
        if distance_m <= int(band["max_m"]):
            return band
    return None


def _guidance_match(ammo: dict, attacker: dict | None = None) -> int:
    # Unguided does not need a seeker. Guided rounds without a match are a later catalog field.
    if ammo.get("guidance", "none") == "none":
        return 1000
    match = int(ammo.get("guidance_match", 1000))
    if ammo.get("guidance") == "optical" and not (attacker or {}).get("illumination"):
        return match * 8 // 24
    return match


def resolve_shot(attacker: dict, defender: dict, distance_m: int, weather: int, aspect: str, stream, neighbors: list | None = None, mount_id: str | None = None) -> dict:
    mounts = sorted(attacker.get("WeaponMount") or [], key=lambda row: row.get("mount_id", ""))
    if mount_id is None:
        mount = next((row for row in mounts if select_ammo(row)), None)
    else:
        mount = next((row for row in mounts if row.get("mount_id") == mount_id), None)
        if mount is not None and select_ammo(mount) is None:
            mount = None
    if mount is None:
        return {"outcome": "no_ammo", "margin_mm": 0}
    ammo = select_ammo(mount)
    band = _band(mount, distance_m)
    ammo["qty"] = int(ammo["qty"]) - 1
    if band is None:
        return {"outcome": "out_of_range", "margin_mm": 0, "ammo_id": ammo["ammo_id"]}

    signature = int(((defender.get("Physical") or {}).get("signature") or {}).get("visual", 0))
    if defender.get("posture") == "submerged":
        signature = int(((defender.get("Physical") or {}).get("signature") or {}).get("submerged", 0))
    chance = hit_chance(
        accuracy=int(band["accuracy"]),
        skill=_gunner_skill(attacker),
        weather=weather,
        guidance=_guidance_match(ammo, attacker),
        signature=signature,
    )
    roll = stream.roll(1000)
    if roll >= chance:
        return {"outcome": "miss", "margin_mm": 0, "ammo_id": ammo["ammo_id"], "hit_chance": chance, "roll": roll}

    warhead = ammo.get("warhead", "ke")
    pen = int(ammo.get("penetration_mm", band.get("penetration_mm", 0)))
    margin = penetration_margin(pen, defender["Physical"]["armor"], aspect, warhead)
    if margin < 0:
        return {"outcome": "hit_no_penetration", "margin_mm": margin, "ammo_id": ammo["ammo_id"]}

    blast = int(ammo.get("blast", band.get("blast", 0)))
    physical = defender["Physical"]
    physical["integrity"] = max(0, int(physical["integrity"]) - (blast + margin))
    for neighbor in neighbors or []:
        reach = int(ammo.get("splash_mm", 0))
        if reach <= 0 or int(neighbor.get("distance_mm", 10**9)) > reach * 1000:
            continue
        body = neighbor.setdefault("Physical", {})
        body["integrity"] = max(0, int(body.get("integrity", 0)) - reach)
    return {
        "outcome": "penetrated",
        "margin_mm": margin,
        "ammo_id": ammo["ammo_id"],
        "damage": blast + margin,
    }
