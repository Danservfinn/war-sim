"""High-resolution NGS Europe sheet. A position is stored only after the mark sat on the letters."""

from pathlib import Path

import yaml

from sim.campaign.step import step_day
from tests.test_cell_map import _campaign

PATH = Path("catalogs/cells/ngs_europe_1939.yaml")

# Measured on docs/sources/evidence/uwm-agdm-32265-ngs-1939.jpg, 9000 by 6602.
# Origin is the 0 tick of the kilometres bar. 300 km is 570.12 px on this scan.
# y positive is south. Image down is south.
CELLS = [
    ("BAY OF BISCAY", "sea", 418043570, -1717796253),
    ("KATTEGAT", "sea", 1623579246, -2844927384),
]

ABSENT = [
    "NORTH SEA",
    "DENMARK",
    "GREAT BRITAIN",
    "LATVIA",
    "ENGLISH CHANNEL",
    "MEDITERRANEAN SEA",
    "ATLANTIC",
    "BLACK SEA",
    "ALGERIA",
    "TUNISIA",
    "LIBYA",
    "YUGOSLAVIA",
    "GREECE",
    "FINLAND",
    "NETHERLANDS",
    "SWEDEN",
    "coast",
]


def test_ngs_europe_sheet_stores_only_marks_that_sat_on_the_letters():
    data = yaml.safe_load(PATH.read_text())
    assert data["title"] == "CENTRAL EUROPE AND THE MEDITERRANEAN"
    assert data["scale"] == "1:5,000,000"
    assert data["date"] == "AS OF AUGUST 28, 1939"
    assert data["origin"]["tick"] == "0 Kilometers"
    assert data["origin"]["x_positive"] == "east"
    assert data["origin"]["y_positive"] == "south"
    assert "916.55" in str(data["origin"]["pixel_x"])
    rows = data["cells"]
    assert [(row["name"], row["surface"], row["x_mm"], row["y_mm"]) for row in rows] == CELLS
    assert all(isinstance(row["x_mm"], int) and isinstance(row["y_mm"], int) for row in rows)
    absent = {row["name"] for row in data["absent"]}
    assert set(ABSENT) <= absent
    assert not absent & {row["name"] for row in rows}


def test_a_ground_step_into_an_ngs_europe_sea_cell_is_rejected():
    data = yaml.safe_load(PATH.read_text())
    seas = [row for row in data["cells"] if row["surface"] == "sea"]
    assert [row["name"] for row in seas] == ["BAY OF BISCAY", "KATTEGAT"]
    for row in seas:
        campaign = _campaign()
        campaign.units[0]["in_bubble"] = True
        campaign.units[0]["speed_mm_per_day"] = 3_000_000
        campaign.units[0]["x_mm"] = row["x_mm"] - 1_000_000
        campaign.units[0]["y_mm"] = row["y_mm"]
        campaign.cells.append({
            "id": row["name"],
            "name": row["name"],
            "surface": "sea",
            "x_mm": row["x_mm"],
            "y_mm": row["y_mm"],
        })
        campaign.march_orders[0]["course"] = [{
            "x_mm": row["x_mm"] + 1_000_000,
            "y_mm": row["y_mm"],
        }]
        step_day(campaign)
        assert campaign.units[0]["x_mm"] == row["x_mm"] - 1_000_000
        assert campaign.march_orders[0].get("gate") == "no_surface"
