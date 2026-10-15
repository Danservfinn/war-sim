"""The prediction gate refuses a war that has no positioned cell."""

from sim.campaign.step import prediction_refusals, write_aar
from tests.test_defect_gates import _bare


def test_unpositioned_cells_refuse_fronts_pockets_beachheads_lifts_and_the_full_sim(tmp_path):
    c = _bare(plants=[], cells=[{"id": "named", "name": "EGYPT", "surface": "land"}])
    refused = prediction_refusals(c.cells)
    assert refused == ("fronts", "pockets", "beachheads", "lifts", "full_simulation")
    out = tmp_path / "aar.json"
    write_aar(c, out)
    import json
    log = json.loads(out.read_text())
    assert log["prediction_gate_met"] is False
    assert log["refused"] == ["fronts", "pockets", "beachheads", "lifts", "full_simulation"]
