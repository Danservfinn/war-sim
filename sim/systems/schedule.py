"""Intra-tick schedule. Systems declare cadence. They do not branch on era."""

from __future__ import annotations

from sim.constants import DAY, TICK_ORDER


class System:
    name = "system"
    reads: tuple[str, ...] = ()
    writes: tuple[str, ...] = ()
    cadence_days = DAY

    def due(self, day: int, in_bubble: bool = False) -> bool:
        return day % self.cadence_days == 0

    def tick(self, world, bubble_ids: list[str]) -> None:
        return None


class Detection(System):
    name = "detection"
    reads = ("Sensor", "Physical", "Position")
    writes = ("Track",)
    cadence_days = DAY


class Movement(System):
    name = "movement"
    reads = ("Mobility", "Position", "Logistics")
    writes = ("Position", "Logistics")
    cadence_days = DAY


class C2(System):
    name = "c2"
    reads = ("Comms", "Order")
    writes = ("Order",)
    cadence_days = DAY


class Combat(System):
    name = "combat"
    reads = ("WeaponMount", "Physical", "Crew", "Defenses")
    writes = ("Physical", "Crew", "Logistics")
    cadence_days = DAY

    def tick(self, world, bubble_ids: list[str]) -> None:
        # Point defense before impact is a later combat pass. Scaffold does not roll damage.
        return None


class Logistics(System):
    name = "logistics"
    reads = ("Logistics", "Industry")
    writes = ("Logistics",)
    cadence_days = DAY


class Production(System):
    name = "production"
    reads = ("Industry",)
    writes = ("Industry",)
    cadence_days = DAY


def schedule() -> list[System]:
    systems: list[System] = [Detection(), Movement(), C2(), Combat(), Logistics(), Production()]
    by_name = {s.name: s for s in systems}
    return [by_name[name] for name in TICK_ORDER]
