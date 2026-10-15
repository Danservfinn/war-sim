"""Air launch gates and fuel arithmetic. A failed gate does not call a shot."""

from __future__ import annotations


_ORDER = (
    "no_signer",
    "no_mission",
    "ready_day",
    "no_field",
    "no_deck",
    "no_crew",
    "no_maint",
    "weather",
    "overflight",
    "no_load",
    "payload",
    "no_fuel",
    "uncovered",
    "bingo",
    "wcs_hold",
    "wcs_tight",
    "wra_range",
    "wra_salvo",
    "wra_shooters",
    "no_contact",
    "cap",
)


def sortie_ml(distance_mm: int, burn_ml_per_km: int, reserve_ml: int, legs: int = 2) -> int:
    """Two legs plus reserve. Milliliters. A missing burn rate is not a guess."""
    leg = int(distance_mm) * int(burn_ml_per_km) // 1_000_000
    return leg * int(legs) + int(reserve_ml)


def guidance_input(ammo: dict) -> int:
    """Air guidance. A missing table row is 0. Unguided is 1000. No shot is taken here."""
    kind = ammo.get("guidance", "none")
    if kind == "none":
        return 1000
    if "guidance_match" not in ammo and "match" not in ammo:
        return 0
    return int(ammo.get("guidance_match", ammo.get("match", 0)))


def _seated(general: dict, wing_id: str, day: int) -> bool:
    if not general or general.get("captured"):
        return False
    if not str(general.get("name") or "").strip() or not str(general.get("source") or "").strip():
        return False
    if int(general.get("from_day", 1)) > int(day) or int(day) >= int(general.get("to_day", 0)):
        return False
    return wing_id in (general.get("command") or [])


def first_gate(wing: dict, mission: dict | None, doctrine: dict | None, day: int, generals=None, fuel=None, field=None, weather=None) -> str | None:
    """First failure wins. Nothing is spent. resolve_shot is not called."""
    doctrine = doctrine or {}
    mission = mission or {}
    generals = list(generals or [])
    fuel = fuel or {}
    checks = {
        "no_signer": not any(_seated(row, str(wing.get("id") or ""), day) for row in generals),
        "no_mission": not mission.get("kind"),
        "ready_day": int(wing.get("ready_day", day)) > int(day),
        "no_field": not (field and field.get("airfield") and field.get("surface") == "land" and int(field.get("damage_milli", 0)) < 1000),
        "no_deck": False,
        "no_crew": not any(
            row.get("role") == "pilot" and int(row.get("count", 0)) > 0 and int(row.get("trained_days", 0)) <= 0
            for row in ((wing.get("Crew") or {}).get("billets") or [])
        ) and not wing.get("uninhabited"),
        "no_maint": int(wing.get("maint_need", 0)) > 0 and int(wing.get("maintainer_billets", 0)) * int(wing.get("craft_per_maintainer", 0)) < 1,
        "weather": weather is not None and int(weather.get("ceiling_m", 0)) < int((wing.get("min_ceiling_m") or {}).get(mission.get("altitude"), 0)),
        "overflight": False,
        "no_load": False,
        "payload": False,
        "no_fuel": int(fuel.get(wing.get("fuel_grade") or "", 0)) <= 0,
        "uncovered": False,
        "bingo": False,
        "wcs_hold": doctrine.get("wcs") == "hold",
        "wcs_tight": False,
        "wra_range": False,
        "wra_salvo": False,
        "wra_shooters": False,
        "no_contact": False,
        "cap": False,
    }
    for name in _ORDER:
        if checks[name]:
            return name
    return None
