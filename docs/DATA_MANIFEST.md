# Data manifest

Inventory only. Written 2026-10-14 from the files on disk. This file is not a year-state. `load_campaign` does not read it. The tick does not read `civil_year`. A line here is a pointer. The catalog is the transcription. The opened document is the source. No number in this file is a source.

Section 18 of `docs/ARCHITECTURE.md` is the slot list. Section 6 is the scenario tree the loader was specified to read. Section 16 is the leader card. This manifest files what we have into those slots. It does not fill an empty slot.

When a locator note and a catalog disagree, the catalog row wins for what was copied. Two stale sentences are named below. They were corrected in the same pass as this file.

## Slot status

`fills` means a cited row exists and can be copied into that schema later. It does not mean the tick reads it.

`refused` means a document was opened and no row was taken. The reason is the close, not a guess.

`fixture` means the engine or a test can read it. It is not a 1939 or 2024 count.

`absent` means the class is empty on purpose.

| Architecture slot | Europe 1939 | Africa 2024 | Where it lives now |
| --- | --- | --- | --- |
| `id`, `civil_year`, `as_of` | fills | fills | `catalogs/year_states/` |
| `region` | fills (`europe`) | absent. `label: modern` is not `region` | Europe file only |
| `source` | absent as a top-level key. Each row has its own `source`. `as_of_source` is the date locator | same | row strings |
| `states` | absent as a list. 23 states are implied by `leaders[].state`. Two more are named absent | absent as a list. 6 states implied | leader rows |
| `leaders` | fills. 35 chairs. Civil dates, not campaign days | fills. 6 chairs. No end date on the page | year-state files |
| `generals` | fills. 2 offices, one name. Starts stated. Ends not stated. A month is not a day. A second page does not finish a tenure | absent. Named in `omitted`. A 2021 appointment does not state the chair on 31 December 2024 | year-state files |
| `units` | fills. 1 strength count, not spawned. 12 listed ships, not placed. A garbled name is absent | fills. 3 listed ships, not placed. A hull still building is absent | `catalogs/year_states/` |
| `plants` | absent. `plants: []` | fills. 2 rows. Boksburg 277 shells/day. Somerset West 1,111 charges/day. Both from Helmsen, 7 July 2023 | `catalogs/year_states/africa_2024.yaml` |
| `stocks` | fills. 15 end-of-1939 stock cells. Production is not a stock. A dot is not a zero | absent | `catalogs/year_states/europe_1939.yaml` |
| `points` | absent. Key missing | absent. Key missing | rifle-contact fixture only |
| `links` | absent. Key missing | absent. Key missing | `catalogs/straits.yaml` is a paraphrase, not a source |
| `cells` | named labels only, no position, no coast. `catalogs/cells/ngs_1939_08_28.yaml` | absent. Empty list. Named | the NGS file, not a grid |
| orders | absent | absent | not a `YearState` field. Section 16 card |
| weapons | absent | absent | not a `YearState` field. Ammo catalog |
| series | 34 national-output rows. Not a plant. Not a stock. Not named on a scenario. An estimate mark is a refusal | 4 rows: Egypt, South Africa, Algeria national steel plus the six-country group total | year-state files |

`goods_cross` is false on both year-state files. Section 18 says a year-state does not open the wall. The flag on the file does not open it.

## What the tick reads

`load_campaign` reads `scenario.yaml`, `factions.yaml`, `points.yaml`, `units.yaml`, `industry.yaml`, and the catalog path on `scenario.yaml`. That path is `catalogs/africa_capacity.yaml` for the rifle contact.

The rifle contact does not read `catalogs/year_states/`. `scenarios/europe_1939` and `scenarios/europe_1939_africa_modern` do, because their `scenario.yaml` lists the path. The tick still does not read `civil_year`.

`scenarios/europe_1939/` lists the Europe catalog. `scenarios/europe_1939_africa_modern/` lists both catalogs. `load_campaign` copies leaders and series. It does not copy `civil_year`. National output is not a plant. `scenarios/europe_africa/` is not pointed at either file.

## Europe 1939

File: `catalogs/year_states/europe_1939.yaml`

sha256 prefix `6830dc3452b7e51f`. 43,567 bytes. Recomputed after the opened-map notes. The earlier prefix `7ab9adcf77e6bebb` was the file before those notes.

`id: europe_1939`. `region: europe`. `civil_year: 1939`. `as_of: 1939-09-01`. `collection_status: open`. `goods_cross: false`.

