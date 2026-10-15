"""Theater of War sheet, July 1942. A position is stored only after the mark sat on the letters."""

from pathlib import Path

import yaml

from sim.campaign.step import step_day
from tests.test_cell_map import _campaign

PATH = Path("catalogs/cells/ngs_theater_1942.yaml")

# Measured on docs/sources/evidence/yale-15258797.jpg, 8096 by 9420.
# Origin is the 0 tick of the printed kilometer bar. 1000 km is 795.5 px.
CELLS = [
    ("BAFFIN BAY", "sea", 1693274670, -3431552483),
    ("EGYPT", "land", 4483022726, 3435623575),
    ("HUDSON BAY", "sea", -81332495, -3433186675),
    ("HUNGARY", "land", 3708108108, 1209050911),
]

ABSENT = [
    "ALGERIA",
    "ARCTIC OCEAN",
    "BAY OF BISCAY",
    "BLACK SEA",
    "FINLAND",
    "FRANCE",
    "GERMANY",
    "GREENLAND",
    "NEWFOUNDLAND",
    "coast",
]


def test_theater_sheet_stores_only_marks_that_sat_on_the_letters():
    data = yaml.safe_load(PATH.read_text())
    assert data["title"] == "THEATER OF WAR IN EUROPE AFRICA AND WESTERN ASIA"
    assert data["scale"] == "1:15,000,000 or 236.7 miles to the inch"
    assert data["date"] == "July, 1942"
    assert data["origin"]["tick"] == "0 kilometers"
    assert data["origin"]["x_positive"] == "image right"
    assert data["origin"]["y_positive"] == "image down"
    rows = data["cells"]
    assert [(row["name"], row["surface"], row["x_mm"], row["y_mm"]) for row in rows] == CELLS
    assert all(isinstance(row["x_mm"], int) and isinstance(row["y_mm"], int) for row in rows)
    absent = {row["name"] for row in data["absent"]}
    assert set(ABSENT) <= absent
    assert not absent & {row["name"] for row in rows}


def test_a_ground_step_into_a_theater_sea_cell_is_rejected():
    data = yaml.safe_load(PATH.read_text())
    seas = [row for row in data["cells"] if row["surface"] == "sea"]
    assert [row["name"] for row in seas] == ["BAFFIN BAY", "HUDSON BAY"]
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
