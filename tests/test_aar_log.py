"""The log quotes shots, deaths, plant gates, and surrender. It invents nothing."""

import json
from pathlib import Path

from sim.campaign.load import load_campaign
from sim.campaign.step import step_until_victory, write_aar


ROOT = Path("scenarios/europe_africa")
RENDER = Path(__file__).resolve().parents[1] / "tools" / "render_aar.py"


def test_rifle_contact_writes_a_surrender_sentence_and_no_story(tmp_path):
    c = load_campaign(ROOT)
    result = step_until_victory(c, limit_days=5)
    assert result["reason"] == "total_surrender"
    kinds = [row["kind"] for row in c.events]
    assert "state_surrender" in kinds
    surrender = next(row for row in c.events if row["kind"] == "state_surrender")
    sentence = surrender["sentence"]
    assert "Points 0" in sentence
    assert "living 0" in sentence
    assert "stock 0" in sentence
    assert "output 0" in sentence
    assert "lost heart" not in sentence
    for row in c.events:
        assert row["sentence"]
        assert "1939" not in row["sentence"]
        assert "modern" not in row["sentence"]
    out = tmp_path / "aar.json"
    write_aar(c, out, stop="victory")
    log = json.loads(out.read_text())
    assert log["scenario_id"] == "europe_africa"
    assert log["prediction_gate_met"] is False
    assert any(row["kind"] == "state_surrender" for row in log["events"])
    page = tmp_path / "aar.html"
    import subprocess
    import sys
    ran = subprocess.run(
        [sys.executable, str(RENDER), "--log", str(out), "--out", str(page)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert ran.returncode == 0
    html = page.read_text()
    assert "Points 0" in html
    assert "not a calibration" in html
    assert "lost heart" not in html
    picture = Path("scenarios/europe_africa/day-1.html")
    assert picture.stat().st_size == 3150
