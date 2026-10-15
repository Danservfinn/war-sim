"""A plant row is a stated rate with a speaker, a place, and a date. A series is not a plant."""

from pathlib import Path

import yaml

from sim.campaign.load import load_campaign, select_year_catalog


ROOT = Path("catalogs/year_states")


def test_only_the_opened_rdm_rates_are_plants():
    africa = select_year_catalog("africa_2024")
    europe = select_year_catalog("europe_1939")
    assert europe["plants"] == []
    rows = {row["id"]: row for row in africa["plants"]}
    assert set(rows) == {"rdm_boksburg", "rdm_somerset"}
    boksburg = rows["rdm_boksburg"]
    somerset = rows["rdm_somerset"]
    assert boksburg["place"] == "Boksburg"
    assert boksburg["speaker"] == "Jan-Patrick Helmsen"
    assert boksburg["stated"] == "2023-07-07"
    assert boksburg["annual"] == 100000
    assert boksburg["daily_cap"] == 277
    assert boksburg["remainder"] == 280
    assert boksburg["remainder_is_stock"] is False
    assert somerset["place"] == "Somerset West"
    assert somerset["annual"] == 400000
    assert somerset["daily_cap"] == 1111
    assert somerset["remainder"] == 40
    assert "150000" not in str(boksburg.get("daily_cap"))
    assert boksburg["daily_cap"] != 416
    assert somerset["daily_cap"] != 1666
    assert "factory_300" not in rows
    assert "dicon_kaduna" not in rows
    assert "pmp_pretoria" not in rows
    series = yaml.safe_load((ROOT / "africa_2024.yaml").read_text()).get("series") or []
    series_ids = {row["id"] for row in series}
    assert series_ids.isdisjoint(rows)
    for row in rows.values():
        assert row["state"] == "south_africa"
        assert row["continent"] == "africa"
        assert "defenceWeb" in row["source"]
        assert "http" in row["source"]
        assert row.get("powder_local") is not True


def test_a_missing_powder_statement_is_not_local(tmp_path):
    root = tmp_path
    (root / "catalog.yaml").write_text("plants: []\n")
    (root / "factions.yaml").write_text("factions: {a: {cohesion: 50}}\n")
    (root / "units.yaml").write_text("units: []\n")
    (root / "points.yaml").write_text("points: []\n")
    (root / "industry.yaml").write_text("{}\n")
    (root / "year_state.yaml").write_text(
        "id: ys\n"
        "source: fixture page 1\n"
        "states: [a]\n"
        "plants:\n"
        "  - id: yard\n"
        "    state: a\n"
        "    place: Named\n"
        "    daily_cap: 4\n"
        "    source: a page that does not state powder origin\n"
    )
    (root / "scenario.yaml").write_text(
        f"id: fixture\ncatalog: {root / 'catalog.yaml'}\nviewer_side: a\nyear_states: [year_state.yaml]\n"
    )
    campaign = load_campaign(root)
    assert campaign.plants[0]["lines"][0].get("powder_local") is not True
