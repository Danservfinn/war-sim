"""Shared sim constants. The tick is one day. Positions are integer millimeters."""

STRATEGIC_CELL_MM = 10_000_000
FINE_CELL_MM = 250_000
MIN_BUBBLE_M = 10_000
MAX_BUBBLE_M = 80_000
DAY = 1
MONTH_DAYS = 30
YEAR_DAYS = 360

BUBBLE_QUALITIES = ("detected", "classified", "tracked")
TICK_ORDER = ("detection", "movement", "c2", "combat", "logistics", "production")
