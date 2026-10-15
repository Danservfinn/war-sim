"""A general is a name, an office, and a dated tenure on one page. A month is not a day. A later page does not finish the tenure."""

from pathlib import Path

from sim.campaign.load import load_campaign
from sim.campaign.step import _general_seated, step_day

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_one_page_states_the_chair_and_a_split_tenure_does_not():
    europe = yaml.safe_load((ROOT / "catalogs/year_states/europe_1939.yaml").read_text())
    rows = {row["id"]: row for row in europe["generals"]}

    emg = rows["fr_gamelin_emg"]
    assert emg["name"] == "Maurice Gamelin"
    assert emg["office"] == "chef d'État-Major général"
    assert emg["state"] == "france"
    assert emg["from_date"] == "1931-02-09"
    assert "to_date" not in emg
    assert "from_day" not in emg
    assert "command" not in emg

    defense = rows["fr_gamelin_defense_nationale"]
    assert defense["name"] == "Maurice Gamelin"
    assert defense["office"] == "Chef d'état-major de la défense nationale"
    assert defense["from_date"] == "1938-01-21"
    assert "to_date" not in defense

    assert all(row.get("from_date") != "1939-09-01" for row in europe["generals"])
    names = " ".join(row["name"] for row in europe["generals"])
    for banned in ("Ironside", "Gort", "Brauchitsch", "Halder", "Keitel", "Thomas", "Hitler"):
        assert banned not in names

    africa = yaml.safe_load((ROOT / "catalogs/year_states/africa_2024.yaml").read_text())
    assert africa.get("generals", []) == []


def test_loaded_gamelin_rows_do_not_sign_a_march():
    c = load_campaign(ROOT / "scenarios/europe_1939_africa_modern")
    assert len(c.generals) == 2
    assert all(not _general_seated(c, row) for row in c.generals)
    assert all("from_day" not in row and "to_day" not in row and "command" not in row for row in c.generals)
    c.cells = [{
        "id": "pad", "surface": "land", "x_mm": 0, "y_mm": 10_000_000,
        "year_state": "europe_1939", "source": "fixture",
    }]
    c.units = [{
        "id": "walker", "side": "europe", "alive": True, "foot": True,
        "year_state": "europe_1939", "x_mm": 0, "y_mm": 0,
        "speed_mm_per_day": 25_000_000, "in_bubble": False, "equipment": {},
    }]
    c.march_orders = [{
        "id": "march-1", "entity_id": "walker", "issued_day": 0, "active_day": 0,
        "course": [{"x_mm": 0, "y_mm": 10_000_000}], "waypoint": 0,
    }]
    step_day(c)
    assert c.units[0]["y_mm"] == 0
    assert c.march_orders[0].get("gate") == "no_signer"
