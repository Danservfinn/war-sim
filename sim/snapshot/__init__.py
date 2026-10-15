"""Map rows. The renderer does not invent units."""

from sim.snapshot.builder import build_snapshot


def map_rows(campaign, viewer: str) -> list[dict]:
    by_id = {unit["id"]: unit for unit in campaign.units}
    seen = {}
    for row in campaign.contacts:
        observer = by_id.get(row["observer"])
        if observer and observer.get("side") == viewer:
            seen[row["target"]] = row["quality"]
    rows = []
    for unit in sorted(campaign.units, key=lambda item: item["id"]):
        if not unit.get("alive", True):
            continue
        if unit.get("side") == viewer:
            quality = "friendly"
        else:
            quality = seen.get(unit["id"])
            if not quality:
                continue
        rows.append({
            "id": unit["id"],
            "side": unit["side"],
            "x_mm": int(unit.get("x_mm", 0)),
            "y_mm": int(unit.get("y_mm", 0)),
            "contact_quality": quality,
            "posture": unit.get("posture", "exposed"),
            "symbol_class": unit.get("symbol_class", "infantry"),
        })
    return rows
