"""Bartholomew 1939 sheet. Positions come from the printed kilometre bar."""

from pathlib import Path

import yaml

from sim.campaign.step import step_day
from tests.test_cell_map import _campaign

PATH = Path("catalogs/cells/bartholomew_1939.yaml")

# Measured on docs/sources/evidence/uwm-agsmap023709-bartholomew-1939.jpg.
# Origin is the 0 tick of the Kilometres bar. 320 km is 518.5 px on this scan.
CELLS = [
    ("ALGERIA", "land", 1004744455, -2864570878),
    ("BLACK SEA", "sea", 3301832208, -1745650916),
    ("BOHEMIA", "land", 1820636451, -1230935391),
    ("BULGARIA", "land", 2663066538, -1983876567),
    ("DENMARK", "land", 1542912247, -465650916),
    ("EGYPT", "land", 3240115718, -3353982642),
    ("EIRE", "land", 357955641, -570568949),
    ("ESTONIA", "land", 2579749277, -120038573),
    ("FINLAND", "land", 2468659595, 274946962),
    ("FRANCE", "land", 888717454, -1477801350),
    ("GERMANY", "land", 1697203472, -1070472517),
    ("GREECE", "land", 2443972999, -2508466731),
    ("GULF OF RIGA", "sea", 2468659595, -231128255),
    ("Gulf of Sidra", "sea", 2116875603, -3339170685),
    ("HUNGARY", "land", 2138476374, -1477801350),
    ("IONIAN SEA", "sea", 2178592093, -2570183221),
    ("KATTEGAT", "sea", 1666345227, -357647059),
    ("LATVIA", "land", 2567405979, -323702989),
    ("LIBYA", "land", 1703375121, -3332381871),
    ("LITHUANIA", "land", 2394599807, -477994214),
    ("MORAVIA", "land", 1950241080, -1230935391),
    ("MOROCCO", "land", 63567985, -3033056895),
    ("NORTH SEA", "sea", 1089296046, -440964320),
    ("NORWAY", "land", 1542912247, 117569913),
    ("POLAND", "land", 2354484089, -916181292),
    ("ROMANIA", "land", 2678495661, -1616663452),
    ("SLOVAKIA", "land", 2258823529, -1280308582),
    ("SPAIN", "land", 385728062, -2162854388),
    ("SPANISH MOROCCO", "land", 178977821, -2743606557),
    ("SWEDEN", "land", 1891610415, 24995178),
    ("SYRIA", "land", 4017743491, -2653500482),
    ("Tripolitania", "land", 1652767599, -3270665381),
]

ABSENT = [
    "GREAT BRITAIN & NORTHERN IRELAND",
    "HATAY",
    "TURKEY",
    "BALTIC",
    "ENGLISH CHANNEL",
    "BAY OF BISCAY",
    "MEDITERRANEAN SEA",
    "TUNISIA",
    "PORTUGAL",
    "ITALY",
    "coast",
]


def test_bartholomew_sheet_stores_measured_named_cells():
    data = yaml.safe_load(PATH.read_text())
    assert data["title"] == "EUROPE AND THE MEDITERRANEAN"
    assert data["scale"] == "1:5,300,000"
    assert data["date"] == "1939"
    assert data["origin"]["tick"] == "0 Kilometres"
    assert data["origin"]["x_positive"] == "east"
    assert data["origin"]["y_positive"] == "north"
    rows = data["cells"]
    assert [(row["name"], row["surface"], row["x_mm"], row["y_mm"]) for row in rows] == CELLS
    assert all(isinstance(row["x_mm"], int) and isinstance(row["y_mm"], int) for row in rows)
    absent = {row["name"] for row in data["absent"]}
    assert set(ABSENT) <= absent
    assert not absent & {row["name"] for row in rows}


def test_a_ground_step_into_a_bartholomew_sea_cell_is_rejected():
    data = yaml.safe_load(PATH.read_text())
    seas = [row for row in data["cells"] if row["surface"] == "sea"]
    assert [row["name"] for row in seas] == [
        "BLACK SEA",
        "GULF OF RIGA",
        "Gulf of Sidra",
        "IONIAN SEA",
        "KATTEGAT",
        "NORTH SEA",
    ]
    for row in seas:
        campaign = _campaign()
        campaign.units[0]["in_bubble"] = True
        campaign.units[0]["speed_mm_per_day"] = 3_000_000
        campaign.units[0]["x_mm"] = row["x_mm"] - 1_000_000
        campaign.units[0]["y_mm"] = row["y_mm"]
        campaign.cells.append({
            "id": row["name"],
            "name": row["name"],
            "surface": "sea",
            "x_mm": row["x_mm"],
            "y_mm": row["y_mm"],
        })
        campaign.march_orders[0]["course"] = [{
            "x_mm": row["x_mm"] + 1_000_000,
            "y_mm": row["y_mm"],
        }]
        step_day(campaign)
        assert campaign.units[0]["x_mm"] == row["x_mm"] - 1_000_000
        assert campaign.march_orders[0].get("gate") == "no_surface"
