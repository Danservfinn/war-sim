#!/usr/bin/env python3
"""Render aar.json to aar.html. Quotes the log. Invents nothing."""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

TURNING = {
    "shot",
    "death",
    "plant_gate",
    "first_contact",
    "battle_open",
    "battle_close",
    "operation_open",
    "operation_close",
    "beachhead",
    "lift_cut",
    "pocket_open",
    "pocket_close",
    "mine_owner_change",
    "gate_zero",
    "trade_blocked",
    "war_entry",
    "state_surrender",
}
MISSING = "The log does not have this."


def _esc(value) -> str:
    if value is None or value == "":
        return html.escape(MISSING)
    return html.escape(str(value))


def _sentence(event: dict) -> str:
    text = event.get("sentence")
    if text is None or str(text).strip() == "":
        return MISSING
    return str(text).strip()


def _winner_line(log: dict) -> str:
    stop = log.get("stop")
    winner = log.get("winner")
    if stop == "limit":
        return "day limit"
    if winner is None:
        return "still at war"
    if isinstance(winner, list):
        if not winner:
            return "still at war"
        return ", ".join(str(item) for item in winner)
    return str(winner)


def _chronology(events: list) -> list[dict]:
    rows = []
    for event in events:
        if not isinstance(event, dict):
            continue
        kind = str(event.get("kind") or "")
        if kind not in TURNING and not event.get("turning_point"):
            continue
        rows.append(event)
    return sorted(rows, key=lambda row: (int(row.get("day") or 0), int(row.get("seq") or 0)))


def render(log: dict) -> str:
    scenario = _esc(log.get("scenario_id"))
    day_start = _esc(log.get("day_start"))
    day_end = _esc(log.get("day_end"))
    layer = _esc(log.get("layer") or "record")
    gate = bool(log.get("prediction_gate_met"))
    banner = (
        "Prediction gate met."
        if gate
        else "This page is not a calibration. The prediction gate is not met."
    )
    events = _chronology(list(log.get("events") or []))
    sentences = []
    for event in events:
        day = _esc(event.get("day"))
        seq = _esc(event.get("seq"))
        kind = _esc(event.get("kind"))
        place = _esc(event.get("place_name"))
        commander = _esc(event.get("commander_id"))
        sentence = html.escape(_sentence(event))
        numbers = event.get("numbers") if isinstance(event.get("numbers"), dict) else {}
        number_bits = []
        for key in sorted(numbers):
            number_bits.append(f"{html.escape(str(key))} {_esc(numbers[key])}")
        number_text = ", ".join(number_bits) if number_bits else html.escape(MISSING)
        sentences.append(
            "<tr>"
            f"<td class=\"num\">{day}</td>"
            f"<td class=\"num\">{seq}</td>"
            f"<td>{kind}</td>"
            f"<td>{place}</td>"
            f"<td>{commander}</td>"
            f"<td>{sentence}</td>"
            f"<td class=\"num\">{number_text}</td>"
            "</tr>"
        )
    if not sentences:
        sentences.append(
            "<tr><td colspan=\"7\">The log does not have this.</td></tr>"
        )
    days = list(log.get("days") or [])
    has_cells = any(isinstance(row, dict) and row.get("cells_held") is not None for row in days)
    if has_cells:
        chart_rows = []
        for row in days:
            if not isinstance(row, dict) or row.get("cells_held") is None:
                continue
            chart_rows.append(
                f"<tr><td class=\"num\">{_esc(row.get('day'))}</td>"
                f"<td>{_esc(row.get('state'))}</td>"
                f"<td class=\"num\">{_esc(row.get('cells_held'))}</td></tr>"
            )
        chart = (
            "<table><tr><th>day</th><th>state</th><th>cells held</th></tr>"
            + "".join(chart_rows)
            + "</table>"
        )
    else:
        chart = "<p>The log has no cells.</p>"
    battles = list(log.get("battles") or [])
    campaigns = list(log.get("campaigns") or [])
    battle_html = "<p>The log does not have this.</p>" if not battles else "".join(
        f"<p>Day {_esc(row.get('opened_day'))}. {_esc(row.get('place_name'))}.</p>"
        for row in battles if isinstance(row, dict)
    )
    campaign_html = "<p>The log does not have this.</p>" if not campaigns else "".join(
        f"<p>{_esc(row.get('name'))}. Day {_esc(row.get('opened_day'))} to {_esc(row.get('closed_day'))}.</p>"
        for row in campaigns if isinstance(row, dict)
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{scenario}</title>
<style>
  html, body {{ margin: 0; width: 100%; background: #101317; color: #e8e6e3; }}
  body {{ font: 20px/1.45 Georgia, "Iowan Old Style", serif; }}
  header, main {{ width: 100%; margin: 0; padding: 24px 28px; }}
  h1 {{ font-size: 32px; margin: 0 0 8px; }}
  h2 {{ font-size: 22px; margin: 32px 0 8px; }}
  .banner {{ border: 1px solid #f0d38a; color: #f0d38a; padding: 12px 14px; margin-top: 16px; }}
  .num, table {{ font-family: ui-monospace, "SF Mono", Menlo, monospace; font-size: 16px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid #2a2e33; word-break: break-word; vertical-align: top; }}
  th {{ color: #9a968f; font-weight: 600; }}
</style>
</head>
<body>
<header>
  <h1>{scenario}</h1>
  <p>Day {day_start} to day {day_end}. Layer {layer}.</p>
  <p>{html.escape(_winner_line(log))}</p>
  <div class="banner">{html.escape(banner)}</div>
</header>
<main>
  <h2>Chronology</h2>
  <table>
    <tr><th>day</th><th>seq</th><th>kind</th><th>place</th><th>commander</th><th>sentence</th><th>numbers</th></tr>
    {''.join(sentences)}
  </table>
  <h2>Charts</h2>
  {chart}
  <h2>Battles</h2>
  {battle_html}
  <h2>Campaigns</h2>
  {campaign_html}
</main>
</body>
</html>
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    log_path = Path(args.log)
    out_path = Path(args.out)
    if out_path.name == "day-1.html":
        print("refusing to overwrite day-1.html", file=sys.stderr)
        return 3
    if not log_path.is_file():
        print("log was not written", file=sys.stderr)
        return 2
    log = json.loads(log_path.read_text())
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render(log))
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
