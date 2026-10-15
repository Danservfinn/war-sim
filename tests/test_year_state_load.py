"""Year-state load. An empty source fails. The tick gets no year pointer."""

from pathlib import Path

import pytest
import yaml

from sim.campaign.load import load_campaign
from sim.campaign.step import Campaign, step_day


def _write(path: Path, row: dict) -> None:
    path.write_text(yaml.safe_dump(row, sort_keys=False))


def _fixture(tmp_path: Path, year_state: dict, scenario=None) -> Path:
    _write(tmp_path / "catalog.yaml", {"plants": []})
    _write(tmp_path / "factions.yaml", {"factions": {"a": {"cohesion": 50}}})
    _write(tmp_path / "units.yaml", {"units": []})
    _write(tmp_path / "points.yaml", {"points": []})
    _write(tmp_path / "industry.yaml", {})
    _write(tmp_path / "year_state.yaml", year_state)
    meta = {
        "id": "fixture",
        "catalog": str(tmp_path / "catalog.yaml"),
        "viewer_side": "a",
        "year_states": ["year_state.yaml"],
    }
    meta.update(scenario or {})
    _write(tmp_path / "scenario.yaml", meta)
    return tmp_path


def test_empty_source_refuses_the_load(tmp_path):
    root = _fixture(tmp_path, {"id": "bare", "source": "", "states": ["a"]})
    with pytest.raises(ValueError, match="source"):
        load_campaign(root)


def test_counted_row_with_empty_source_refuses_the_load(tmp_path):
    root = _fixture(tmp_path, {
        "id": "bare",
        "source": "fixture page 1",
        "states": ["a"],
        "leaders": [{"id": "gap", "name": "Gap", "source": ""}],
    })
    with pytest.raises(ValueError, match="source"):
        load_campaign(root)


def test_sourced_row_loads_without_a_year_pointer(tmp_path):
    root = _fixture(tmp_path, {
        "id": "ys",
        "region": "europe",
        "civil_year": 1939,
        "as_of": "1939-09-01",
        "source": "fixture page 1",
        "goods_cross": True,
        "states": ["a"],
        "leaders": [{
            "id": "ldr",
            "name": "Named",
            "office": "Office",
            "state": "a",
            "source": "fixture page 1",
        }],
    })
    campaign = load_campaign(root)
    assert campaign.leaders[0]["id"] == "ldr"
    assert not hasattr(campaign, "civil_year")
    assert not hasattr(campaign, "as_of")
    assert not hasattr(campaign, "region")
    assert campaign.goods_cross is False
    campaign.research = [{"id": "seeker", "unlocked": True}]
    step_day(campaign)
    assert campaign.research[0]["unlocked"] is False
    assert "civil_year" not in Path("sim/campaign/step.py").read_text()


def test_scenario_goods_cross_is_not_opened_by_the_year_state(tmp_path):
    root = _fixture(
        tmp_path,
        {"id": "ys", "source": "fixture page 1", "states": ["a"], "goods_cross": True},
        {"goods_cross": True},
    )
    assert load_campaign(root).goods_cross is True


def test_two_year_states_cannot_share_a_state_id(tmp_path):
    _write(tmp_path / "catalog.yaml", {"plants": []})
    _write(tmp_path / "factions.yaml", {"factions": {"a": {}}})
    _write(tmp_path / "units.yaml", {"units": []})
    _write(tmp_path / "points.yaml", {"points": []})
    _write(tmp_path / "industry.yaml", {})
    _write(tmp_path / "one.yaml", {"id": "one", "source": "page 1", "states": ["shared"]})
    _write(tmp_path / "two.yaml", {"id": "two", "source": "page 2", "states": ["shared"]})
    _write(tmp_path / "scenario.yaml", {
        "id": "fixture",
        "catalog": str(tmp_path / "catalog.yaml"),
        "year_states": ["one.yaml", "two.yaml"],
    })
    with pytest.raises(ValueError, match="state"):
        load_campaign(tmp_path)


