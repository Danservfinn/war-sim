"""Air gates and fuel. A failed gate does not shoot. No combat outcome is invented."""

from sim.systems.air import first_gate, guidance_input, sortie_ml


def _wing():
    return {
        "id": "wing",
        "side": "de",
        "alive": True,
        "domain": "air",
        "fuel_grade": "avgas",
        "burn_ml_per_km": {"low": 2000},
        "reserve_ml": 500,
        "Crew": {"billets": [{"role": "pilot", "count": 1, "trained_days": 0}]},
    }


def _general():
    return {
        "id": "gen", "name": "Fixture", "state": "de", "from_day": 0, "to_day": 2,
        "source": "fixture", "captured": False, "command": ["wing"],
    }


def _ready():
    return {
        "generals": [_general()],
        "fuel": {"avgas": 9000, "diesel": 9000},
        "field": {"airfield": True, "surface": "land", "damage_milli": 0},
        "weather": {"ceiling_m": 5000},
    }


def test_hold_spends_nothing_and_does_not_shoot():
    wing = _wing()
    gate = first_gate(
        wing,
        mission={"kind": "cap", "signer": "gen", "altitude": "low"},
        doctrine={"wcs": "hold"},
        day=0,
        **_ready(),
    )
    assert gate == "wcs_hold"
    assert wing.get("sortie_flown") is not True
    assert "shots" not in wing


def test_no_signer_beats_a_later_fuel_failure():
    wing = _wing()
    wing["fuel_grade"] = "diesel"
    gate = first_gate(
        wing,
        mission={"kind": "cap", "altitude": "low"},
        doctrine={"wcs": "free"},
        day=0,
        generals=[],
        fuel={"diesel": 0},
    )
    assert gate == "no_signer"


def test_wrong_fuel_grade_does_not_burn():
    wing = _wing()
    pool = {"diesel": 9000, "avgas": 0}
    gate = first_gate(
        wing,
        mission={"kind": "cap", "signer": "gen", "distance_mm": 1_000_000, "altitude": "low"},
        doctrine={"wcs": "free"},
        day=0,
        generals=[_general()],
        fuel=pool,
        field={"airfield": True, "surface": "land", "damage_milli": 0},
        weather={"ceiling_m": 5000},
    )
    assert gate == "no_fuel"
    assert pool["diesel"] == 9000
    assert pool["avgas"] == 0


def test_sortie_fuel_is_two_legs_plus_reserve():
    assert sortie_ml(distance_mm=2_000_000, burn_ml_per_km=3000, reserve_ml=400) == 2_000_000 * 3000 // 1_000_000 * 2 + 400


def test_a_missing_guidance_row_is_zero_not_a_free_hit():
    assert guidance_input({"guidance": "radar"}) == 0
    assert guidance_input({"guidance": "none"}) == 1000
