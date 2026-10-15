# Industrial capacity and logistics variables

Status: formulas implemented. Sample numbers are a model, not a historical census.
Date: 2026-10-14

A mine is not a front. The sim never reads national output. It reads what survives the path.

## What to calculate

Eight fields. Each one is a number on a node, a link, or a recipe. None of them is "modern" or "Africa".

| Field | Where it lives | How to set it |
|---|---|---|
| Source output | node, t/day by cargo id | Mine or plant throughput after local labor and power. Not GDP. |
| Capability tags | faction or plant | `welding`, `explosives`, `electronics`, `airframe`. A recipe with a missing tag builds 0. |
| Recipe inputs | catalog | Goods per unit. Runs = min of stock // input. |
| Link capacity | link, t/day | Slots on that mode. Rail: trains/day times net tons/train. Road: trucks times payload times trips/day the road can actually take. |
| Self-consumption | link, thousandths | Fuel, water, and spare parts burned to move the cargo. `kept = moved * (1000 - tax) / 1000`. |
| Transload loss | link, thousandths | Port, gauge break, or ferry. Same tax field. Do not invent a second formula. |
| Interdiction | link, thousandths | Enemy tracks on the link cut capacity before the tax. |
| Front burn | unit or formation, t/day | Ammo, fuel, food. Days of supply = arrived // burn. |

Delivered tons on one link:

```
moved = min(inbound, capacity)
arrived = moved * (1000 - self_consume_milli) / 1000
```

Delivered tons on a path is that function folded in order. The binding link is the lowest `capacity_t`. Ties take the earliest link. That name is the slot constraint. The tax is separate.

Combat never sees source output. It sees ammo `qty` in the unit buffer. Empty precision stock falls through to the next ammo id. The hit formula does not change.

## Why the Sahara and the European rail are different data

Same source: 5,000 t/day.

Sahara path, modeled slots:

| Link | Capacity t/day | Self-consume | Out |
|---|---:|---:|---:|
| Reef to Cape | 4,000 | 20 | 3,920 |
| Cape to Lagos | 2,000 | 80 | 1,840 |
| Lagos to Tripoli | 60 | 450 | 33 |

European rail, same source:

| Link | Capacity t/day | Self-consume | Out |
|---|---:|---:|---:|
| Moscow to Warsaw | 8,000 | 25 | 4,875 |
| Warsaw to Vienna | 8,000 | 25 | 4,753 |
| Vienna to Rome | 8,000 | 25 | 4,634 |

Steady state, front burn 200 t/day:

- Sahara: 33 t arrived. Throughput 6 per 1,000. Days of supply 0. Binding link `lagos-to-tripoli`.
- Rail: 4,634 t arrived. Throughput 926 per 1,000. Days of supply 23. Capacities tie, so the earliest link is named. The tax is the only loss.

The mine is identical. The front is not. A South African ore body does not move north the way a Donbass or Moscow shipment moves on double track. The sand link has almost no slots, and the trucks eat about half of what they lift.

## How to fill the fields without a region switch

Rail capacity. One restored double-track military line in the Russo-German war was scheduled around 24 train pairs a day. A German military train carried about 450 t net. One direction at that schedule is on the order of 10,000 t/day before civilian traffic, empties, and breaks of gauge. A single restored line was about half of that. Use that band for a European trunk. Cut it at each gauge break and each destroyed bridge. Do not paste "Europe" into the code.

Road capacity. A truck is a payload and a burn rate. Over a paved net the burn is a few percent of payload per day of driving. Over sand the same truck makes fewer trips, carries less, and the fuel for the outbound and return legs becomes a large share of the cargo. Set `capacity_t` from trucks times trips the track can accept. Set `self_consume_milli` from fuel liters times distance times 2, divided by payload. Cap the tax at 900 so a link cannot invent cargo, and so a suicide haul still shows a trickle.

Sea capacity. High tons, moderate tax, and a port transload. The port, not the ocean, is usually the slot.

Air capacity. Tax often exceeds payload for fuel and bulk ammo. Use it for electronics and precision fuzes. It will not feed a shell dump.

Industry. Output is recipe runs, not a steel slogan. `can_build` returns 0 if a required capability is missing, else the minimum of input stocks. A 1939 plant with `welding` and `explosives` builds unguided shells. It does not build a GPS bomb, because that recipe requires `electronics`. Adding the tag takes conversion days and goods. It is not a tech-level flag.

Interdiction. A track of quality `detected` or better on a link multiplies capacity by `(1000 - disruption_milli) / 1000` before the fold. Disruption is a catalog number for that mode, not a side bonus.

## What the fight should show

Report these four numbers every day tick, per side, per cargo:

- produced
- arrived
- binding link
- days of supply at the engaged formation

If days of supply is 0, mounts return `no_ammo` or fall through to the cheap ammo id. That is the industrial result. A modern fighter with an empty bomb rack and a 1939 battery with a full limber resolve through the same shot function.

Code: `sim/systems/combat.py`, `sim/systems/logistics.py`. Checks: `tests/test_combat.py`, `tests/test_logistics.py`.
