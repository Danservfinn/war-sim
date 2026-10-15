"""Order channel. Outside the sim, everyone appends rows. C2 delivers them."""

from __future__ import annotations

KINDS = ("plot_course", "set_speed", "join_formation", "leave_formation", "track")


def submit(world, order: dict) -> dict:
    if order.get("kind") not in KINDS:
        raise ValueError(f"unknown order kind {order.get('kind')}")
    row = {
        "id": order["id"],
        "issuer": order.get("issuer", "player"),
        "entity_id": order["entity_id"],
        "issued_tick": world.tick,
        "kind": order["kind"],
        "course": order.get("course") or [],
        "speed_mmps": order.get("speed_mmps"),
        "formation_id": order.get("formation_id"),
        "status": "pending",
    }
    world.orders.append(row)
    return row
