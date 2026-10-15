"""A general is a name, an office, and a dated tenure on one page. A month is not a day. A later page does not finish the tenure."""

from pathlib import Path

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
