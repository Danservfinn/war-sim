"""A 1939 stock cell is a stock. A production series is not. A dot is not a zero."""

from pathlib import Path

import yaml

from sim.campaign.load import load_campaign


ROOT = Path("scenarios/europe_1939")
YEAR = Path("catalogs/year_states/europe_1939.yaml")


def test_end_of_1939_stock_cells_load():
    campaign = load_campaign(ROOT)
    assert campaign.stocks["gb_coal_distributed_1939"] == 14_550_000
    assert campaign.stocks["gb_coal_colliery_1939"] == 5_186_000
    assert campaign.stocks["gb_coke_ovens_1939"] == 487_000
    assert campaign.stocks["gb_coke_gasworks_1939"] == 706_000
    assert campaign.stocks["uk_pyrites_1939"] == 318_000
    assert campaign.stocks["uk_sulphur_for_acid_1939"] == 63_600
    assert campaign.stocks["uk_spent_oxide_1939"] == 74_600
    assert campaign.stocks["uk_sulphuric_acid_1939"] == 65_500
    assert campaign.stocks["uk_industrial_alcohol_1939"] == 1_900_000
    assert campaign.stocks["uk_scrap_1939"] == 282_300
    assert "gb_coal_1939" not in campaign.stocks
    assert "uk_aluminium_1939" not in campaign.stocks


def test_the_yaml_keeps_the_printed_figure_and_refuses_dots():
    rows = {row["id"]: row for row in yaml.safe_load(YEAR.read_text())["stocks"]}
    assert rows["gb_coal_distributed_1939"]["printed"] == 14550
    assert rows["gb_coal_distributed_1939"]["unit"] == "thousand_tons"
    assert rows["gb_coal_distributed_1939"]["dated"] == "1939"
    assert rows["uk_industrial_alcohol_1939"]["printed"] == "1.90"
    assert rows["uk_industrial_alcohol_1939"]["unit"] == "million_bulk_gallons"
    assert all(row.get("printed") not in (".", "..", "-", "—") for row in rows.values())
    assert all("1940" not in row["id"] for row in rows.values())
