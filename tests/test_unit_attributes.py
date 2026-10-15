"""Unit attributes are copied from a cited row. A missing field stays empty. No integer is invented."""

from pathlib import Path

import pytest
import yaml

from sim.campaign.attributes import (
    guidance_succeeds,
    load_attribute_catalog,
    load_cited_attributes,
    require_cited_attributes,
)


def test_a_missing_cited_source_refuses_the_attribute_table():
    with pytest.raises(ValueError, match="cited source missing"):
        require_cited_attributes([])


def test_a_complete_cited_row_loads_exactly_those_values():
    source = "loader contract. Not a weapon. Not written to the catalog."
    row = load_cited_attributes([{
        "id": "fixture",
        "ammo_parts": "kit-a",
        "guidance_match": 250,
        "penetration": 12,
        "blast": 3,
        "rounds_per_day": 40,
        "source": source,
    }])[0]
    assert row["ammo_parts"] == "kit-a"
    assert row["guidance_match"] == 250
    assert row["penetration"] == 12
    assert row["blast"] == 3
    assert row["rounds_per_day"] == 40
    assert row["source"] == source


def test_a_partial_citation_leaves_the_unstated_fields_empty():
    row = load_cited_attributes([{
        "id": "partial",
        "penetration": 12,
        "source": "partial citation. Not a weapon.",
    }])[0]
    assert row["penetration"] == 12
    assert row["ammo_parts"] in (None, "")
    assert row["guidance_match"] in (None, "")
    assert row["blast"] in (None, "")
    assert row["rounds_per_day"] in (None, "")


def test_a_row_with_no_citation_raises():
    with pytest.raises(ValueError, match="cited source missing"):
        load_cited_attributes([{"id": "ghost", "penetration": 12}])


def test_an_empty_guidance_match_is_not_a_successful_match():
    row = load_cited_attributes([{
        "id": "unguided-unknown",
        "penetration": 12,
        "source": "partial citation. Not a weapon.",
    }])[0]
    assert row["guidance_match"] in (None, "")
    assert guidance_succeeds(row) is False


def test_the_on_disk_catalog_contains_no_invented_integer():
    root = Path(__file__).resolve().parents[1]
    raw = yaml.safe_load((root / "catalogs/units/attributes.yaml").read_text())
    assert raw["units"] == []
    assert load_attribute_catalog() == []
