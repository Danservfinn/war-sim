"""Side-filtered map snapshot. Renderer input only."""

from __future__ import annotations


def _symbol(entity: dict, in_bubble: bool) -> str:
    org = entity.get("Organization") or {}
    if org.get("aggregated") and not in_bubble:
        return "formation"
    return "platform"


def build_snapshot(world, viewer_side: str, bubble_ids: list[str]) -> list[dict]:
    bubble = set(bubble_ids)
    rows = []
    for eid in world.ids():
        ent = world.entities[eid]
        ident = ent["Identity"]
        pos = ent.get("Position")
        if not pos:
            continue
        own = ident["side"] == viewer_side
        if own:
            quality = "friendly"
        else:
            tracks = [
                t for t in world.tracks
                if t.get("target_id") == eid and t.get("observer_side") == viewer_side
            ]
            if not tracks:
                continue
            quality = tracks[0]["quality"]
            if quality == "undetected":
                continue
            pos = {"x_mm": tracks[0]["x_mm"], "y_mm": tracks[0]["y_mm"], "heading_mdeg": pos.get("heading_mdeg", 0)}
        rows.append({
            "id": eid,
            "side": ident["side"],
            "posture": (ent.get("Physical") or {}).get("posture", "exposed"),
            "symbol_class": ident["unit_type"],
            "x_mm": int(pos["x_mm"]),
            "y_mm": int(pos["y_mm"]),
            "heading_mdeg": int(pos.get("heading_mdeg", 0)),
            "speed_mmps": int((ent.get("Mobility") or {}).get("speed_mmps", {}).get("road", 0)),
            "contact_quality": quality,
            "formation_id": (ent.get("Organization") or {}).get("formation_id"),
            "selected": False,
            "draw_mode": _symbol(ent, eid in bubble),
        })
    return rows
