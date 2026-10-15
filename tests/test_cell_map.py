"""Cell map. A course is not a coast. These fail until a cited surface exists."""

from sim.campaign.step import Campaign, step_day


CELL = 10_000_000


def _campaign():
    return Campaign(
        day=0,
        nodes=[],
        plants=[],
        lots=[],
        fleets={},
        links=[],
        in_transit=[],
        imports=[],
        factions={"a": {
            "cohesion": 50, "manpower": 1, "trainees": 0, "training_cap_per_day": 0,
            "food_t": 1, "food_burn_t": 0, "water_t": 0, "water_burn_t": 0,
            "fuel": {}, "loss_hold_days": 0, "cohesion_loss_per_day": 0, "stockpile": {},
        }},
        victory_rules=[],
        history=[],
        victory=None,
        stocks={},
        units=[{
            "id": "mover", "side": "a", "alive": True, "foot": True, "domain": "land",
            "x_mm": 0, "y_mm": 0, "cell_id": "shore",
            "speed_mm_per_day": 25_000_000, "heading": "east",
            "in_bubble": False, "equipment": {},
        }],
        engagements=[],
        cells=[
            {"id": "shore", "surface": "land", "x_mm": 0, "y_mm": 0, "owner": "a",
             "source": "fixture"},
            {"id": "water", "surface": "sea", "x_mm": CELL, "y_mm": 0, "owner": "",
             "source": "fixture"},
            {"id": "far", "surface": "land", "x_mm": 2 * CELL, "y_mm": 0, "owner": "a",
             "source": "fixture"},
        ],
        march_orders=[{
            "id": "march-1",
            "entity_id": "mover",
            "issued_day": 0,
            "active_day": 0,
            "course": [{"x_mm": 2 * CELL, "y_mm": 0, "cell_id": "far"}],
            "waypoint": 0,
        }],
    )


def test_a_ground_unit_does_not_enter_sea():
    campaign = _campaign()
    step_day(campaign)
    assert campaign.units[0]["x_mm"] == 0
    assert campaign.units[0]["cell_id"] == "shore"


def test_a_course_across_sea_is_rejected():
    campaign = _campaign()
    step_day(campaign)
    assert campaign.march_orders[0].get("gate") == "no_surface"
    assert campaign.march_orders[0]["waypoint"] == 0


def test_named_sheet_cells_have_no_invented_position():
    import yaml
    from pathlib import Path
    data = yaml.safe_load(Path("catalogs/cells/ngs_1939_08_28.yaml").read_text())
    rows = data["cells"]
    assert [row["name"] for row in rows] == [
        "NORTH SEA",
        "TYRRHENIAN SEA",
        "GREAT BRITAIN",
        "FRANCE",
        "GERMANY",
        "BAY OF BISCAY",
        "BLACK SEA",
        "IONIAN SEA",
        "KATTEGAT",
        "LIGURIAN SEA",
        "MARMARA DENIZI",
        "SEA OF CANDIA",
        "KRITIKON PELAGOS",
        "EIRE",
        "SWEDEN",
        "DENMARK",
        "LATVIA",
        "LITHUANIA",
        "POLAND",
        "HUNGARY",
        "SWITZERLAND",
        "SPAIN",
        "ITALY",
        "ROMANIA",
        "BULGARIA",
        "MOROCCO",
        "ALGERIA",
        "SARDEGNA (SARDINIA)",
        "CORSE (CORSICA)",
        "CYPRUS",
        "TURKEY",
        "SICILIA",
        "NORWAY",
        "PORTUGAL",
        "SYRIA",
    ]
    assert {row["surface"] for row in rows} == {"land", "sea"}
    assert all(row["source"] and "x_mm" not in row and "y_mm" not in row for row in rows)
    absent = {row["name"] for row in data["absent"]}
    assert "BALTIC SEA" in absent
    assert "MEDITERRANEAN SEA" in absent
    assert not absent & {row["name"] for row in rows}


def test_every_sheet_sea_rejects_a_ground_step():
    import yaml
    from pathlib import Path
    data = yaml.safe_load(Path("catalogs/cells/ngs_1939_08_28.yaml").read_text())
    seas = [row["name"] for row in data["cells"] if row["surface"] == "sea"]
    assert seas == [
        "NORTH SEA",
        "TYRRHENIAN SEA",
        "BAY OF BISCAY",
        "BLACK SEA",
        "IONIAN SEA",
        "KATTEGAT",
        "LIGURIAN SEA",
        "MARMARA DENIZI",
        "SEA OF CANDIA",
        "KRITIKON PELAGOS",
    ]
    for name in seas:
        campaign = _campaign()
        campaign.cells[1]["name"] = name
        step_day(campaign)
        assert campaign.units[0]["x_mm"] == 0
        assert campaign.march_orders[0].get("gate") == "no_surface"