Date locator: USGS, Rabbitt vol. 4, chapter 2. Ledger [1]. Footnote 2 of that page was not opened. Capture: `docs/sources/evidence/usgs-1939.txt`.

Locator note: `docs/sources/europe-1939.md`.

### Leaders

35 rows. Each has name, office, state, `from_date`, `to_date`, and a source string. The printed table below does not list `it_mussolini` or `su_molotov`. The catalog does. Section 16 seats a leader on `from_day` and `to_day`. Those are campaign days. These dates are civil dates. A loader must not treat them as the same field. This file does not convert them.

| id | state | office |
| --- | --- | --- |
| de_hitler | germany | Führer und Reichskanzler |
| uk_george_vi | united_kingdom | King |
| uk_chamberlain | united_kingdom | Prime Minister and First Lord of the Treasury |
| fr_lebrun | france | Président de la République française |
| fr_daladier | france | Président du Conseil des ministres |
| it_vittorio_emanuele_iii | italy | Re d'Italia |
| pl_moscicki | poland | President of the Republic |
| pl_skladkowski | poland | President of the Council of Ministers |
| es_franco_state | spain | Jefe del Estado |
| es_franco_govt | spain | Presidente del Gobierno |
| su_kalinin | ussr | Chairman of the Presidium of the Supreme Soviet |
| be_leopold_iii | belgium | Roi des Belges |
| nl_wilhelmina | netherlands | Queen of the Netherlands |
| dk_christian_10 | denmark | King of Denmark and Iceland |
| se_gustaf_v | sweden | Med Guds Nåde, Sveriges, Götes och Vendes Konung |
| no_haakon_vii | norway | King of Norway |
| fi_kallio | finland | President of the Republic |
| gr_georgios_ii | greece | King of the Hellenes |
| ro_carol_ii | romania | King of Romania |
| bg_boris_iii | bulgaria | King (Tsar) of the Bulgarians |
| hu_horthy | hungary | Governor of Hungary |
| hu_teleki | hungary | Hungarian Royal Prime Minister |
| yu_petar_ii | yugoslavia | King of Yugoslavia |
| yu_pavle | yugoslavia | Royal Regent |
| yu_stankovic | yugoslavia | Royal Regent |
| yu_perovic | yugoslavia | Royal Regent |
| al_viktor_emanueli | albania | King of Italy and Albania, Emperor of Ethiopia |
| pt_carmona | portugal | Presidente da República |
| pt_salazar | portugal | Presidente do Conselho de Ministros |
| ie_hyde | ireland | President of Ireland |
| ie_de_valera | ireland | Taoiseach |
| ch_etter | switzerland | President of the Confederation |
| tr_inonu | turkey | President |

Seven of those are heads of government: Chamberlain, Daladier, Sławoj-Składkowski, Franco's government chair, Teleki, Salazar, de Valera. The old omitted label said only Hungary, Portugal, and Ireland. That label was false. A later pass added Molotov from the Soviet government page and kept the Camera dei deputati row for Mussolini. The omitted label is now `heads_of_government_not_on_an_opened_page`. The catalog is the list. This table is not.

Italy head of government is the Camera dei deputati row, `it_mussolini`. The Archontology Italy index still has no government page. That absence does not drop the Camera row.

Absent on the date, with a source, not filled from a neighbor:

- Czechoslovakia. Last listed term ends 15 March 1939. `arch-cs_state.txt`.
- Austria. Last listed term ends 13 March 1938. `arch-at_state.txt`.

Kalinin's page does not assign a continent. The row says so.

### Not a Unit

`uk_armed_forces_1939_09` is a strength count. End of September 1939, not 1 September. Thousands. Total 1,270, Royal Navy 180, Army 897, Royal Air Force 193. Not a formation. Not an order of battle. It does not fill `YearState.units`.

Source: Central Statistical Office, Statistical Digest of the War, HMSO, London, 1951, Table 10. Wellcome Collection. File: `docs/sources/evidence/statistical-digest-of-the-war-1951.pdf`, 67,415,029 bytes. No text layer. The note's later sentence that the Archive copy is borrow-restricted and was not opened is about the Archive, not this file. The Wellcome copy is the one on disk.

### Series

