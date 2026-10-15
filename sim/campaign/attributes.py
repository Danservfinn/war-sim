"""Unit attribute rows. A missing citation is a refusal. A missing field stays empty."""

from __future__ import annotations

from pathlib import Path

import yaml


_FIELDS = ("ammo_parts", "guidance_match", "penetration", "blast", "rounds_per_day")
_CATALOG = Path(__file__).resolve().parents[2] / "catalogs" / "units" / "attributes.yaml"


def _cited(row: dict) -> bool:
    return bool(str((row or {}).get("source") or "").strip())


def load_cited_attributes(rows: list) -> list:
    """Copy stated fields. Do not fill a blank with 0 or 1000."""
    if not rows:
        raise ValueError("cited source missing")
    kept = []
    for row in rows:
        if not _cited(row):
            raise ValueError("cited source missing")
        copied = {"id": row.get("id"), "source": str(row["source"]).strip()}
        for key in _FIELDS:
            value = row.get(key)
            copied[key] = None if value in (None, "") else value
        kept.append(copied)
    return kept


def require_cited_attributes(rows: list) -> list:
    """An empty table is a refusal. A cited partial row is not a guess."""
    if not rows:
        raise ValueError("cited source missing")
    return load_cited_attributes(rows)


def guidance_succeeds(row: dict) -> bool:
    """An empty guidance-match field is not a match. 0 and 1000 are not defaults."""
    value = (row or {}).get("guidance_match")
    if value in (None, ""):
        return False
    return int(value) > 0


def load_attribute_catalog(path: Path | None = None) -> list:
    """Read the on-disk catalog. An empty file is an empty table, not a guess."""
    target = path or _CATALOG
    raw = yaml.safe_load(target.read_text()) or {}
    rows = raw.get("units") or []
    if not rows:
        return []
    return load_cited_attributes(rows)
