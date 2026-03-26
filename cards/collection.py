"""
Sports card collection manager — CRUD operations on a JSON-backed collection.
"""

import json
import uuid
from datetime import date
from pathlib import Path

COLLECTION_FILE = Path(__file__).parent / "data" / "collection.json"


def _load() -> list[dict]:
    if COLLECTION_FILE.exists():
        with open(COLLECTION_FILE) as f:
            return json.load(f)
    return []


def _save(cards: list[dict]):
    COLLECTION_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(COLLECTION_FILE, "w") as f:
        json.dump(cards, f, indent=2)


def add_card(
    player: str,
    year: str,
    card_set: str,
    card_number: str,
    sport: str,
    condition: str,
    raw_value: float,
    notes: str = "",
) -> dict:
    """Add a card to the collection. Returns the new card record."""
    card = {
        "id": uuid.uuid4().hex[:8],
        "player": player,
        "year": year,
        "set": card_set,
        "card_number": card_number,
        "sport": sport,
        "condition": condition,
        "raw_value": raw_value,
        "notes": notes,
        "date_added": str(date.today()),
    }
    cards = _load()
    cards.append(card)
    _save(cards)
    return card


def list_cards(
    sort_by: str = "player",
    sport: str | None = None,
    min_value: float | None = None,
) -> list[dict]:
    """Return cards, optionally filtered and sorted."""
    cards = _load()
    if sport:
        cards = [c for c in cards if c["sport"].lower() == sport.lower()]
    if min_value is not None:
        cards = [c for c in cards if c["raw_value"] >= min_value]

    valid_sorts = {"player", "year", "raw_value", "sport", "date_added", "set"}
    key = sort_by if sort_by in valid_sorts else "player"
    reverse = key == "raw_value"  # highest value first
    cards.sort(key=lambda c: c.get(key, ""), reverse=reverse)
    return cards


def get_card(card_id: str) -> dict | None:
    """Find a single card by ID."""
    for c in _load():
        if c["id"] == card_id:
            return c
    return None


def update_card(card_id: str, **fields) -> dict | None:
    """Update one or more fields on a card. Returns updated card or None."""
    cards = _load()
    for card in cards:
        if card["id"] == card_id:
            for k, v in fields.items():
                if k in card:
                    card[k] = v
            _save(cards)
            return card
    return None


def remove_card(card_id: str) -> bool:
    """Remove a card by ID. Returns True if found and removed."""
    cards = _load()
    before = len(cards)
    cards = [c for c in cards if c["id"] != card_id]
    if len(cards) < before:
        _save(cards)
        return True
    return False


def collection_summary() -> dict:
    """Return aggregate stats about the collection."""
    cards = _load()
    if not cards:
        return {"total_cards": 0, "total_value": 0, "by_sport": {}, "by_year": {}}

    by_sport: dict[str, int] = {}
    by_year: dict[str, int] = {}
    total_value = 0.0

    for c in cards:
        by_sport[c["sport"]] = by_sport.get(c["sport"], 0) + 1
        by_year[c["year"]] = by_year.get(c["year"], 0) + 1
        total_value += c["raw_value"]

    return {
        "total_cards": len(cards),
        "total_value": round(total_value, 2),
        "by_sport": dict(sorted(by_sport.items(), key=lambda x: -x[1])),
        "by_year": dict(sorted(by_year.items())),
    }
