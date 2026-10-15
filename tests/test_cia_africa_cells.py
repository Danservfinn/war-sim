"""CIA Africa political sheet. A position is stored only after the mark sat on the letters."""

from pathlib import Path

import yaml

from sim.campaign.step import step_day
from tests.test_cell_map import CELL, _campaign

PATH = Path("catalogs/cells/cia_africa_pol.yaml")

SEAS = {
    'NORTH ATLANTIC OCEAN': (-5692917847, -10078186969),
    'SOUTH ATLANTIC OCEAN': (-5448158640, -2603966006),
    'INDIAN OCEAN': (1724645892, -4573371105),
    'Mediterranean Sea': (-1677053824, -8380736544),
    'Black Sea': (-589235127, -9411898017),
    'Caspian Sea': (643626062, -9511614731),
    'Red Sea': (-38526912, -6973371105),
    'Arabian Sea': (1985269122, -6506515581),
    'Persian Gulf': (1402832861, -7707648725),
    'Gulf of Aden': (1167138810, -6103116147),
    'Gulf of Guinea': (-3499150142, -4994900850),
    'Mozambique Channel': (133711048, -2388668555),
    'Strait of Gibraltar': (-4707082153, -8700283286),
}

LAND = {
    'MOROCCO': (-4763739377, -8074787535),
    'ALGERIA': (-3721246459, -7805099150),
    'TUNISIA': (-2980169972, -8383002833),
    'LIBYA': (-2193767705, -7635127479),
    'EGYPT': (-994900850, -7544475921),
    'MAURITANIA': (-5291784703, -6943909348),
    'MALI': (-4199433428, -6749008499),
    'NIGER': (-3016430595, -6662889518),
    'CHAD': (-1996600567, -6370538244),
    'SUDAN': (-1033427762, -6248158640),
    'SOUTH SUDAN': (-861189802, -5325779037),
    'ERITREA': (77053824, -6506515581),
    'DJIBOUTI': (847592068, -6062322946),
    'ETHIOPIA': (317280453, -5579603399),
    'SOMALIA': (1511614731, -5289518414),
    'KENYA': (-47592068, -4831728045),
    'UGANDA': (-312747875, -4913314448),
    'RWANDA': (-892917847, -4457790368),
    'BURUNDI': (-586968839, -4303682720),
    'TANZANIA': (-224362606, -3854957507),
    'GABON': (-2912181303, -4514447592),
    'CAMEROON': (-2814730878, -5325779037),
    'CENTRAL AFRICAN REPUBLIC': (-1597733711, -5330311615),
    'NIGERIA': (-3120679887, -5824362606),
    'BENIN': (-3916147309, -5844759207),
    'TOGO': (-3950141643, -5677053824),
    'GHANA': (-4088385269, -5547875354),
    'CÔTE D’IVOIRE': (-4684419263, -5692917847),
    'BURKINA FASO': (-4541643059, -5971671388),
    'LIBERIA': (-5287252125, -5305382436),
    'SIERRA LEONE': (-5511614731, -5584135977),
    'GUINEA': (-5439093484, -5953541076),
    'THE GAMBIA': (-5921813031, -6207365439),
    'SENEGAL': (-5640793201, -6372804533),
    'ANGOLA': (-2223229462, -3315580737),
    'NAMIBIA': (-2252691218, -2411331445),
    'BOTSWANA': (-1434560907, -2234560907),
    'ZAMBIA': (-1078753541, -3095750708),
    'ZIMBABWE': (-897450425, -2572237960),
    'MOZAMBIQUE': (-181303116, -2676487252),
    'MALAWI': (-373937677, -3308781870),
    'SOUTH AFRICA': (-1627195467, -1228328612),
    'ESWATINI': (-580169972, -1611331445),
    'MADAGASCAR': (931444759, -2227762040),
    'Sardinia': (-2971104816, -8999433428),
    'Sicily': (-2511048159, -8761473088),
    'CYPRUS': (-917847025, -8548441926),
    'IRELAND': (-4292351275, -10488385269),
    'PORTUGAL': (-4775070822, -9051558074),
    'SPAIN': (-4092917847, -9083286119),
    'FRANCE': (-3490084986, -9776770538),
    'GERMANY': (-2773937677, -10205099150),
    'POLAND': (-2155240793, -10282152975),
    'BELARUS': (-1488951841, -10409065156),
    'UKRAINE': (-1119546742, -10035127479),
    'RUSSIA': (-358073654, -10395467422),
    'KAZAKHSTAN': (1203399433, -10227762040),
    'CZECHIA': (-2449858357, -10028328612),
    'ROMANIA': (-1389235127, -9609065156),
    'ITALY': (-2551841360, -9158073654),
    'GREECE': (-1679320113, -8931444759),
    'TURKEY': (-688951841, -8976770538),
    'TURKMENISTAN': (1371104816, -9241926346),
    'UZBEKISTAN': (1556940510, -9579603399),
    'SYRIA': (-328611898, -8586968839),
    'IRAQ': (244759207, -8407932011),
    'IRAN': (1149008499, -8441926346),
    'SAUDI ARABIA': (713881020, -7222662890),
    'OMAN': (1819830028, -7018696884),
    'YEMEN': (1117280453, -6513314448),
    'JORDAN': (-360339943, -8124645892),
}

