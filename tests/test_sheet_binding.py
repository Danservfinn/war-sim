"""A unit keeps its sheet. An unbound unit does not walk two tagged sheets."""

from sim.campaign.load import load_campaign
from sim.campaign.step import Campaign, _move_cells, step_day
from pathlib import Path

CELL = 10_000_000


def test_loader_stamps_the_sheet_on_a_copied_row():
    c = load_campaign(Path("scenarios/europe_1939_africa_modern"))
    europe = [row for row in c.generals if row.get("state") == "france"]
    africa = [row for row in c.plants if row.get("id") == "rdm_boksburg"]
    assert europe
    assert africa
    assert all(row.get("year_state") == "europe_1939" for row in europe)
    assert all(row.get("year_state") == "africa_2024" for row in africa)
    assert all(row.get("year_state") for row in c.units)


def test_a_bound_unit_sees_only_its_sheet():
    cells = [
        {"id": "eu", "surface": "land", "x_mm": 0, "y_mm": 0, "year_state": "europe_1939", "source": "fixture"},
        {"id": "af", "surface": "land", "x_mm": CELL, "y_mm": 0, "year_state": "africa_2024", "source": "fixture"},
    ]
    c = Campaign(cells=cells, units=[])
    europe = _move_cells(c, {"id": "eu-unit", "year_state": "europe_1939"})
    africa = _move_cells(c, {"id": "af-unit", "year_state": "africa_2024"})
    assert [row["id"] for row in europe] == ["eu"]
    assert [row["id"] for row in africa] == ["af"]


def test_an_unbound_unit_does_not_walk_two_sheets():
    c = Campaign(
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
            "id": "walker", "side": "a", "alive": True, "foot": True,
            "x_mm": 0, "y_mm": 0, "speed_mm_per_day": 25_000_000,
            "in_bubble": False, "equipment": {},
        }],
        cells=[
            {"id": "eu", "surface": "land", "x_mm": 0, "y_mm": CELL, "year_state": "europe_1939", "source": "fixture"},
            {"id": "af", "surface": "sea", "x_mm": CELL, "y_mm": 0, "year_state": "africa_2024", "source": "fixture"},
        ],
        march_orders=[{
            "id": "march-1",
            "entity_id": "walker",
            "issued_day": 0,
            "active_day": 0,
            "course": [{"x_mm": 0, "y_mm": CELL}],
            "waypoint": 0,
        }],
    )
    step_day(c)
    assert c.units[0]["x_mm"] == 0
    assert c.units[0]["y_mm"] == 0
    assert c.march_orders[0].get("gate") == "no_sheet"
    sentences = [row["sentence"] for row in getattr(c, "events", []) or [] if row["kind"] == "march_refused"]
    assert sentences == ["March walker refused. Gate no_sheet."]
    assert not any(word in sentences[0] for word in ("1939", "modern", "lost heart"))
