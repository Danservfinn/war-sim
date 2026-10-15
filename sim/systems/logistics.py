"""Path-minimum supply. Geography is link data. No region branch."""

from __future__ import annotations


def link_delivery(cargo_t: int, capacity_t: int, self_consume_milli: int) -> int:
    moved = min(int(cargo_t), int(capacity_t))
    kept = 1000 - int(self_consume_milli)
    if kept <= 0 or moved <= 0:
        return 0
    return moved * kept // 1000


def path_delivery(source_t: int, links: list[dict]) -> int:
    cargo = int(source_t)
    for link in links:
        cargo = link_delivery(cargo, link["capacity_t"], link["self_consume_milli"])
    return cargo


def can_build(recipe: dict, capabilities: list[str], stocks: dict) -> int:
    missing = [req for req in recipe.get("requires") or [] if req not in capabilities]
    if missing:
        return 0
    runs = None
    for good, need in (recipe.get("inputs") or {}).items():
        have = int(stocks.get(good, 0)) // int(need)
        runs = have if runs is None else min(runs, have)
    return 0 if runs is None else runs


def sustainment(source_t: int, links: list[dict], front_burn_t: int) -> dict:
    arrived = path_delivery(source_t, links)
    burn = int(front_burn_t)
    binding = min(links, key=lambda link: (int(link["capacity_t"]), links.index(link)))["id"] if links else None
    return {
        "produced_t": int(source_t),
        "arrived_t": arrived,
        "throughput_milli": (arrived * 1000 // int(source_t)) if source_t else 0,
        "days_of_supply": (arrived // burn) if burn else 0,
        "binding_link": binding,
    }
