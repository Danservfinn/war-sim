"""One radar-missile aircraft against one optical-gun aircraft. Same formula. No year field."""

from pathlib import Path

from sim.campaign.load import load_campaign
from sim.campaign.step import step_day

ROOT = Path("scenarios/air_band")


def test_radar_missile_spends_a_kit_inside_the_legal_band_and_the_optical_integrity_hits_zero():
    c = load_campaign(ROOT)
    by_id = {row["id"]: row for row in c.units}
    radar = by_id["radar_missile"]
    optical = by_id["optical_gun"]
    for unit in (radar, optical):
        assert "year" not in unit
        assert "civil_year" not in unit
        assert "as_of" not in unit
        assert "modern" not in unit
    radar_kits = radar["WeaponMount"][0]["ammo"][0]["qty"]
    optical_kits = optical["WeaponMount"][0]["ammo"][0]["qty"]
    step_day(c)
    spent_radar = radar_kits - radar["WeaponMount"][0]["ammo"][0]["qty"]
    spent_optical = optical_kits - optical["WeaponMount"][0]["ammo"][0]["qty"]
    distance_m = 1
    legal = [
        band for band in radar["WeaponMount"][0]["range_bands"]
        if distance_m <= int(band["max_m"])
    ]
    assert legal
    assert spent_radar == 1
    assert spent_optical == 1
    assert optical["Physical"]["integrity"] == 0
    assert radar["Physical"]["integrity"] > 0
    assert any(row["kind"] == "death" and row["sentence"] == "optical_gun was no longer alive." for row in c.events)
    assert not any("1939" in row["sentence"] or "modern" in row["sentence"] for row in c.events)
