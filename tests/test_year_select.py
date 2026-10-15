"""Plants, stocks, and units come from one year-state. The other catalog is not mixed in."""

import pytest

from sim.campaign.load import select_year_catalog


def test_europe_1939_is_not_the_africa_catalog():
    europe = select_year_catalog("europe_1939")
    africa = select_year_catalog("africa_2024")
    assert europe["id"] == "europe_1939"
    assert africa["id"] == "africa_2024"
    assert europe["plants"] == []
    assert africa["plants"] == []
    assert europe["units"] == []
    assert "za_ramaphosa" not in {row["id"] for row in europe["leaders"]}
    assert "de_hitler" not in {row["id"] for row in africa["leaders"]}


def test_the_loader_refuses_to_mix_the_two_year_states():
    with pytest.raises(ValueError, match="mixed year-states"):
        select_year_catalog("europe_1939", also="africa_2024")
