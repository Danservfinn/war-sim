# Missing variables: weapons, stocks, and the date

Status: folded into `docs/ARCHITECTURE.md` on 2026-10-14. This note is the gap list that drove that edit. The architecture is the source of truth.

The shot function and the path tax are real. They still cannot say what a military can fire on day 400. A mount with a qty list is a loadout, not an army.

## What is already enough

- Hit chance is a product of accuracy, skill, weather, guidance match, and signature.
- Penetration is millimeters against a plate. Fail means no structural damage.
- Empty precision qty falls through to the next row. The formula does not change.
- Path delivery is `min(inbound, capacity) * (1000 - tax) / 1000`.
- A recipe with a missing capability builds 0.

## What is missing

### 1. A round is not a bill of materials

`gps_bomb` and `unguided_he` are names. They do not say how many tons of steel, propellant, explosive, copper, and electronics one round is. Without mass and a parts list, 33 t arrived cannot become a round count, and a factory cannot be starved of one precursor.

Add, on the ammo catalog, not on the side:

```yaml
ammo_id: 155mm_he
mass_kg: 43
volume_l: 18
parts:
  shell_body: {good: steel, kg: 35}
  filler: {good: explosives, kg: 7}
  fuze: {good: fuzes, qty: 1}
  charge: {good: propellant, kg: 12}
dud_milli: 20
storage_days: 1800
accepts_kit: []          # empty means the body is the whole round
```

A precision round is the same body plus a kit that can be out of stock by itself:

```yaml
ammo_id: 500lb_body
mass_kg: 227
parts:
  body: {good: steel, kg: 140}
  filler: {good: explosives, kg: 87}
accepts_kit: [gps_kit, none]
```

`gps_kit` is its own catalog row: mass, electronics qty, and a guidance value. The bomb body can fly as unguided when the kit qty is 0. That is the fall-through, and it is a parts check, not a name check.

### 2. The mount does not know what it can fire

`select_ammo` takes the first row with qty > 0. An 88 mm gun can currently "fall through" to a GPS bomb if that row is next.

Add `accepts: [ammo_id, ...]`, `caliber_mm`, and `domain`. A shot is legal only if the ammo id is in `accepts` and every part and kit in that row has qty > 0. No legal row means `no_ammo`. Do not skip to an incompatible id.

### 3. A shot consumes a set, not one integer

Firing is blocked by the first zero in this set:

- compatible round in the ready rack
- propellant charge, if the catalog lists one
- fuze
- seeker kit, if the selected loadout uses one
- platform fuel for the sortie or the displacement
- a filled crew billet for the mount
- a fire-control item, or the degraded accuracy row if it is missing
- barrel life remaining, or the worn-barrel accuracy row

Ready rack and unit dump are different stocks. `ready_qty` is what the mount can fire this tick. `dump_qty` refills the rack at `reload_s`, and only if the crew billet is filled. The formation buffer refills the dump only when a supply link delivered that cargo id.

### 4. The weapon's numbers must move when parts are missing

`tech_level` is unused. Accuracy and penetration are fixed on the range band. That hides the difference between a gun with sights and a gun without them.

Put the effect on the missing part, as a second row, not as an era:

| Missing part | What changes |
|---|---|
| Fire control or optical sight | Use `accuracy_degraded` on the band. Range cap may drop. |
| Seeker kit | Guidance match becomes the `none` row. Same body, worse hit chance. |
| Worn barrel (`rounds_fired` > `barrel_life`) | Accuracy times `wear_milli / 1000`. |
| Green crew | Already a skill input. Keep it. Do not add a second morale hack. |
| No meteorological data | Weather factor uses the worse catalog row. |
| Dud | Roll `dud_milli` before hit chance. A dud spends the round and misses. Industrial strain raises `dud_milli`. |

Penetration stays a property of the ammo id and the plate. Do not scale it by year.

### 5. There is no resource node under the factory

Source output is a given 5,000 t/day. A real plant stops when one input stops. South African chrome does not make South African aviation fuel. A 1939 European plant does not make a GPS kit because the electronics good does not exist in its stocks.

