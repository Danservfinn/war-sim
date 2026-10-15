"""The rifle step names the gate that bound. A missing node is not a powder failure. A wired plant does not mint steel it cannot draw."""

from pathlib import Path

from sim.campaign.load import load_campaign
from sim.campaign.step import step_day

ROOT = Path("scenarios/europe_africa")


def test_rifle_plants_log_the_gate_that_bound():
    c = load_campaign(ROOT)
    by_id = {plant["id"]: plant for plant in c.plants}
    assert by_id["essen_guns"]["node_id"] == "ruhr_pit"
    assert by_id["essen_guns"]["continent"] == "europe"
    assert not by_id["dicon_kaduna"].get("node_id")
    assert not by_id["rdm_boksburg"].get("node_id")
    step_day(c)
    sentences = [row["sentence"] for row in c.events if row["kind"] == "plant_gate"]
    assert "Plant dicon_kaduna produced 0. Gate powder." in sentences
    assert "Plant rdm_boksburg produced 0. Gate no_access." in sentences
    assert "Plant essen_guns produced 0. Gate no_access." in sentences
    assert all(plant.get("military_out") == 0 for plant in c.plants)
    assert all("made 5" not in row["sentence"] for row in c.events)
