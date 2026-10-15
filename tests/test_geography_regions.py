"""Continuous color from the cited sheet. A vertex without a pixel is not a measurement."""

from pathlib import Path

import pytest

from sim.spatial.regions import ground_step, load_regions


ROOT = Path(__file__).resolve().parents[1]
TOLERANCE_PX = 2


def test_a_traced_polygon_loads_with_origin_scale_and_provenance():
    rows = load_regions()
    assert rows, "no traced polygon"
    row = rows[0]
    assert row["image"]
    assert (ROOT / row["image"]).exists()
    assert row["origin_px"][0] is not None
    assert row["mm_per_px"] > 0
    assert row["vertices"]
    for vertex in row["vertices"]:
        assert type(vertex["px"]) is int
        assert type(vertex["py"]) is int
        assert type(vertex["x_mm"]) is int
        assert type(vertex["y_mm"]) is int
        assert vertex["source"]


def test_second_tracing_matches_within_tolerance():
    rows = load_regions()
    assert rows
    for row in rows:
        assert row["tolerance_px"] <= TOLERANCE_PX
        assert row["trace_b_hausdorff_px"] <= row["tolerance_px"]
        assert row["trace_b"]


def test_ground_step_into_a_measured_sea_polygon_is_rejected():
    seas = [row for row in load_regions() if row["surface"] == "sea"]
    assert seas, "no measured sea polygon"
    sea = seas[0]
    assert ground_step(sea["year_state"], sea["seed_x_mm"], sea["seed_y_mm"]) == "no_surface"


def test_no_invented_vertex_in_the_catalog():
    for row in load_regions():
        ox, oy = row["origin_px"]
        scale = row["mm_per_px"]
        y_sign = -1 if row["y_positive"] == "north" else 1
        for vertex in row["vertices"]:
            expect_x = int(round((vertex["px"] - ox) * scale))
            expect_y = int(round((vertex["py"] - oy) * scale * y_sign))
            assert vertex["x_mm"] == expect_x
            assert vertex["y_mm"] == expect_y


def test_cross_year_state_polygons_remain_unbound():
    europe = load_regions("europe_1939")
    africa = load_regions("africa_2024")
    assert africa
    assert {row["sheet"] for row in europe}.issubset({"bartholomew_1939"})
    assert {row["sheet"] for row in africa} == {"cia_africa_pol"}
    assert all(row["year_state"] == "europe_1939" for row in europe)
    assert all(row["year_state"] == "africa_2024" for row in africa)
    unbound = [row for row in load_regions() if row["year_state"] is None]
    bound_sheets = {row["sheet"] for row in europe + africa}
    assert all(row["sheet"] not in bound_sheets for row in unbound)
    assert all(row["sheet"] not in {"ngs_africa_1943", "ngs_theater_1942", "ngs_europe_1939"} for row in europe + africa)
