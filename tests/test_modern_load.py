"""The modern folder is two factions and the cited plants. It is not a second army."""

from pathlib import Path

from sim.campaign.load import load_campaign
from sim.campaign.step import step_day

ROOT = Path("scenarios/europe_1939_africa_modern")


def test_modern_folder_loads_two_sides_and_does_not_invent_a_force():
    c = load_campaign(ROOT)
    assert c.goods_cross is False
    assert set(c.factions) == {"europe", "africa"}
    assert c.at_war == [["europe", "africa"]]
    assert c.units == []
    assert c.points == []
    plants = {row["id"]: row for row in c.plants}
    assert set(plants) == {"rdm_boksburg", "rdm_somerset"}
    assert plants["rdm_boksburg"]["side"] == "africa"
    assert plants["rdm_somerset"]["side"] == "africa"
    assert plants["rdm_boksburg"]["lines"][0]["daily_cap"] == 277
    assert plants["rdm_somerset"]["lines"][0]["daily_cap"] == 1111
    assert not any(int(node.get("stock_t") or 0) for node in c.nodes)
    step_day(c)
    assert all(row.get("military_out") == 0 for row in c.plants)
