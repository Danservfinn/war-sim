# REA plan: map interface that tracks units at scale

Date: 2026-10-14
Status: plan only. No capture, no code, no install.

## Decision

Target assumption: **Command: Modern Operations** (Warfare Sims / Matrix Games). That is the shipped interface where thousands of air, sea, and land units move on one map, aggregate into groups, and stay selectable while time is compressed.

Do not buy it from this plan. Do not decompile it. Do not copy its scenario database, unit stats, or combat math.

REA boundary: observe public docs and, only if a legally owned copy is running, the UI. Rebuild the interaction independently. Proprietary formulas and paywalled data stay out.

## What "at scale" actually is

The public manual already names the mechanism. Group view is the default. One symbol stands for a group. Keypad 9 switches to unit view, which draws every unit. Selection, datablocks, plotted courses, hover info, ORBAT search, and "track selected unit" (T) sit on top of that. Three minimaps cover global, scenario, and local extent.

Scale is not "draw 10,000 sprites every frame." Scale is:

1. Ground truth lives in the sim.
2. The map draws an aggregated contact picture.
3. Zoom, selection, or contact promotes a bubble to individual symbols.
4. Time compression changes the sim tick, not the draw rate.

That split is the thing to spec. Everything else is chrome.

## Surfaces, in order

### 1. Public manual (do this first, no install)

URL: https://command.matrixgames.com/manual/

REA path: headless Chrome, `list_browser_targets`, `inspect_web_page`, then `capture_browser_scenario` on the UI chapters only.

Read, do not scrape the whole site:

- 5.0 interface overview
- 5.1-5.2 map and camera
- 5.8 context menus, group vs unit view, right-side info panel
- Message log, ORBAT, hover datablock, track-selected-unit

Output: `docs/observed-map-ui.md` with one row per control: name, gesture, what it changes, what it must not change.

### 2. Owned-copy UI observation (only after a yes)

If a legally owned copy is running, record gestures, not binaries.

Scripted passes, each one short:

1. Pan, zoom, jump to unit, track unit, stop tracking.
2. Toggle group view and unit view. Count symbols before and after.
3. Select one unit, select a group, plot a 3-point course, drag a waypoint.
4. Hover a friendly and a contact. Note which fields appear.
5. Compress time. Note whether symbols interpolate or snap, and whether off-screen units still update the ORBAT.

Refuse: memory dumps, `batch_decompile`, asset extraction, license bypass, scenario-file decryption.

A Windows-only build is a stopper without a Windows host. Do not stand up a crack or a borrowed install to get past that.

### 3. Independent interface spec

Write `docs/map-interface-spec.md` from the observation notes plus public wargame practice. No Command assets, colors, or icon sheets.

Required behaviors:

- Camera: pan, zoom-at-cursor, bookmarks, track-selected.
- Two draw modes: formation symbol and platform symbol. Same entity, different render proxy.
- Selection set with a class summary ("4 fighters, 1 tanker").
- Course as an ordered waypoint list, edited on the map.
- Hover card only on an explicit modifier, so it does not cover the map.
- Side contact picture, not ground truth, for hostile icons.
- Minimap with three extents: world, scenario, view.
- ORBAT list that stays open and can jump the camera.

LOD rule, stated so the sim can honor it later:

| Zoom or state | Drawn | Simulated |
|---|---|---|
| Strategic | Formation symbol, one track | Aggregate motion, hourly logistics |
| Contact bubble | Platform symbols | Tactical detection and weapons |
| Selected | Datablock + course + sensor range | Same entity, no extra fidelity tax |

Promotion into a contact bubble is a sim event. The renderer does not invent units.

## What this does not design

Combat resolution, industrial production, and the 1939-vs-modern data model stay in the architecture doc. This plan only locks the map contract those systems must feed:

- A renderer-facing snapshot: id, side, posture, symbol class, position, heading, speed, contact quality, formation id, selected.
- An order channel: plot course, set speed, join or leave formation, track.
- A clock the UI can pause, step, and compress without owning the sim.

No "modern always wins" flag. A 1939 bomber and a modern fighter are the same snapshot shape. The icon and the datablock come from catalog fields.

## File layout when approved

```
projects/war-sim/docs/
  rea-map-interface-plan.md    this file
  observed-map-ui.md           filled by pass 1
  map-interface-spec.md        filled by pass 3
```

No `sim/` code until the spec is approved.

## Stop line

Pass 1 is public and can start on approval. Pass 2 waits on ownership. Pass 3 is a spec, not a port of their engine.
