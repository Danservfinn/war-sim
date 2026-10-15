"""A scenario folder is a war. It ends only in total surrender."""

from pathlib import Path

from sim.campaign.load import load_campaign
from sim.campaign.step import step_day, step_until_victory
from sim.snapshot import map_rows


ROOT = Path("scenarios/europe_africa")


def test_closed_continent_loads_cited_caps():
    c = load_campaign(ROOT)
    caps = {plant["id"]: plant["lines"][0]["daily_cap"] for plant in c.plants}
    assert caps["rdm_boksburg"] == 277
    assert caps["dicon_kaduna"] == 83333
    assert c.plants_by_id["dicon_kaduna"]["lines"][0]["powder_local"] is False
    step_day(c)
    step_day(c)
    assert c.imports[0]["received_t"] == 0


def test_war_ends_in_total_surrender_and_the_map_hides_the_unseen():
    c = load_campaign(ROOT)
    c.units.append({
        "id": "af-far", "side": "africa", "alive": True, "x_mm": 500_000_000, "y_mm": 0,
        "sensor_range_mm": 0, "equipment": {},
    })
    # The far unit is alive, so this step must not be the surrender. It must omit the unit.
    step_day(c)
    rows = map_rows(c, "europe")
    assert all(row["id"] != "af-far" for row in rows)
    assert any(row["id"] == "eu-inf" and row["contact_quality"] == "friendly" for row in rows)

    c = load_campaign(ROOT)
    result = step_until_victory(c, limit_days=5)
    assert result["reason"] == "total_surrender"
    assert result["lost"] == "africa"
    assert result["winner"] == "europe"
    assert c.factions["africa"]["victory_points"] == 0
    end = map_rows(c, "europe")
    assert [row["id"] for row in end] == ["eu-inf"]
