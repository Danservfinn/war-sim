"""Africa 1943 sheet. A position is stored only after the ink mark was seen on the name."""

from pathlib import Path

import yaml

from sim.campaign.step import step_day
from tests.test_cell_map import CELL, _campaign

PATH = Path("catalogs/cells/ngs_africa_1943.yaml")

SEAS = {
    "ATLANTIC OCEAN": (-5918801502, -7745247376),
    "BLACK SEA": (-1494310559, -8117545342),
    "GULF OF GUINEA": (-4172336754, -3554751283),
}


def test_verified_sea_cells_keep_the_measured_points():
    data = yaml.safe_load(PATH.read_text())
    seas = {row["name"]: row for row in data["cells"] if row["surface"] == "sea"}
    assert set(seas) == set(SEAS)
    for name, (x_mm, y_mm) in SEAS.items():
        assert seas[name]["x_mm"] == x_mm
        assert seas[name]["y_mm"] == y_mm
    absent = {item["name"] for item in data["absent"]}
    assert "ATLANTIC OCEAN" not in absent
    assert "BLACK SEA" not in absent
    assert "TYRRHENIAN SEA" in absent


def test_a_ground_step_through_every_positioned_sea_is_rejected():
    data = yaml.safe_load(PATH.read_text())
    seas = [row for row in data["cells"] if row["surface"] == "sea"]
    assert len(seas) == len(SEAS)
    for sea in seas:
        campaign = _campaign()
        campaign.cells = [sea]
        campaign.units[0]["x_mm"] = sea["x_mm"] - CELL
        campaign.units[0]["y_mm"] = sea["y_mm"]
        campaign.march_orders[0]["course"] = [{
            "x_mm": sea["x_mm"] + CELL,
            "y_mm": sea["y_mm"],
            "cell_id": sea["id"],
        }]
        step_day(campaign)
        assert campaign.units[0]["x_mm"] == sea["x_mm"] - CELL
        assert campaign.march_orders[0].get("gate") == "no_surface"
