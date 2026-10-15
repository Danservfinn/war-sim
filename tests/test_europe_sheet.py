"""Europe and the Mediterranean sheet. A printed ratio is not a measured bar."""

from pathlib import Path

import yaml

from sim.campaign.step import step_day
from tests.test_cell_map import _campaign

PATH = Path("catalogs/cells/europe_mediterranean.yaml")

LEGIBLE = [
    "GREAT BRITAIN & NORTHERN IRELAND",
    "SPAIN",
    "GERMANY",
]


def test_europe_sheet_stores_no_invented_position():
    data = yaml.safe_load(PATH.read_text())
    assert data["title"] == "EUROPE AND THE MEDITERRANEAN"
    assert data["scale"] == "1:5,300,000"
    assert data["cells"] == []
    assert all("x_mm" not in row and "y_mm" not in row for row in data["absent"])
    absent = {row["name"]: row for row in data["absent"]}
    for name in LEGIBLE:
        assert name in absent
        assert "unmeasurable" in absent[name]["reason"]
    assert "blue" in absent["GREAT BRITAIN & NORTHERN IRELAND"]["reason"]
    assert "TURKEY" in absent
    assert "POLAND" in absent
    assert "ITALY" in absent
    assert not {row["name"] for row in data["cells"]} & set(absent)


def test_position_gate_still_rejects_a_ground_step_into_sea():
    campaign = _campaign()
    step_day(campaign)
    assert campaign.units[0]["x_mm"] == 0
    assert campaign.march_orders[0].get("gate") == "no_surface"
