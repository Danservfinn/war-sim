# Africa arms and munitions capacity, 2024-2026

Status: incorporated as plant nameplates. A plant cannot mint past its cited daily cap.
Date: 2026-10-14
Rule: no technical advancement. No goods from outside the continent. Foreign ownership of a plant on the continent does not import a part the continent cannot make.

This is a nameplate, not a war stock. Export contracts leave the continent. They do not fill an African dump. A target is not output. A minister's wish is not a line.

## What the sources support

SIPRI's 2024 Top 100 contains no African company. The only African firm ever in that ranking was South African, last in 2002-11.[1][2]

South Africa is the only state on the continent with a measured large-calibre line and a measured small-calibre line. Egypt has a measured small-arms and small-calibre complex. Nigeria has a resumed line whose stated output is a fraction of stated need, and whose powder is still imported.

Nobody on this continent publishes a measured airframe line, a measured tank line, or a measured electronics line for guided weapons. Those stay at zero until a source names a rate.

## Plants

Rates are integer rounds per day. `360` is the sim year. A published annual figure divides by 360, not 365.

### South Africa

Rheinmetall Denel Munition. Rheinmetall Waffe Munition 51 percent, Denel 49 percent. Large and medium calibre: 105 mm, 155 mm, mortars 60/81/120 mm, 40 mm, propellant, fuses, missile subsystems.[5]

| Plant | Place | Job | Nameplate | Status |
|---|---|---|---|---|
| rdm_boksburg | Boksburg | shell forgings | 100,000 shells/year, 277/day | capacity. Plan is 150,000, not yet output.[3] |
| rdm_somerset | Somerset West | propellant and 40 mm | 400,000 charges/year, 1,111/day | capacity. Plan is 600,000.[3] |
| rdm_wellington | Wellington | explosives and raw energetics | no round rate published | runs, 185 people in 2023[3] |
| rdm_boskop | Boskop, Potchefstroom | load, assemble, pack | no round rate published | runs, 520 people in 2023[3] |
| rdm_laingsdale | Laingsdale | fuses, safe and arm | no round rate published | 160 people in 2023[3] |

The 100,000 shell figure is the only shell nameplate with a place and a speaker. RDM's CEO, Jan-Patrick Helmsen, at Boskop, July 2023.[3] Later "double it" lines are plans. The catalog keeps 277 a day until a source reports the higher rate as output.

RDM's whole South African chain employed 2,441 people across those five sites in 2023.[3] By 2025 the firm said about 2,500, plus 1,500 tier-1 suppliers. It was investing R1 billion a year in the four manufacturing sites, and said it was doubling 155 mm capacity. Sweden's order, R7.3 billion of 155 mm for 2025-2027, is the largest in the firm's history. It is an export. It does not raise the African stock.[4]

Denel PMP, Pretoria. Small calibre 5.56 mm through 12.7 mm. Medium calibre 20 mm through 35 mm. Also 7.62x39 and 23x152. Brass strip up to 80 tons a day. No current round-per-year rate is published. The firm is seeking a partner to modernise the foundry. Liquidity, plant age, and payroll are the constraints, not demand.[6][7] Catalog rate for PMP rounds: 0, until a source names one. Brass tons are real and are not rounds.

### Nigeria

Defence Industries Corporation of Nigeria, Kaduna, founded 1964.

| Line | Figure | What it is |
|---|---|---|
| dicon_762 | 4,000,000 rounds delivered, January 2024, 7.62 mm | a delivery, not a capacity[10] |
| dicon_stated | 30,000,000 rounds/year, 83,333/day | DG Babatunde Alaya, 29 Nov 2025, stated capacity[8] |
| dicon_d7g | 60,000,000 rounds/year target | D7G CEO Osman Chennar, 22 Nov 2025. Target. Not used.[9] |
| dicon_need | 200,000,000 military + 150,000,000 police and paramilitary | Matawalle, Aug 2024. Need, not output.[11] |
| dicon_design | 12,000,000 of 7.62x51 and 4,000,000 of 9x19 per year | 1964 Fritz Werner design capacity. The line went silent after the civil war.[12] |

Gunpowder is imported. Alaya said a partner MoU would start local powder in about eight months from November 2025, aimed at August 2026. Until that plant is reported running, a Nigerian round in this sim spends imported powder, which the continent rule sets to zero.[8][16]

DICON-D7G assembled about 1,000 DG-103 rifles in two months at Kaduna from October 2025. That is knockdown assembly, not a forged receiver line.[9]

Catalog uses the stated 83,333 rounds/day, and a powder gate. No powder, no rounds.

### Egypt

