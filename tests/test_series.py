"""A national output series is a series. An estimate mark is a refusal. A footnote with unread text is a refusal."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_a_clean_country_cell_is_a_series_and_a_marked_cell_is_not():
    europe = yaml.safe_load((ROOT / "catalogs/year_states/europe_1939.yaml").read_text())
    rows = {r["id"]: r for r in europe["series"]}

    # Netherlands zinc 1939, clean cell. Bureau of Mines zinc table, printed page 143.
    assert rows["nl_zinc_slab_1939"]["state"] == "netherlands"
    assert rows["nl_zinc_slab_1939"]["annual_t"] == 20534
    assert rows["nl_zinc_slab_1939"]["per_360_t"] == 57
    assert rows["nl_zinc_slab_1939"]["remainder_t"] == 14

    # Switzerland virgin aluminium 1939, clean cell. Printed page 654.
    assert rows["ch_virgin_aluminium_1939"]["annual_t"] == 28000
    assert rows["ch_virgin_aluminium_1939"]["per_360_t"] == 77
    assert rows["ch_virgin_aluminium_1939"]["remainder_t"] == 280

    # Portugal tungsten concentrates 1939, clean cell. Printed page 639.
    assert rows["pt_tungsten_concentrates_1939"]["annual_t"] == 3851
    assert rows["pt_tungsten_concentrates_1939"]["per_360_t"] == 10
    assert rows["pt_tungsten_concentrates_1939"]["remainder_t"] == 251

    # Refused: UK zinc 50,440 carries a footnote mark whose text the OCR dropped.
    text = (ROOT / "catalogs/year_states/europe_1939.yaml").read_text()
    assert "50,440" not in text


def test_africa_worldsteel_national_rows():
    africa = yaml.safe_load((ROOT / "catalogs/year_states/africa_2024.yaml").read_text())
    rows = {r["id"]: r for r in africa["series"]}
    assert rows["eg_crude_steel_2024"]["annual_t"] == 10700000
    assert rows["eg_crude_steel_2024"]["per_360_t"] == 29722
    assert rows["eg_crude_steel_2024"]["remainder_t"] == 80
    assert rows["za_crude_steel_2024"]["annual_t"] == 4700000
    assert rows["za_crude_steel_2024"]["per_360_t"] == 13055
    assert rows["za_crude_steel_2024"]["remainder_t"] == 200
    assert rows["dz_crude_steel_2024"]["annual_t"] == 4500000
    assert rows["dz_crude_steel_2024"]["per_360_t"] == 12500
    assert rows["dz_crude_steel_2024"]["remainder_t"] == 0
    # The group row keeps its own identity and is not a national row.
    assert rows["africa_six_crude_steel_2024"]["kind"] == "group_total"
    # Libya, Morocco, Tunisia have no own row on the page. Not computed.
    assert "ly_crude_steel_2024" not in rows
    assert "ma_crude_steel_2024" not in rows
    assert "tn_crude_steel_2024" not in rows
