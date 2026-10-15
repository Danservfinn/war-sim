"""A listed ship is a unit. A smashed column is not a number. A headcount is not a formation."""

from pathlib import Path

import yaml

from sim.campaign.load import load_campaign


ROOT = Path("scenarios/europe_1939")
YEAR = Path("catalogs/year_states/europe_1939.yaml")

NAMED = {
    "uk_nelson_1939_09": "Nelson",
    "uk_rodney_1939_09": "Rodney",
    "uk_royal_sovereign_1939_09": "Royal Sovereign",
    "uk_royal_oak_1939_09": "Royal Oak",
    "uk_revenge_1939_09": "Revenge",
    "uk_resolution_1939_09": "Resolution",
    "uk_malaya_1939_09": "Malaya",
    "uk_valiant_1939_09": "Valiant",
    "uk_barham_1939_09": "Barham",
    "uk_queen_elizabeth_1939_09": "Queen Elizabeth",
    "uk_renown_1939_09": "Renown",
    "uk_repulse_1939_09": "Repulse",
}


def test_a_name_on_its_own_line_is_stored_and_not_placed():
    rows = {row["id"]: row for row in yaml.safe_load(YEAR.read_text())["units"]}
    for key, name in NAMED.items():
        assert rows[key]["name"] == name
        assert rows[key]["dated"] == "1939-09"
        assert rows[key]["not_placed"] is True
        assert "displacement" not in rows[key]
        assert "x_mm" not in rows[key]
    campaign = load_campaign(ROOT)
    assert campaign.units == []
    assert rows["uk_armed_forces_1939_09"]["kind"] == "strength"


def test_a_garbled_name_and_a_smashed_column_are_absent():
    text = YEAR.read_text()
    for banned in ("Ramilb", "IVarspite", "Tirpitz", "Bismarck", "Scharnhorst", "43 divisions"):
        assert banned not in text
    africa = yaml.safe_load(Path("catalogs/year_states/africa_2024.yaml").read_text())
    rows = {row["id"]: row for row in africa["units"]}
    assert rows["eg_al_aziz_2024"]["name"] == "Al-Aziz"
    assert rows["eg_al_qahhar_2024"]["name"] == "Al-Qahhar"
    assert rows["eg_al_qadeer_2024"]["name"] == "Al-Qadeer"
    assert rows["eg_al_qadeer_2024"]["dated"] == "2024-01-05"
    assert rows["eg_al_qadeer_2024"]["not_placed"] is True
    assert "displacement" not in rows["eg_al_qadeer_2024"]
    assert "Al-Jabbar" not in Path("catalogs/year_states/africa_2024.yaml").read_text()
    assert "King Adam Kok" not in Path("catalogs/year_states/africa_2024.yaml").read_text()