def test_strength_count_does_not_spawn_a_formation(tmp_path):
    root = _fixture(tmp_path, {
        "id": "ys",
        "source": "fixture page 1",
        "states": ["a"],
        "units": [{
            "id": "uk_armed_forces_1939_09",
            "kind": "strength",
            "total": 1270,
            "source": "digest table 10",
        }],
    })
    campaign = load_campaign(root)
    assert campaign.units == []


def test_1944_rate_is_not_a_1939_cap(tmp_path):
    root = _fixture(tmp_path, {
        "id": "ys",
        "civil_year": 1939,
        "source": "fixture page 1",
        "states": ["a"],
        "plants": [{
            "id": "later",
            "year": 1944,
            "daily_cap": 9,
            "source": "a 1944 page",
        }],
    })
    campaign = load_campaign(root)
    assert campaign.plants == []
    assert not hasattr(campaign, "civil_year")


def test_national_output_is_not_a_stock_or_a_plant(tmp_path):
    root = _fixture(tmp_path, {
        "id": "ys",
        "source": "fixture page 1",
        "states": ["a"],
        "series": [{
            "id": "gb_coal_1939",
            "kind": "national_output",
            "not_a_plant": True,
            "not_a_stock": True,
            "annual_t": 231338,
            "source": "digest table 73",
        }],
    })
    campaign = load_campaign(root)
    assert campaign.plants == []
    assert campaign.stocks == {}


def test_plant_with_empty_input_stock_mints_zero():
    campaign = Campaign(
        day=0,
        nodes=[],
        refiners=[],
        plants=[{
            "id": "yard",
            "side": "a",
            "continent": "europe",
            "input_good": "steel",
            "input_per": 1,
            "strain_milli": 0,
            "dud_base": 10,
            "skilled_labor": 1,
            "power_mw": 10,
            "tools": 1,
            "civilian_share_milli": 0,
            "lines": [{
                "id": "line",
                "output": "shell",
                "daily_cap": 4,
                "powder_local": True,
                "power_mw_need": 1,
                "tools_need": 1,
                "skilled_need": 1,
                "damage_milli": 0,
            }],
        }],
        lots=[],
        fleets={},
        links=[],
        in_transit=[],
        imports=[],
        factions={"a": {
            "cohesion": 50, "manpower": 1, "trainees": 0, "training_cap_per_day": 0,
            "food_t": 1, "food_burn_t": 0, "water_t": 0, "water_burn_t": 0,
            "fuel": {}, "loss_hold_days": 0, "cohesion_loss_per_day": 0, "stockpile": {},
        }},
        victory_rules=[],
        history=[],
        victory=None,
        stocks={},
        units=[],
        points=[],
        continent_stocks={"europe": {}},
    )
    step_day(campaign)
    assert campaign.plants[0]["military_out"] == 0
    assert sum(int(lot["qty"]) for lot in campaign.lots) == 0


def test_europe_1939_scenario_loads_the_catalog_without_a_year_pointer():
    root = Path(__file__).resolve().parents[1] / "scenarios" / "europe_1939"
    campaign = load_campaign(root)
    assert any(row["id"] == "de_hitler" for row in campaign.leaders)
    assert not hasattr(campaign, "civil_year")
    assert not hasattr(campaign, "as_of")
    assert not hasattr(campaign, "region")
    assert campaign.goods_cross is False
    assert campaign.plants == []
    assert campaign.stocks == {}
    assert campaign.units == []
    coke = next(row for row in campaign.series if row["id"] == "gb_coke_1939")
    assert "civil_year" not in coke
    assert coke["annual_thousand_tons"] == 24226
    rifle = yaml.safe_load((root.parent / "europe_africa" / "scenario.yaml").read_text())
    assert "year_states" not in rifle


def test_later_war_loads_both_catalogs_and_keeps_the_wall_shut():
    root = Path(__file__).resolve().parents[1] / "scenarios" / "europe_1939_africa_modern"
    campaign = load_campaign(root)
    assert campaign.goods_cross is False
    assert not hasattr(campaign, "civil_year")
    assert any(row["id"] == "de_hitler" for row in campaign.leaders)
    assert any(row["id"] == "za_ramaphosa" for row in campaign.leaders)
    assert campaign.plants == []
    assert campaign.stocks == {}
    assert "gb_coke_1939" in {row["id"] for row in campaign.series}