Add resource nodes and a goods ledger:

```yaml
node: witwatersrand
outputs: {coal: 800, chrome: 40, gold: 1}   # t/day, model tons
cannot_output: [oil, explosives, electronics]
```

A recipe runs only if every input good is in the local ledger or arrived on a link this day. `can_build` already returns 0 for a missing capability. Extend it to return 0 for a missing good, and to decrement the ledger by the inputs. Output mass must equal the ammo `mass_kg` times runs, or the recipe is inconsistent and the loader rejects it.

Imported finished weapons are a node outside the map with a finite stock and a sea or air link. When that stock hits 0 and no domestic recipe can run, the army cannot replace the weapon. That is how a modern force with no industrial base becomes a 1939 force that still owns the airframes.

### 6. There is no date

"At a given point in the war" needs `day` on the clock and three curves, all data:

- `stock_at_day0` per depot and per unit
- `recipe.available_after_day` so a line cannot start early
- `recipe.daily_cap` so a line cannot jump to infinite output the day it unlocks

Day 0 of a 1939 European side has artillery ammo, optical sights, and no GPS kits. Day 0 of a modern African side may have a finite import of precision kits and almost no domestic explosives line. Both are ledger rows. Neither is a branch in combat.

### 7. Losses do not come back

Combat can cut integrity and crew. Nothing writes a replacement demand. A destroyed mount must enqueue:

- one platform, if a recipe and the goods exist
- crew billets, which cost training days, not just tons
- the ammo that was on board, which is gone

Training days are the slow variable. Steel can arrive in a week. A gunner at skill 70 cannot. Crew pools are a stock with a daily graduation cap. Empty billets cut skill to 0 and block the mount.

### 8. Scarce cargo is not allocated

`supply_priority` is a field and unused. Two fronts on one thin link need a rule. Sort formations by priority, then by id. Each takes its burn until the arrived cargo is gone. The loser does not get a hidden reserve. Its legal loadout drops to whatever ammo id it still holds. That is how one army fights with precision on the decisive front and unguided shells everywhere else, in the same tick, with the same catalogs.

### 9. Tons are not rounds

Path delivery is in tons. The unit buffer is in rounds. Convert at the depot, not in the shot function:

```
rounds = arrived_kg / mass_kg
```

A 33 t Sahara arrival of mixed cargo might be 0 GPS kits and a few hundred shells, or 33 t of chrome that no local plant can turn into either. The cargo id has to survive the path. A ton of chrome is not a ton of ammunition.

## The chain that makes the weapon true

```
resource node
  -> goods ledger
  -> recipe (capability, inputs, available_after_day, daily_cap)
  -> depot rounds and kits
  -> path delivery by cargo id
  -> allocation by priority
  -> unit dump, then ready rack
  -> legal loadout (mount.accepts and every part qty > 0)
  -> shot consumes the set
  -> losses and expenditure re-enter the ledger as demand
```

At any day, the weapon in use is the best legal loadout, not the platform's `guidance_default`. Best means highest catalog effect among rows that pass the parts check. Effect is penetration, blast, and hit chance against the target class. If the precision kit is absent, the body flies unguided. If the body is absent, the mount does not fire. If the fuel is absent, the aircraft does not reach the bubble.

## What not to add

- No year multiplier on damage.
- No "Africa cannot supply" flag. The Lagos-Tripoli link already does that if its capacity and tax are honest.
- No free substitution across calibers.
- No tech_level in the hit product. Parts and kits are the tech.

## Smallest next cut

1. Ammo catalog gains `mass_kg`, `parts`, `accepts_kit`, `dud_milli`.
2. Mount gains `accepts`. `select_ammo` refuses incompatible ids.
3. Ledger and `available_after_day` so day 0 stocks and day N output differ.
4. Depot converts arrived kg of a cargo id into rounds. Combat reads rounds.
5. One test: same factory, GPS kits exhausted, mount fires the body as unguided, and a second front with lower priority receives none.