The catalog is the list. 34 rows. An earlier sentence said twelve, then thirty-one. Those counts are stale. The table below is a pointer, not a second copy of the tonnes. Full calendar year 1939, so the rows include days after 1 September. Not the pile on that date. Not a plant. Remainder after dividing by 360 is not a stock. They are not named on a scenario, so they are not yet the calibration series in section 18 step 3. The 2026-10-15 series pass added Netherlands slab zinc, Switzerland virgin aluminium, and Portugal tungsten concentrates from the Bureau of Mines yearbook. No estimate mark on those cells. The United Kingdom zinc cell carries a footnote mark whose text the OCR dropped. Refused.

| id | good | document |
| --- | --- | --- |
| be_pig_iron_1939 | pig iron, including ferro-alloys | Minerals Yearbook 1940, printed page 562 |
| nl_pig_iron_1939 | pig iron, including ferro-alloys | same table |
| ro_pig_iron_1939 | pig iron, including ferro-alloys | same table |
| pt_iron_ore_1939 | iron ore | printed page 555. 1938 cell on the same line is 2,519. The 1939 cell is 418. Not repaired |
| ro_iron_ore_1939 | iron ore | same table |
| yu_iron_ore_1939 | iron ore | same table |
| yu_bauxite_1939 | bauxite | printed page 653 |
| gb_coal_1939 | coal | Digest, Table 73, printed page 75. Great Britain, not the United Kingdom. The page does not say long or metric. Not converted |
| uk_home_iron_ore_1939 | home iron ore | Digest, Table 90, printed page 101. United Kingdom. Not a Germany row |
| uk_pig_iron_1939 | pig iron, including ferro-alloys | Digest, Table 91, printed page 103. United Kingdom. Not a Germany row |
| uk_steel_ingots_castings_1939 | steel ingots and castings | Digest, Table 92, printed page 105. United Kingdom. Not a Germany row |
| uk_aircraft_completed_1939 | aircraft completions | Digest, Table 130, printed page 152. Completions, not a strength, not an order of battle |
| gb_coke_1939 | coke | Digest, Table 77. Great Britain |
| gb_gas_made_1939 | gas made | Digest, Table 79. Great Britain |
| gb_electricity_generated_1939 | electricity generated | Digest, Table 81. Great Britain |
| uk_finished_steel_products_1939 | finished steel products | Digest, Table 93 |
| uk_virgin_aluminium_1939 | virgin aluminium | Digest, Table 96 |
| uk_sulphuric_acid_1939 | sulphuric acid | Digest, Table 101 |
| uk_spent_oxide_1939 | spent oxide | Digest, Table 101 |
| uk_industrial_alcohol_1939 | industrial alcohol | Digest, Table 101 |
| uk_methylated_spirit_1939 | industrial methylated spirit | Digest, Table 101 |
| uk_small_arms_completed_1939 | small arms | Digest, Table 122. Completions, not a stock |
| uk_armoured_vehicles_completed_1939 | armoured fighting vehicles | Digest, Table 126. Completions, not a unit |
| uk_other_weapons_completed_1939 | other weapons | Digest, Table 121. Completions, not a trial |
| uk_aircraft_engines_completed_1939 | aircraft engines | Digest, Table 134. Completions, not a second count of horsepower |
| uk_agricultural_machinery_1939 | agricultural machinery | Digest, Table 138. Milking machines are dots. Not repaired |
| uk_pitwood_1939 | pitwood | Digest, Table 98 |
| uk_plywood_1939 | plywood | Digest, Table 98. No page total. Not summed |
| uk_rayon_1939 | rayon | Digest, Table 107. Two rows. Not summed |
| uk_cotton_woven_fabrics_1939 | cotton woven fabrics | Digest, Table 107 |
| uk_raw_wool_1939 | raw wool | Digest, Table 108. Actual weight. The estimated row was not copied |

Minerals Yearbook file: `docs/sources/evidence/minerals-yearbook-1940.pdf` and `.txt`. Ledger [37].

Germany, France, and Italy pig iron and steel stay empty. The yearbook cells were estimated, preliminary, or not on a country line. The Digest does not cover those three. Great Britain coal is the coal row. It is not a United Kingdom coal row. United Kingdom home iron ore, pig iron, and steel are the Digest rows above. They are not plants.

### Empty on purpose

