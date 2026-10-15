"""Measured cells are the geographic layer. No invented position."""

import pytest

from sim.campaign.step import prediction_refusals, step_day
from sim.spatial.cells import geographic_layer, load_measured_cells, use_year_state_cells
from tests.test_cell_map import _campaign


def _positioned(rows, surface):
    return [
        row for row in rows
        if row.get("surface") == surface
        and isinstance(row.get("x_mm"), int)
        and isinstance(row.get("y_mm"), int)
    ]


def test_loader_reads_only_measured_cells():
    rows = load_measured_cells()
    catalogs = {row["catalog"] for row in rows}
    assert "bartholomew_1939.yaml" in catalogs
    assert "ngs_theater_1942.yaml" in catalogs
    assert "cia_africa_pol.yaml" in catalogs
    assert "ngs_africa_1943.yaml" in catalogs
    assert "ngs_1939_08_28.yaml" not in catalogs
    assert "europe_mediterranean.yaml" not in catalogs
    assert all(isinstance(row["x_mm"], int) and isinstance(row["y_mm"], int) for row in rows)
    assert _positioned(rows, "land")
    assert _positioned(rows, "sea")


def test_a_ground_step_into_a_measured_sea_cell_is_rejected():
    sea = _positioned(geographic_layer("europe_1939"), "sea")[0]
    campaign = _campaign()
    campaign.cells = [sea]
    campaign.units[0]["in_bubble"] = True
    campaign.units[0]["speed_mm_per_day"] = 2_000_000
    campaign.units[0]["x_mm"] = sea["x_mm"] - 1_000_000
    campaign.units[0]["y_mm"] = sea["y_mm"]
    campaign.march_orders[0]["course"] = [{
        "x_mm": sea["x_mm"] + 1_000_000,
        "y_mm": sea["y_mm"],
    }]
    step_day(campaign)
    assert campaign.units[0]["x_mm"] == sea["x_mm"] - 1_000_000
    assert campaign.units[0]["y_mm"] == sea["y_mm"]
    assert campaign.march_orders[0].get("gate") == "no_surface"


def test_a_ground_step_that_leaves_every_measured_land_cell_is_rejected():
    land = _positioned(geographic_layer("europe_1939"), "land")
    assert land
    home = land[0]
    campaign = _campaign()
    campaign.cells = list(land)
    campaign.units[0]["in_bubble"] = False
    campaign.units[0]["x_mm"] = home["x_mm"]
    campaign.units[0]["y_mm"] = home["y_mm"]
    campaign.march_orders[0]["course"] = [{
        "x_mm": home["x_mm"] + 50_000_000,
        "y_mm": home["y_mm"],
    }]
    step_day(campaign)
    assert campaign.units[0]["x_mm"] == home["x_mm"]
    assert campaign.units[0]["y_mm"] == home["y_mm"]
    assert campaign.march_orders[0].get("gate") == "no_surface"


def test_1939_cells_are_not_usable_under_modern_africa_and_vice_versa():
    europe = geographic_layer("europe_1939")
    africa = geographic_layer("africa_2024")
    assert _positioned(europe, "land") and _positioned(europe, "sea")
    assert _positioned(africa, "land") and _positioned(africa, "sea")
    assert {row["catalog"] for row in europe}.isdisjoint({row["catalog"] for row in africa})
    assert all(row["year_state"] == "europe_1939" for row in europe)
    assert all(row["year_state"] == "africa_2024" for row in africa)
    with pytest.raises(ValueError, match="year-state"):
        use_year_state_cells("africa_2024", europe)
    with pytest.raises(ValueError, match="year-state"):
        use_year_state_cells("europe_1939", africa)


def test_prediction_gate_refuses_fronts_and_beachheads_when_cells_exist():
    europe = geographic_layer("europe_1939")
    africa = geographic_layer("africa_2024")
    assert _positioned(europe, "land") and _positioned(europe, "sea")
    assert _positioned(africa, "land") and _positioned(africa, "sea")
    refused = prediction_refusals({
        "europe_1939": europe,
        "africa_2024": africa,
    })
    assert "fronts" in refused
    assert "beachheads" in refused
    assert "pockets" in refused
    assert "lifts" in refused
    assert "full_simulation" in refused


def test_an_empty_year_state_keeps_the_prediction_refusal():
    europe = geographic_layer("europe_1939")
    refused = prediction_refusals({
        "europe_1939": europe,
        "africa_2024": [],
    })
    assert refused == ("fronts", "pockets", "beachheads", "lifts", "full_simulation")
