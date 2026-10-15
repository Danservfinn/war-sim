"""Trace exact-color regions. Reject a region whose second trace disagrees."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path("/Users/kublai/projects/war-sim")
OUT = ROOT / "catalogs" / "geography"
TOLERANCE_PX = 2
MIN_AREA = 10000
STRUCT4 = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=int)
# Moore neighborhood, clockwise from east.
MOORE = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]


def simplify(ring):
    if len(ring) < 4:
        return ring
    kept = []
    count = len(ring)
    for index in range(count):
        px, py = ring[index]
        qx, qy = ring[index - 1]
        rx, ry = ring[(index + 1) % count]
        if (px - qx) * (ry - py) != (py - qy) * (rx - px):
            kept.append((px, py))
    return kept or ring


def trace_ring(boundary, start, used):
    x, y = start
    # Enter from the west, so the first search starts just after that direction.
    back = 4  # index of west in MOORE
    ring = [(x, y)]
    used.add((x, y))
    guard = 0
    while guard < 2_000_000:
        guard += 1
        found = None
        for step in range(1, 9):
            direction = (back + step) % 8
            nx, ny = x + MOORE[direction][0], y + MOORE[direction][1]
            if (nx, ny) in boundary:
                found = (nx, ny, direction)
                break
        if found is None:
            return None
        x, y, direction = found
        if (x, y) == start:
            return ring
        ring.append((x, y))
        used.add((x, y))
        back = (direction + 4) % 8
    return None


def rings_of(mask):
    eroded = ndimage.binary_erosion(mask, structure=STRUCT4)
    boundary = mask & ~eroded
    ys, xs = np.where(boundary)
    pending = set(zip(xs.tolist(), ys.tolist()))
    rings = []
    while pending:
        start = min(pending)
        used = set()
        ring = trace_ring(pending, start, used)
        if not ring or len(ring) < 4:
            pending.discard(start)
            continue
        pending -= set(ring)
        rings.append(simplify(ring))
    return rings


def pip(x, y, ring):
    inside = False
    j = len(ring) - 1
    for i, (xi, yi) in enumerate(ring):
        xj, yj = ring[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi):
            inside = not inside
        j = i
    return inside


def self_test():
    mask = np.zeros((12, 12), dtype=bool)
    mask[2:8, 3:9] = True
    rings = rings_of(mask)
    assert len(rings) == 1, rings
    assert pip(5, 4, rings[0])
    assert not pip(0, 0, rings[0])


def vertices(ring, origin, scale, y_sign, source):
    ox, oy = origin
    rows = []
    for px, py in ring:
        rows.append({
            "px": int(px),
            "py": int(py),
            "x_mm": int(round((px - ox) * scale)),
            "y_mm": int(round((py - oy) * scale * y_sign)),
            "source": source,
        })
    return rows


def component_at(mask, x, y):
    if not (0 <= y < mask.shape[0] and 0 <= x < mask.shape[1] and mask[y, x]):
        return None
    lab4, _ = ndimage.label(mask, structure=STRUCT4)
    lab8, _ = ndimage.label(mask)
    a = lab4 == lab4[y, x]
    b = lab8 == lab8[y, x]
    xor = int(np.logical_xor(a, b).sum())
    if xor == 0:
        hausdorff = 0.0
    else:
        dist_a = ndimage.distance_transform_edt(~a)
        dist_b = ndimage.distance_transform_edt(~b)
        hausdorff = 0.0
        only_a = a & ~b
        only_b = b & ~a
        if np.any(only_a):
            hausdorff = max(hausdorff, float(dist_b[only_a].max()))
        if np.any(only_b):
            hausdorff = max(hausdorff, float(dist_a[only_b].max()))
    return a, b, hausdorff


def accept_color(image, seed, color, sheet):
    mask = np.all(image == np.array(color, dtype=np.uint8), axis=2)
    found = component_at(mask, seed[0], seed[1])
    if found is None:
        return None, f"seed {seed} is not color {color}"
    area4, area8, hausdorff = found
    area = int(area4.sum())
    if area < MIN_AREA:
        return None, f"area {area} below {MIN_AREA}"
    if hausdorff > TOLERANCE_PX:
        return None, f"hausdorff {hausdorff} above {TOLERANCE_PX}"
    rings = rings_of(area4)
    if not rings:
        return None, "no ring"
    sx, sy = seed
    exterior = None
    holes = []
    for ring in rings:
        if pip(sx, sy, ring):
            exterior = ring
        else:
            holes.append(ring)
    if exterior is None:
        return None, "seed outside every ring"
    holes = [ring for ring in holes if any(pip(px, py, exterior) for px, py in ring[:: max(1, len(ring)//8)])]
    ox, oy = sheet["origin"]
    scale = sheet["mm_per_px"]
    y_sign = -1 if sheet["y_positive"] == "north" else 1
    source = (
        f"{sheet['title']}. Exact RGB {list(color)}. "
        f"4-connected and 8-connected traces, Hausdorff {hausdorff} px. "
        f"{sheet['image']}"
    )
    seed_x = int(round((sx - ox) * scale))
    seed_y = int(round((sy - oy) * scale * y_sign))
    row = {
        "id": sheet["id"] + ":" + sheet["surface"],
        "sheet": sheet["id"],
        "year_state": sheet["year_state"],
        "surface": sheet["surface"],
        "image": sheet["image"],
        "image_size": [int(image.shape[1]), int(image.shape[0])],
        "origin_px": [ox, oy],
        "mm_per_px": scale,
        "y_positive": sheet["y_positive"],
        "scale_bar": sheet["scale_bar"],
        "color_rgb": [int(v) for v in color],
        "seed_px": [int(sx), int(sy)],
        "seed_x_mm": seed_x,
        "seed_y_mm": seed_y,
        "tolerance_px": TOLERANCE_PX,
        "trace_b_hausdorff_px": hausdorff,
        "trace_b": {
            "method": "8-connected exact RGB",
            "area": int(area8.sum()),
            "hausdorff_px": hausdorff,
            "identical": hausdorff == 0 and int(area4.sum()) == int(area8.sum()),
        },
        "area_px": area,
        "vertices": vertices(exterior, (ox, oy), scale, y_sign, source),
        "holes": [vertices(ring, (ox, oy), scale, y_sign, source) for ring in holes],
    }
    return row, None


def main():
    self_test()
    OUT.mkdir(parents=True, exist_ok=True)
    render = OUT / "cia-africa-8x.png"
    shutil.copy("/tmp/digest-pages/cia-africa-8x.png", render)
    image = np.asarray(Image.open(render))
    sheet = {
        "id": "cia_africa_pol",
        "title": "AFRICA",
        "image": "catalogs/geography/cia-africa-8x.png",
        "origin": (3448.5, 5513.5),
        "mm_per_px": 800_000_000 / 353.0,
        "y_positive": "south",
        "year_state": "africa_2024",
        "surface": "sea",
        "scale_bar": "0 to 800 km across 353.0 px on the 8x render",
    }
    row, reason = accept_color(image, (980, 1100), (230, 231, 232), sheet)
    print("cia sea", "accepted" if row else reason, "vertices", len(row["vertices"]) if row else 0)
    regions = []
    gaps = []
    if row:
        regions.append(row)
    else:
        gaps.append({"sheet": "cia_africa_pol", "image": sheet["image"], "reason": reason, "polygons": 0})
    # Land fill beside the cited Morocco letter. The letter pixel is ink, not the fill.
    window = image[1930:1970, 1326:1366]
    colors, counts = np.unique(window.reshape(-1, 3), axis=0, return_counts=True)
    order = np.argsort(-counts)
    land_reason = "no land color passed"
    for index in order[:4]:
        color = tuple(int(v) for v in colors[index])
        if max(color) < 80 or min(color) > 245:
            continue
        ys, xs = np.where(np.all(window == colors[index], axis=2))
        if len(xs) == 0:
            continue
        seed = (int(xs[0] + 1326), int(ys[0] + 1930))
        land = dict(sheet)
        land["surface"] = "land"
        land["id"] = "cia_africa_pol"
        found, why = accept_color(image, seed, color, land)
        print("cia land", color, "accepted" if found else why)
        if found:
            found["id"] = "cia_africa_pol:land:" + "-".join(str(v) for v in color)
            regions.append(found)
            land_reason = None
            break
        land_reason = why
    if land_reason:
        gaps.append({
            "sheet": "cia_africa_pol",
            "image": sheet["image"],
            "surface": "land",
            "reason": land_reason,
            "polygons": 0,
        })
    payload = {
        "tolerance_px": TOLERANCE_PX,
        "min_area_px": MIN_AREA,
        "rule": "Exact RGB, 4-connected. Accepted only when the 8-connected trace of the same color has Hausdorff distance at or under 2 px. Colinear boundary pixels are dropped. No chord leaves the boundary.",
        "regions": regions,
        "adjacencies": [],
        "gaps": gaps,
    }
    (OUT / "regions.json").write_text(json.dumps(payload))
    print("wrote", len(regions), "regions")


if __name__ == "__main__":
    main()
