"""A stored series survives the loader. This is not a prediction."""

from pathlib import Path

import yaml

from sim.campaign.load import load_campaign
from sim.campaign.step import prediction_refusals

ROOT = Path(__file__).resolve().parents[1]
SERIES_ID = "pt_tungsten_concentrates_1939"


def test_a_stored_series_survives_the_loader_and_the_gate_stays_shut():
    state = yaml.safe_load((ROOT / "catalogs/year_states/europe_1939.yaml").read_text())
    stored = next(row for row in state["series"] if row["id"] == SERIES_ID)
    c = load_campaign(ROOT / "scenarios/supply_check")
    loaded = next(row for row in c.series if row["id"] == SERIES_ID)
    assert c.goods_cross is False
    assert loaded["annual_t"] == stored["annual_t"]
    assert prediction_refusals() == (
        "fronts", "pockets", "beachheads", "lifts", "full_simulation",
    )