`plants`, `stocks`, `orders`, and `weapons` are empty lists. `generals`, `points`, and `links` are missing keys. Formations are omitted. `cells` in the year-state stays an empty list. 35 named labels from the opened National Geographic Europe sheet are in `catalogs/cells/ngs_1939_08_28.yaml`. They have no millimeter position. The Africa 1943 sheet is in `catalogs/cells/ngs_africa_1943.yaml`. The scan is `docs/sources/evidence/yale-15533705.jpg`, 8,924 by 9,573. Origin is the kilometer-bar zero tick. Ten cells are measured. Three are sea: Atlantic Ocean, Black Sea, and Gulf of Guinea. A ground step through each sea point is rejected. Names whose marks missed the letters stay absent. The July 1942 Theater of War sheet is in `catalogs/cells/ngs_theater_1942.yaml`. The scan is `docs/sources/evidence/yale-15258797.jpg`, 8,096 by 9,420. Origin is the kilometer-bar zero tick. Four cells are measured. Two are sea. A ground step through each sea point is rejected. Names whose marks missed the letters stay absent. The CIA political sheet is in `catalogs/cells/cia_africa_pol.yaml`. It is not the 1943 sheet. Its origin is its own kilometer-bar zero tick. Eighty-four cells are measured. Thirteen are sea. A ground step through each sea point is rejected. The uploaded Europe and the Mediterranean sheet is in `catalogs/cells/europe_mediterranean.yaml`. The printed scale is 1:5,300,000. Three names were read. None has a position. The bar endpoints are not readable. Coast is absent. A scale is not a coast. NLS Map Area C16(360) asked for a human check. It was not clicked.

## Africa 2024

File: `catalogs/year_states/africa_2024.yaml`

sha256 prefix `b941cde9b6e10a37`. 25,199 bytes. Recomputed after the loader comment. The earlier prefix `ddcd0fe06af836b4` was the file before that comment.

`id: africa_2024`. `label: modern`. `civil_year: 2024`. `as_of: 2024-12-31`. `collection_status: closed`. `goods_cross: false`. No `region` key. Do not invent `africa` as that field. The word modern is a label. The tick must not read it.

Date locator: worldsteel Table 3, calendar year 2024. Press release 24 January 2025. Ledger [13]. Capture: `docs/sources/evidence/worldsteel-2024.txt`.

Locator note: `docs/sources/africa-2024.md`. The sentence that says leaders are absent is the first pass. The six-chair close is the next sentence in that note. A later pass copied the chairs whose opened pages state name, office, and a tenure covering 31 December 2024. The catalog is the transcription. Capture: `docs/sources/evidence/arch-africa-2024-chairs.txt`.

### Leaders

Six heads of state. None of the pages states an end.

| id | state | from_date | capture |
| --- | --- | --- | --- |
| za_ramaphosa | south_africa | 2018-02-15 | `arch-za_1994.txt` |
| eg_sisi | egypt | 2014-06-08 | `arch-eg_1961.txt` |
| dz_tabun | algeria | 2019-12-19 | `arch-dz_1962.txt` |
| ma_muhammad_vi | morocco | 1999-07-23 | `arch-ma_1957.txt` |
| ng_tinubu | nigeria | 2023-05-29 | `arch-ng_1963.txt` |
| ke_ruto | kenya | 2022-09-13 | `arch-ke_1964.txt` |

`arch-za_state.txt` is the 1910-1961 page. It does not seat Ramaphosa. No row was taken from it.

CIA World Leaders, Egypt, updated 6/2/2026, names a president and a prime minister and does not state a tenure start. Ledger [14]. Capture: `cia-egypt.txt`. Not a leader row. The Egypt chair that was copied is the Archontology row, not this page.

The six rows above are the first close. The file now has 53 leader rows. Libya and South Sudan stay empty. The omitted labels name why. Every other opened page that stated one covering chair was copied. This table is not a second transcription.

### Output, not plants

Three national crude-steel rows. worldsteel Table 3, 2024 column, not marked estimated. Published figure times 1,000,000. Not a counted tonne. Not a plant. Remainder is not a stock.

| id | state | published |
| --- | --- | --- |
| eg_crude_steel_2024 | egypt | 10.7 million tonnes |
| za_crude_steel_2024 | south_africa | 4.7 |
| dz_crude_steel_2024 | algeria | 4.5 |

`africa_six_crude_steel_2024` is Table 1, Africa row, 22.3 million tonnes. Algeria, Egypt, Libya, Morocco, South Africa, Tunisia. Not the continent. Not a plant cap. Libya, Morocco, and Tunisia are inside the total and have no own row. Their share was not computed.

### Plants

