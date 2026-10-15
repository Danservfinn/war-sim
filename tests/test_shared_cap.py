"""A mount's rounds_per_day is shared across targets. Mounts do not share with each other."""

from sim.campaign.step import Campaign, _fight


def _body(unit_id: str, integrity: int = 100) -> dict:
    return {
        "id": unit_id,
        "Physical": {
            "integrity": integrity,
            "signature": {"visual": 1000},
            "armor": [{"aspect": "front", "thickness_mm": 0, "ke_mod": 1000}],
        },
    }


def _mount(mount_id: str, cap: int, qty: int, ammo_id: str) -> dict:
    return {
        "mount_id": mount_id,
        "rounds_per_day": cap,
        "ammo": [{
            "ammo_id": ammo_id,
            "qty": qty,
            "warhead": "ke",
            "penetration_mm": 0,
            "blast": 1,
            "guidance": "none",
        }],
        "range_bands": [{"max_m": 1000, "accuracy": 1000}],
    }


def _attacker(mounts: list) -> dict:
    return {
        "id": "jet",
        "WeaponMount": mounts,
        "Crew": {"billets": [{"role": "gunner", "count": 1, "skill": 100}]},
    }


def _campaign(engagements: list) -> Campaign:
    return Campaign(
        day=0, nodes=[], plants=[], lots=[], fleets={}, links=[], in_transit=[], imports=[],
        factions={}, victory_rules=[], history=[], victory=None, stocks={},
        units=[], contacts=[], engagements=engagements,
    )


def _row(attacker: dict, defender: dict) -> dict:
    return {
        "day": 0,
        "attacker": attacker,
        "defender": defender,
        "distance_m": 100,
        "weather": 1000,
        "aspect": "front",
    }


def test_first_target_in_id_order_spends_the_mount_cap():
    mount = _mount("missile", cap=6, qty=6, ammo_id="aam")
    attacker = _attacker([mount])
    low = _body("a")
    high = _body("z")
    # Queued high-id first. The cap still resolves ascending.
    c = _campaign([_row(attacker, high), _row(attacker, low)])
    _fight(c)
    assert mount["ammo"][0]["qty"] == 0
    assert low["Physical"]["integrity"] == 94  # 6 shots, 1 damage each
    assert high["Physical"]["integrity"] == 100


def test_second_target_gets_only_the_remainder():
    mount = _mount("missile", cap=6, qty=4, ammo_id="aam")
    attacker = _attacker([mount])
    low = _body("a")
    high = _body("z")
    c = _campaign([_row(attacker, high), _row(attacker, low)])
    _fight(c)
    assert mount["ammo"][0]["qty"] == 0
    assert low["Physical"]["integrity"] == 96  # ready 4 binds the cap
    assert high["Physical"]["integrity"] == 100


def test_gun_and_missile_mounts_do_not_share_a_cap():
    gun = _mount("gun", cap=1, qty=5, ammo_id="ball")
    missile = _mount("missile", cap=2, qty=5, ammo_id="aam")
    attacker = _attacker([gun, missile])
    target = _body("a", integrity=100)
    c = _campaign([_row(attacker, target)])
    _fight(c)
    assert gun["ammo"][0]["qty"] == 4
    assert missile["ammo"][0]["qty"] == 3
    assert target["Physical"]["integrity"] == 97  # 1 + 2
