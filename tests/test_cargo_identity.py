"""A link keeps its cargo id. Steel does not ride a food link."""

from sim.campaign.step import step_day
from tests.test_defect_gates import _bare, _plant


def test_a_food_link_does_not_deliver_steel():
    c = _bare(
        plants=[_plant(node_id="yard")],
        nodes=[
            {"id": "pit", "continent": "africa", "good": "steel", "stock_t": 5, "nameplate_t": 0, "reserve_t": 0},
            {"id": "yard", "continent": "africa", "good": "none", "stock_t": 0, "nameplate_t": 0, "reserve_t": 0},
        ],
        links=[{
            "id": "road", "kind": "road", "from_node": "pit", "to_node": "yard",
            "open": True, "capacity_t": 8, "cargo_id": "food",
            "fleet_id": "trucks", "payload_t": 1, "payload_l": 1, "distance_km": 0,
        }],
        fleets={"trucks": {"count": 1}},
    )
    step_day(c)
    assert c.nodes[0]["stock_t"] == 5
    assert c.plants[0]["military_out"] == 0