Two rows are in `catalogs/year_states/africa_2024.yaml`. Both are from the opened defenceWeb page, 7 July 2023. Jan-Patrick Helmsen, RDM CEO. Boksburg, 100 000 shells a year, 277 a sim-day, remainder 280. Somerset West, 400 000 charges a year, 1,111 a sim-day, remainder 40. The remainders are not stocks. The 150 000 and 600 000 figures are an intention and an aim. Not copied. The page does not state powder origin. `powder_local` is omitted. The loader does not turn that omission into true.

Not copied into the year-state:

- Factory 300. Al Mal, 20 April 2022, was opened. Tarek Ezzat states about 1,400,000 metal parts a year and about 500,000 pieces a year. Those are approximations. Not an exact cap. The page does not state 50,000,000 small-calibre rounds. Rosa El-Youssef returned 403. That rate stays out.
- DICON Kaduna. The cited statement is 29 November 2025. That is after `as_of` 2024-12-31. Not copied.
- PMP Pretoria. No page dated on or before 31 December 2024 was opened that states a round rate, or states that none was published.
- Europe 1939. The documents on disk are national series, completions, or group totals. No plant rate with a speaker, a place, and a date. `plants: []`.

`catalogs/africa_capacity.yaml` still has the older five nameplates. Its `shell_155` label and `powder_local: true` on the RDM rows are not what the opened page states. That file was not rewritten. The rifle scenario still points at it.

The tick reads a year-state only when a scenario names it. `scenarios/europe_africa` is the rifle contact. It was not pointed at this year-state.

The older catalog table is not the year-state. It was not rewritten.

| id | place | good | daily_cap | powder_local | source id |
| --- | --- | --- | --- | --- | --- |
| rdm_boksburg | Boksburg | shell_155 | 277 | true | 3 |
| rdm_somerset | Somerset West | propellant_charge | 1111 | true | 3 |
| dicon_kaduna | Kaduna | round_762 | 83333 | false | 8 |
| factory_300 | Abu Zaabal | round_small | 138888 | true | 14 |
| pmp_pretoria | Pretoria West | round_556 | 0 | true | 6 |

`daily_cap` 0 on PMP means no current round rate was published. It is not a missing file. `powder_local: false` mints nothing while imports are closed. A plan, a target, a need, a 1964 design capacity, and an export contract are not in this table. Airframes, tanks, and guided-weapon electronics are absent.

Locator: `docs/africa-capacity.md`. Ledger: `docs/africa-capacity-ledger.json`, 16 sources, titles empty, URLs present. sha256 prefix `453b405dae21cba7`.

## Opened and refused

No row. Do not copy these on a later pass unless a new page puts the country on the same line as a measured number, with a date on or before `as_of`.

| File | Document | Why no row |
| --- | --- | --- |
| `armaments-yearbook.txt` | League of Nations, Armaments Year-Book, C.228.M.155.1939.IX, Geneva, June 1940. Ledger [43] | Germany's 900,000 is unofficial, end of 1938. France's 31,060 is a legal ceiling, not a count of men on 1 September |
| `statistisches-jahrbuch-1939.txt` | Statistisches Jahrbuch 1939/40. Ledger [44] | Iron table is 1932-1938. The 1938 row does not keep a commodity on its tons |
| `british-war-economy.txt` | Hancock and Gowing, British War Economy. Ledger [45] | Surviving strength table is June 1944. Tons are not on the category line |
| `ussbs-german-economy-ocr.txt` | USSBS, Effects of Strategic Bombing on the German War Economy, 31 October 1945. HathiTrust `mdp.39015017684799` | No 1939 plant cap. District tables are 1943-44 and the columns do not stay with the district. Note calls this [46]. Not in `ledger.json` |
| `statistical-digest-of-the-war-1951.pdf` | Digest, 1951 | Used for the copied production tables. Stock cells are end of period. End-1939 stock was not copied. Table 111 did not agree on a second read. Table 128 is a four-year lump. Table 77 coke footnotes were read. The production row was copied. It says Great Britain. Note calls this [47]. |
| `cia-egypt.txt` | CIA World Leaders, Egypt | No tenure start |
| `arch-it-index.txt` | Archontology Italy index | No heads-of-government page |
| `arch-za_state.txt` | South Africa heads of state, 1910-1961 | Wrong span for 31 December 2024 |
| `arch-al_prev.txt` | Albania heads of state, 1925-1939 | Prior span. The 1939 chair is `arch-al_state.txt` |
| `arch-cs_state.txt` | Czechoslovakia, 1918-1939 | No head of state on 1 September 1939 |
| `arch-at_state.txt` | Austria, 1918-1938 | No head of state on 1 September 1939 |

