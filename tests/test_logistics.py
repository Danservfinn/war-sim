"""Supply is a path minimum. A rich source behind a thin link still starves the front."""

from sim.systems.logistics import path_delivery, sustainment, can_build


SAHARA = [
    {"id": "reef-to-cape", "capacity_t": 4000, "self_consume_milli": 20},
    {"id": "cape-to-lagos", "capacity_t": 2000, "self_consume_milli": 80},
    {"id": "lagos-to-tripoli", "capacity_t": 60, "self_consume_milli": 450},
]

RAIL = [
    {"id": "moscow-warsaw", "capacity_t": 8000, "self_consume_milli": 25},
    {"id": "warsaw-vienna", "capacity_t": 8000, "self_consume_milli": 25},
    {"id": "vienna-rome", "capacity_t": 8000, "self_consume_milli": 25},
]


def test_equal_source_sahara_arrives_far_below_european_rail():
    source = 5000
    desert = path_delivery(source, SAHARA)
    rail = path_delivery(source, RAIL)
    assert desert < 50
    assert rail > 4000
    assert rail > desert * 50


def test_binding_constraint_is_the_thinnest_link_not_the_mine():
    blocked = path_delivery(5000, [{"id": "sand", "capacity_t": 0, "self_consume_milli": 0}])
    assert blocked == 0


def test_missing_capability_builds_nothing():
    recipe = {"requires": ["electronics"], "inputs": {"electronics": 1, "explosives": 1}}
    assert can_build(recipe, capabilities=["welding", "explosives"], stocks={"electronics": 10, "explosives": 10}) == 0
    assert can_build(recipe, capabilities=["electronics"], stocks={"electronics": 3, "explosives": 3}) == 3


def test_front_days_follow_arrivals_not_source_output():
    desert = sustainment(source_t=5000, links=SAHARA, front_burn_t=200)
    rail = sustainment(source_t=5000, links=RAIL, front_burn_t=200)
    assert desert["arrived_t"] < desert["produced_t"]
    assert desert["days_of_supply"] == 0
    assert rail["days_of_supply"] >= 20
    assert desert["binding_link"] == "lagos-to-tripoli"