Abu Zaabal Specialized Industries, Military Factory 300, Qalyubia. Opened February 2020. 371 acres, about 2,000 machines. Four factories: small and medium weapons, small-calibre ammunition, medium-calibre metal parts, and fill/assembly.[15]

Chairman Tarek Ezzat, to Al Mal, 20 April 2022:

* Small-calibre lines: 9 mm, 7.62x39, 7.62x51, 5.56x45.
* Medium-calibre metal parts: 20 mm to 40 mm, plus 40 mm grenades. About 1,400,000 parts a year.
* Fill and assembly, including 155 mm fuze assembly: about 500,000 pieces a year.
* Small-arms ammunition capacity: 50,000,000 rounds a year, 138,888 a day. Rosa El-Youssef, 19 April 2022.[13][14]

Weapons named: Helwan 920 9 mm pistol, Maadi 40 mm grenade launcher, Misr 7.62x39 rifle under Kalashnikov licence, and a locally designed 7.62x51 machine gun.[15]

155 mm projectile bodies are not in that rate. Fuze assembly is. The shell body stays at 0.

Factory 18 at Abu Zaabal makes propellant for ammunition and rocket motors. No tonnage published. It is a gate, not a rate.[unverified rate]

## What is not in the catalog

* No African firm in the SIPRI Top 100 for 2024.[1][2]
* No published African airframe rate, tank rate, or guided-weapon electronics rate. Those plants do not exist in this data. A modern kit on the continent is a prewar stock. It is not replaced.
* Algeria, Ethiopia, Sudan, Ghana, Kenya: production is claimed in secondary surveys. No primary rate survived this pass. They are omitted, not guessed.
* Rheinmetall's group target of 1.1 million or 1.5 million 155 mm shells by 2027 is a German number across several countries. It is not a South African nameplate.

## How the sim uses this

`catalogs/africa_capacity.yaml` is the source. A plant's `daily_cap` is the cited figure. `_produce` refuses to mint above it. A line with `powder_local: false` mints 0 while the continent rule holds. Export demand does not raise the cap.

## Sources

[1] SIPRI Arms Industry Database. https://www.sipri.org/databases/armsindustry
[2] SIPRI, Top 100 press release, 2025. https://www.sipri.org/media/press-release/2025/sipri-top-100-arms-producers-see-combined-revenues-surge-states-rush-modernize-and-expand-arsenals
[3] defenceWeb, RDM aiming to double production, 7 Jul 2023. https://defenceweb.co.za/editors-pick/rdm-aiming-to-double-production-expand-facilities-as-artillery-demand-soars/
[4] defenceWeb, RDM multi-billion rand investment, 2 Apr 2026. https://defenceweb.co.za/industry/industry-industry/rdm-commits-to-multi-billion-rand-investment-at-sa-investment-conference/
[5] Rheinmetall, Rheinmetall Denel Munition. https://www.rheinmetall.com/en/company/subsidiaries/rheinmetall-denel-munition
[6] defenceWeb, Denel looking for partners to modernise PMP, 13 Jul 2026. https://defenceweb.co.za/industry/industry-industry/denel-looking-for-partners-to-modernise-pmp-and-expand-market-opportunities/
[7] Denel PMP, small calibre. https://www.pmp.co.za/products/military-ammunition/small-calibre
[8] The Digger News, DICON 30m rounds, 29 Nov 2025. https://www.thediggernews.com/2025/11/29/dicon-produces-30m-rounds-of-ammunition-annually-d-g
[9] PRNigeria, DICON-D7G 1,000 rifles, 60m target, 22 Nov 2025. https://prnigeria.com/?p=174288
[10] defenceWeb, DICON resumes ammunition production, 21 Feb 2024. https://defenceweb.co.za/industry/industry-industry/nigerias-dicon-resumes-ammunition-production-as-it-continues-expansion/
[11] The Nation, Matawalle on 350m rounds, 15 Aug 2024. https://thenationonlineng.net/security-needs-350m-rounds-of-ammunition-yearly-says-minister/
[12] Daily Trust, DICON at 60, design capacity. https://dailytrust.com/new-beginning-for-dicon60/
[13] Al Mal, Factory 300 lines, 20 Apr 2022. https://almalnews.com/1252721/
[14] Rosa El-Youssef, Factory 300, 50 million rounds, 19 Apr 2022. https://daily.rosaelyoussef.com/402945
[15] Abu Zaabal Specialized Industries. https://en.wikipedia.org/wiki/Abu_Zaabal_Specialized_Industries
[16] Military Africa, Nigeria-Czech ammunition line, 8 Oct 2026. https://www.military.africa/2026/10/nigeria-czech-discuss-ammunition-production-skyfox-and-l-410ng-buy/