`british-war-economy-1939-1943.txt` is Mary E. Murphy, The British War Economy, New York, 1943. It is on disk. It is not Hancock and Gowing. It is not cited in either year-state note. No row was taken from it in this inventory. Do not treat it as ledger [45].

Also refused, with no separate evidence file named above: League Statistical Year-Book 1939-40 Table 72, because the transcription does not keep a country on its number. Statista tables, because a commercial database is not a source. A Bureau of Mines coal table whose scan does not keep the year on the number. Minerals Yearbook steel, aluminum, estimated pig iron, iron ore with no 1939 cell, and coal and lignite marked preliminary.

## Evidence that did produce a chair

These captures are the pages behind the leader rows. The source string on the row is the locator. The capture is not a second source.

Europe: `arch-hitler.txt`, `arch-george6.txt`, `arch-chamberlain.txt`, `arch-france-state.txt`, `arch-france-govt.txt`, `arch-italy-kings.txt`, `arch-poland-state.txt`, `arch-poland-govt.txt`, `arch-spain-state.txt`, `arch-spain-govt.txt`, `arch-kalinin.txt`, `arch-su_govt.txt`, `arch-de_govt.txt`, `arch-europe-indexes-1939.txt`, `arch-be_state.txt`, `arch-nl_state.txt`, `arch-dk_state.txt`, `arch-se_state.txt`, `arch-no_state.txt`, `arch-fi_state.txt`, `arch-gr_state.txt`, `arch-ro_state.txt`, `arch-bg_state.txt`, `arch-hu_state.txt`, `arch-hu_govt.txt`, `arch-yu_state.txt`, `arch-al_state.txt`, `arch-pt_state.txt`, `arch-pt_govt.txt`, `arch-ie_state.txt`, `arch-ie_govt.txt`, `arch-ch_state.txt`, `arch-tr_state.txt`.

Africa: `arch-za_1994.txt`, `arch-eg_1961.txt`, `arch-dz_1962.txt`, `arch-ma_1957.txt`, `arch-ng_1963.txt`, `arch-ke_1964.txt`, `arch-africa-2024-chairs.txt`.

`docs/sources/ledger.json` has 47 sources. sha256 prefix `1c449461d8d33047`. 18,654 bytes. Ids 46 and 47 are the bombing survey and the Statistical Digest. Their titles were empty after the add. The titles now match the locator notes. No new id was invented.

## Fixtures

Not year-state data. Do not cite them as 1939 or 2024.

| File | sha256 prefix | What it is |
| --- | --- | --- |
| `scenarios/europe_africa/scenario.yaml` | `bd36b6800387db7e` | Rifle contact. Seed 1939. Catalog pointer only |
| `scenarios/europe_africa/factions.yaml` | `96e0569318e8c4d8` | Two sides. Food 100. Europe stockpile rifle 20 |
| `scenarios/europe_africa/units.yaml` | `016452f2366b3d91` | `eu-inf`, `af-inf`. Not an order of battle |
| `scenarios/europe_africa/industry.yaml` | `f4903d77c7482696` | Ruhr pit, Essen refiner, Essen gun line, two `from_catalog` plants, one import schedule |
| `scenarios/europe_africa/points.yaml` | `92c7643d1ea044e0` | `ruhr`, `pretoria`. Not measured cells |
| `scenarios/europe_africa/day-1.html` |  | Static picture of one finished day. Not a snapshot consumer |
| `scenarios/sample_asymmetric/scenario.yaml` |  | Scaffold. Not a `load_campaign` folder |
| `scenarios/sample_asymmetric/oob/sides.yaml` |  | Three entities. `he111`, `f16c`. Not cited |
| `scenarios/sample_asymmetric/industry.yaml` |  | Capability tags and ammo counts. Not loaded |
| `scenarios/sample_asymmetric/tracks.yaml` |  | One track. Not loaded |
| `catalogs/shared.yaml` | `edb1d40aa7c442da` | Platforms, ammo, sensors, recipes, modifiers. Not cited. Not loaded |
| `catalogs/straits.yaml` | `b641cf81bd515ac8` | Four distances. Paraphrases. Not sources. A test reads the file. The tick does not |