ABSENT = {
    'CABO VERDE',
    'SAO TOME AND PRINCIPE',
    'EQUATORIAL GUINEA',
    'COMOROS',
    'SEYCHELLES',
    'MAURITIUS',
    'BAHRAIN',
    'MALTA',
    'AZORES',
    'MADEIRA ISLANDS',
    'CANARY ISLANDS',
    'Corsica',
    'Socotra',
    'TRISTAN DA CUNHA',
    'AGALEGA ISLANDS',
    'Ascension',
    'Gough Island',
    'Annobon',
    'Mayotte',
    'Reunion',
    'Saint Helena',
    'Glorioso Islands',
    'ISRAEL',
    'LEBANON',
    'QATAR',
    'GUINEA-BISSAU',
    'LESOTHO',
    'Cabinda',
    'Lake Victoria',
    'Lake Tanganyika',
    'Lake Nyasa',
    'Nile',
    'Orange',
    'U.K.',
    'NETH.',
    'BEL.',
    'LUX.',
    'LIECH.',
    'SWITZ.',
    'AND.',
    'AUS.',
    'HUNG.',
    'MOL.',
    'SLO.',
    'SLOV.',
    'CRO.',
    'BOS. & HER.',
    'SER.',
    'MONT.',
    'KOS.',
    'BULG.',
    'ALB.',
    'N. MACE.',
    'GEO.',
    'ARM.',
    'AZER.',
    'AFG.',
    'PAK.',
    'KUW.',
    'U.A.E.',
    'LITH.',
    'RUS.',
    'EQUA. GUI.',
    'DEM. REP. OF THE CONGO',
    'REP. OF THE CONGO',
    'coast',
}


def test_sheet_reading_and_measured_points():
    data = yaml.safe_load(PATH.read_text())
    assert data["title"] == "AFRICA"
    assert data["scale"] == "1:51,400,000"
    assert "3448.5" in data["origin"]
    assert "5513.5" in data["origin"]
    cells = {row["name"]: row for row in data["cells"]}
    assert set(cells) == set(SEAS) | set(LAND)
    for name, (x_mm, y_mm) in SEAS.items():
        assert cells[name]["surface"] == "sea"
        assert cells[name]["x_mm"] == x_mm
        assert cells[name]["y_mm"] == y_mm
    for name, (x_mm, y_mm) in LAND.items():
        assert cells[name]["surface"] == "land"
        assert cells[name]["x_mm"] == x_mm
        assert cells[name]["y_mm"] == y_mm
    absent = {item["name"] for item in data["absent"]}
    assert absent == ABSENT
    assert not absent & set(cells)


def test_a_ground_step_through_every_positioned_sea_is_rejected():
    data = yaml.safe_load(PATH.read_text())
    seas = [row for row in data["cells"] if row["surface"] == "sea"]
    assert len(seas) == len(SEAS)
    for sea in seas:
        campaign = _campaign()
        campaign.cells = [sea]
        campaign.units[0]["x_mm"] = sea["x_mm"] - CELL
        campaign.units[0]["y_mm"] = sea["y_mm"]
        campaign.march_orders[0]["course"] = [{
            "x_mm": sea["x_mm"] + CELL,
            "y_mm": sea["y_mm"],
            "cell_id": sea["id"],
        }]
        step_day(campaign)
        assert campaign.units[0]["x_mm"] == sea["x_mm"] - CELL
        assert campaign.march_orders[0].get("gate") == "no_surface"
