"""The authoritative tick is one day."""

from sim.clock.clock import SimClock
from sim.constants import DAY, YEAR_DAYS
from sim.spatial.index import movement_resolution
from sim.systems.schedule import schedule


def test_step_advances_one_day():
    clock = SimClock()
    assert clock.day == 0
    assert clock.step() == 1
    assert clock.day == 1
    assert clock.tick == clock.day


def test_year_is_360_days():
    clock = SimClock()
    clock.step(YEAR_DAYS)
    assert clock.year == 1
    assert clock.month == 0


def test_compression_is_days_per_wall_step():
    clock = SimClock()
    clock.set_compression(7)
    assert clock.quanta_due() == 7
    clock.pause()
    assert clock.quanta_due() == 0


def test_every_system_is_due_every_day():
    for system in schedule():
        assert system.cadence_days == DAY
        assert system.due(0) is True
        assert system.due(359) is True


def test_movement_resolution_is_daily():
    inside = movement_resolution(True)
    outside = movement_resolution(False)
    assert inside["cadence_days"] == 1
    assert outside["cadence_days"] == 1
    assert inside["position"] == "mm"
    assert outside["grid_mm"] == 10_000_000