Section 6's tree (`tech.yaml`, `oob/<side>.yaml`, `industry/<side>.yaml`, `resources/`, `imports/`, `logistics/`, `map/terrain.yaml`, `weather.yaml`, `orders.yaml`, and the split catalogs) is not on disk. The loader does not read that tree. Do not pretend a missing file in it is loaded.

## What a later loader must not do

- Pass either year-state file to `load_campaign` until a failing test asks for it.
- Treat `from_date` as `from_day`.
- Treat the September strength count as a formation, or as the count on 1 September.
- Treat a national output as a plant cap or as a stock.
- Treat a remainder as a stock.
- Treat `22.3` as the continent.
- Treat `label: modern` as a field the tick reads.
- Average two measurements.
- Promote `catalogs/straits.yaml` to a source.
- Fill Italy's empty chair, a general, a stock, a weapon, an order, or a cell from memory.
- Copy a 1943-45 rate back onto 1 September 1939.
- Put these rows into `scenarios/europe_africa`.

## 2026-10-15 systems pass

Cell catalogs were not edited. The sea gate was not edited.

| Slot | Status |
| --- | --- |
| Air gates and fuel | fills as rules in `sim/systems/air.py`. First failure wins. A failed gate does not shoot. `sortie_ml` is two legs plus reserve. Wrong `fuel_grade` does not burn. |
| Guidance match | fills for the air path. A guided round with no table row is 0. Unguided is 1000. No new combat outcome. |
| Air combat resolution | absent. Not implemented. |
| Year-state plants, stocks, units | `select_year_catalog` reads one file. Mixing `europe_1939` and `africa_2024` is refused. Both files still have empty plants and empty stocks. The Europe strength count is not a unit. |
| Continent stocks | already closed. A plant still draws only from a connected node on its continent. |
| Cargo identity | fills. A link whose `cargo_id` is `food` does not deliver `steel`. |
| Unit attributes | examined. Catalog `catalogs/units/attributes.yaml` has `units: []`. No opened document stated ammo parts, a guidance-match integer, penetration, blast, or `rounds_per_day` for a unit. No integer was invented. The loader copies a cited field and leaves an unstated field empty. An empty guidance-match field is not a match. |
| Command and posture | fills. A head of state does not set a land posture. A seated general on the unit's `command` list does. Existing tests still pass. |
| Prediction gate | fills as a refusal. Fronts, pockets, beachheads, lifts, and full simulation stay refused until a cell has `x_mm` and `y_mm`. `prediction_gate_met` stays false. Those five were not implemented. |

## Unit attributes, 2026-10-15

No row was added. No field was filled.

| Document | Opened before | What it states | Fields taken |
| --- | --- | --- | --- |
| `docs/sources/evidence/armaments-yearbook.txt` | yes | Naval summary tables state gun counts and calibre in inches. Line 1742, column `Calibre (inches)`. | none. Calibre is not penetration, blast, guidance match, ammo parts, or `rounds_per_day`. |
| `docs/sources/evidence/statistical-digest-of-the-war-1951.pdf` | yes, for production tables | 269 pages. Text layer on 1 page. No occurrence of penetration, guidance, rounds per, rate of fire, calibre, ammunition, or blast. Previously copied tables are completions, not a unit. | none |
| `docs/sources/evidence/minerals-yearbook-1940.txt` | yes | Line 84207, `200 penetration`, is an asphalt grade. Not armor. | none |
| `docs/sources/evidence/british-war-economy-1939-1943.txt` | yes | Line 3884. Beaverbrook, 28 January 1941, says filled shells and armor-piercing shot kept in step with gun production. No penetration integer. No firing rate. | none |
| `docs/sources/evidence/british-war-economy.txt` | yes | `penetration` is administrative. Not a weapon. | none |
| `docs/sources/evidence/ussbs-german-economy-ocr.txt` | yes | Precision bombing is a directive. Not a guidance-match integer. | none |
| `docs/sources/evidence/statistisches-jahrbuch-1939.txt` | yes | Line 56111, `Kalibergbau`, is potash mining. Not a gun. | none |
| `docs/sources/evidence/usgs-1939.txt` | yes | Economic penetration. Not armor. | none |
| `docs/sources/evidence/worldsteel-2024.txt` | yes | Steel tonnes. Not a unit. | none |
| `docs/africa-capacity.md` | yes | Factory ammunition output. A plant rate, not a unit's `rounds_per_day`. Not copied. | none |
| `catalogs/shared.yaml` | not a source | Not cited. Not loaded into the attribute catalog. | none |
| `scenarios/europe_africa/units.yaml` | fixture | `penetration_mm: 20` and `blast: 15` are not a citation. Not copied. | none |

