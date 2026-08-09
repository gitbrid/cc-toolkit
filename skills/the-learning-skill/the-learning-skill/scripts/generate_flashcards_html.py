#!/usr/bin/env python3
"""Generate a self-contained HTML flashcard app from a JSON card list.

Reads the template from ../assets/flashcard_template.html and injects the
card data, deck title, and a deck ID for localStorage.

Usage:
    python generate_flashcards_html.py --cards cards.json --output deck.html --title "Topic"
    python generate_flashcards_html.py --cards-stdin --output deck.html --title "Topic"

JSON card format:
    [
      {"front": "...", "back": "..."},
      ...
    ]

The resulting HTML file is fully standalone — no internet, no install, just open it in a browser.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE = SCRIPT_DIR.parent / "assets" / "flashcard_template.html"


def deck_id_from(title: str, num_cards: int) -> str:
    """Stable deck ID for localStorage so reruns of the generator don't reset progress
    (as long as the title and card count don't change)."""
    raw = f"{title}|{num_cards}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cards", type=Path, help="Path to JSON file with card list")
    p.add_argument("--cards-stdin", action="store_true", help="Read JSON cards from stdin")
    p.add_argument("--output", type=Path, required=True, help="Output HTML path")
    p.add_argument("--title", default="Flashcards", help="Title shown in the app")
    p.add_argument("--template", type=Path, default=TEMPLATE, help="Override the HTML template path")
    args = p.parse_args()

    if args.cards_stdin:
        cards = json.loads(sys.stdin.read())
    elif args.cards:
        cards = json.loads(args.cards.read_text(encoding="utf-8"))
    else:
        print("Error: must provide --cards or --cards-stdin", file=sys.stderr)
        return 1

    if not isinstance(cards, list):
        print("Error: cards must be a list", file=sys.stderr)
        return 1

    if not args.template.exists():
        print(f"Error: template not found at {args.template}", file=sys.stderr)
        return 1

    template = args.template.read_text(encoding="utf-8")
    cards_json = json.dumps(cards, ensure_ascii=False)
    deck_id = deck_id_from(args.title, len(cards))

    output = (template
        .replace("__TITLE__", args.title)
        .replace("__DECK_ID__", deck_id)
        .replace("__CARDS_JSON__", cards_json))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8")
    print(f"Wrote {len(cards)} flashcards to {args.output}")
    print(f"Open with: open {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
