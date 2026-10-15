"""A battle is a shot or a death between two sides at war. A detection is not a battle."""

from pathlib import Path

from sim.campaign.load import load_campaign
from sim.campaign.step import step_day, write_aar


def test_a_shot_without_a_war_does_not_open_a_battle(tmp_path):
    c = load_campaign(Path("scenarios/europe_africa"))
    step_day(c)
    assert c.battles == []
    out = tmp_path / "aar.json"
    write_aar(c, out)
    assert __import__("json").loads(out.read_text())["battles"] == []


def test_a_resolved_shot_between_warring_sides_opens_a_battle_and_invents_no_title():
    c = load_campaign(Path("scenarios/europe_africa"))
    c.at_war = [["europe", "africa"]]
    step_day(c)
    assert len(c.battles) == 1
    battle = c.battles[0]
    assert battle["id"] == "pretoria-0"
    assert battle["place_id"] == "pretoria"
    assert battle["place_name"] == "pretoria-0"
    assert battle["opened_day"] == 0
    assert battle["closed_day"] is None
    assert battle["shots"] >= 1
    assert set(battle["states"]) == {"europe", "africa"}
    assert "eu-inf" in battle["units"]
    assert "af-inf" in battle["units"]
    sentence = next(row["sentence"] for row in c.events if row["kind"] == "battle_open")
    assert sentence == "Battle pretoria-0 opened."
    for banned in ("1939", "modern", "lost heart", "Battle of"):
        assert banned not in sentence