Maps, chair pages, and the ledger were not unit-performance documents. They were not re-read for this slot. Air combat resolution was not implemented.

A runnable 1939 war is not this file. The land march refuses a step onto a sea cell. A full catalog would still not be a calibration.

## Continuous color, 2026-10-15

Catalog: `catalogs/geography/regions.json`. Loader: `sim/spatial/regions.py`. Tolerance: 2 px Hausdorff between a 4-connected trace and an 8-connected trace of the same exact RGB. A component under 10,000 px is not a polygon. Colinear boundary pixels were dropped. No chord was added. Fronts, beachheads, lifts, and pathfinding were not implemented.

| Sheet | Scale bar | Origin | Polygons |
| --- | --- | --- | --- |
| CIA 8x render of `cia-africa-pol-2020.pdf`, 4896 by 6336 | 0 to 800 km, 353.0 px | pixel 3448.5, 5513.5. South is image down | 2. Sea RGB [230, 231, 232], 5,132,233 px, 9,550 vertices, 690 holes. Land RGB [217, 183, 187], 115,813 px, beside the Morocco letter. Bound to `africa_2024` |
| `uwm-agsmap023709-bartholomew-1939.jpg`, 9000 by 7140 | 0 to 320 km, 518.5 px | pixel 750, 1285.5. North is image up | 0. Exact color beside the cited marks has area 1 to 6 |
| `uwm-agdm-32265-ngs-1939.jpg`, 9000 by 6602 | 0 to 300 km, 570.12 px | pixel 916.55, 6016.5 | 0. Exact color beside Biscay has area 12. Not bound |
| `yale-15533705.jpg`, 8924 by 9573 | 0 to 800 km, 805 px | pixel 6888.5, 8795 | 0. Exact color beside Atlantic has area 1. Not bound |
| `yale-15258797.jpg`, 8096 by 9420 | 0 to 1000 km, 795.5 px | pixel 1052.5, 3143 | 0. Exact color beside Baffin has area 1. Not bound |
| `bartholomew-europe-mediterranean-1939.jpg`, 1280 by 1015 | not measured on this file | none | 0 |
| `ngs-africa-1943.jpg`, 1193 by 1280 | endpoints not readable | none | 0 |
| `europe-mediterranean-uploaded.jpg`, 1280 by 1015 | endpoints not readable | none | 0 |
| `ngs-central-europe-mediterranean-1939-08-28.jpg`, 1999 by 1467 | not measured on this file | none | 0 |

Adjacencies: 0. The two accepted polygons do not share a 4-edge. No edge was added.

`europe_1939` has no polygon. The bound Bartholomew sheet does not have a continuous exact color. `africa_2024` has the two CIA polygons. The other large CIA fills were not stored. Their surface was not verified from a cited mark. White is the page margin. Theater of War and the 1943 sheet stay unbound.

## Missing documents, 2026-10-15 pass

Search only. Zero rows added. A string that was not opened is not a source.

| Step | Missing document | Rows added |
| --- | --- | --- |
| Placed formation | No opened page states a formation name and a measured cell together. Table 10 is a strength count. The 12 British ships and 3 Egyptian frigates stay `not_placed`. The 116 names are not positions. NLS Map Area C16(360) asked for a human check. That check was not clicked. | 0 |
| Coast and strait cells | No opened sheet has a measured coast class. Bartholomew, CIA, NGS, and Yale record coast as a drawn line, not a named cell. `catalogs/straits.yaml` is a paraphrase, not a locator. The edge between a land polygon and a sea polygon was not surveyed as coast. | 0 |
| European plant rate | No opened page states a 1939 plant cap. USSBS was opened. No rate lined up. | 0 |
| African steel node | No opened page states a nameplate for a steel node at Boksburg or Somerset West. Helmsen, 7 July 2023, states the two plant rates. It does not state a mine. A place name is not a node. | 0 |
| Europe 1939 air catalog | No opened page states sensors, bands, ammo, or `rounds_per_day` for a 1939 aircraft. | 0 |
| Modern African air catalog | No opened page states sensors, bands, ammo, or `rounds_per_day` for a modern African aircraft. `scenarios/air_band` is a fixture. Its numbers were not copied. | 0 |
