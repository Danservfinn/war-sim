# war-sim

A daily continental war simulation. A side fires only what its own continent can dig, refine, and haul. Technology does not advance after day 0. Victory is complete and total surrender.

A loaded catalog is not a calibration. A printed scale is not a coast. National output series are not plants, stocks, or units.

## Run the tests

```bash
python3 -m pip install -r requirements.txt
python3 -m pytest -q
```

The live day step is `step_day` in `sim/campaign/step.py`. Architecture and the data contract are in `docs/ARCHITECTURE.md` and `docs/DATA_MANIFEST.md`.

Render an after-action page from a written log:

```bash
python3 tools/render_aar.py --log scenarios/europe_africa/aar.json --out /tmp/aar.html
```

The renderer quotes the log. It does not invent an event. It will not overwrite `day-1.html`.

## What is not in this repository

`docs/sources/evidence/` stays local. It holds third-party map scans and book text. Those works are not licensed for redistribution. Citations, with title, date, and URL, are in `docs/sources/ledger.json`. Measured place names and sheet-plane offsets are in `catalogs/cells/`. A missing scan is not a license to invent a coordinate.
