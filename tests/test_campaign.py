"""Year-scale ledger. Fails until sim.campaign exists."""

from sim.campaign.step import Campaign, step_day, step_until_victory


def _base():
    return Campaign(
        day=0,
        nodes=[{"id": "reef", "good": "chrome", "nameplate_t": 10, "reserve_t": 100, "season_mod": {0: 1000, 6: 500}, "stock_t": 0}],
        plants=[{"id": "plant", "strain_milli": 0, "dud_base": 20, "skilled_labor": 2, "power_mw": 10, "tools": 2,
                 "civilian_share_milli": 0, "lines": [{"id": "shells", "power_mw_need": 10, "tools_need": 1, "skilled_need": 1, "damage_milli": 0, "daily_cap": 5}]}],
        lots=[],
        fleets={"trucks": {"count": 10, "fuel_grade": "diesel"}},
        links=[{"id": "sand", "fleet_id": "trucks", "payload_t": 5, "payload_l": 1000, "empties_milli": 0, "port_slots_t": 0,
                "distance_km": 1000, "speed_km_per_day": 100, "self_consume_milli": 0, "season_mod": {0: 1000}, "cargo_id": "food"}],
        in_transit=[],
        imports=[{"good": "avgas", "embargo_day": 11, "schedule": [{"day": 10, "qty_t": 100}, {"day": 12, "qty_t": 50}], "received_t": 0}],
        factions={"side_b": {"cohesion": 5, "manpower": 10, "trainees": 100, "training_cap_per_day": 3, "food_t": 10, "food_burn_t": 5,
                             "water_t": 10, "water_burn_t": 0, "fuel": {"diesel": 20, "avgas": 0}, "loss_hold_days": 0,
                             "cohesion_loss_per_day": 5}},
        victory_rules=[{"against": "side_b", "kind": "cohesion_at_or_below", "value": 0, "hold_days": 2}],
        history=[],
        victory=None,
        stocks={"food": 0, "avgas": 0},
    )


def test_mine_depletes_and_stops():
    c = _base()
    step_day(c)
    assert c.nodes[0]["reserve_t"] == 90
    c.nodes[0]["reserve_t"] = 0
    step_day(c)
    assert c.nodes[0]["last_output_t"] == 0


def test_season_cuts_output():
    c = _base()
    c.day = 180  # month 6
    step_day(c)
    assert c.nodes[0]["last_output_t"] == 5


def test_lot_ages_past_storage():
    c = _base()
    c.lots.append({"lot_id": "L1", "ammo_id": "he", "plant_id": "plant", "minted_day": 0, "qty": 4, "dud_milli": 20, "storage_days": 30, "age_dud_per_30d": 10})
    c.day = 60
    step_day(c)
    assert c.lots[0]["dud_milli"] == 30


def test_africa_nameplate_and_imported_powder():
    c = _base()
    c.plants[0]["lines"][0]["daily_cap"] = 277
    c.plants[0]["lines"][0]["powder_local"] = True
    step_day(c)
    assert c.plants[0]["military_out"] == 277
    c.plants[0]["lines"][0]["powder_local"] = False
    step_day(c)
    assert c.plants[0]["military_out"] == 0


def test_civilian_share_and_missing_tools():
    c = _base()
    c.plants[0]["civilian_share_milli"] = 400
    step_day(c)
    assert c.plants[0]["military_out"] == 3  # daily_cap 5, 40% civilian
    c.plants[0]["tools"] = 0
    before = len(c.lots)
    step_day(c)
    assert len(c.lots) == before


def test_empties_and_volume_cap():
    c = _base()
    c.links[0]["empties_milli"] = 500
    assert c.link_capacity_t("sand") == 25
    c.links[0]["empties_milli"] = 0
    c.links[0]["payload_l"] = 100
    assert c.link_capacity_t("sand", volume_l_per_t=1000) == 1


def test_strain_mints_worse_lot():
    c = _base()
    c.plants[0]["strain_milli"] = 800
    step_day(c)
    minted = [lot for lot in c.lots if lot["plant_id"] == "plant"]
    assert minted
    assert minted[-1]["dud_milli"] == 20 + 80


def test_fleet_loss_cuts_capacity():
    c = _base()
    assert c.link_capacity_t("sand") == 50
    c.fleets["trucks"]["count"] = 2
    assert c.link_capacity_t("sand") == 10


def test_transit_waits_for_arrive_day():
    c = _base()
    c.stocks["food"] = 20
    c.factions["side_b"]["food_burn_t"] = 0
    step_day(c)
    assert c.in_transit[0]["arrive_day"] == 10
    assert c.factions["side_b"]["food_t"] == 10
    c.day = 10
    step_day(c)
    assert c.factions["side_b"]["food_t"] == 30
    assert c.in_transit == []


def test_embargo_cancels_later_rows():
    c = _base()
    c.factions["side_b"]["food_t"] = 100
    c.factions["side_b"]["food_burn_t"] = 0
    c.victory_rules = []
    for _ in range(13):
        step_day(c)
    assert c.imports[0]["received_t"] == 100


def test_wrong_fuel_grade_does_not_burn():
    c = _base()
    assert c.can_burn("side_b", "avgas", 5) is False
    assert c.can_burn("side_b", "diesel", 5) is True


def test_training_cap():
    c = _base()
    step_day(c)
    assert c.factions["side_b"]["graduated_today"] == 3
    assert c.factions["side_b"]["trainees"] == 97


def test_year_snapshot_then_victory_from_empty_food():
    c = _base()
    c.links = []
    c.factions["side_b"]["food_t"] = 400
    c.factions["side_b"]["food_burn_t"] = 1
    c.factions["side_b"]["cohesion"] = 40
    c.factions["side_b"]["cohesion_loss_per_day"] = 1
    c.victory_rules = [{"against": "side_b", "kind": "cohesion_at_or_below", "value": 0, "hold_days": 30}]
    result = step_until_victory(c, limit_days=800)
    assert result["day"] == 800
    assert result["reason"] == "limit"
    assert any(row["day"] == 360 for row in result["history"])
    year = next(row for row in result["history"] if row["day"] == 360)
    assert year["reserve_t"] == 0
    assert year["food_t"] == 40
    c = _base()
    c.factions["side_b"]["food_t"] = 0
    c.factions["side_b"]["food_burn_t"] = 0
    c.links = []
    result = step_until_victory(c, limit_days=10)
    assert result["reason"] == "limit"
    assert result["day"] == 10
