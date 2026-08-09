#!/usr/bin/env python3
"""Generate an Anki-compatible TSV from a JSON card list.

Anki imports tab-separated files with format:
    front\tback\ttags

Usage:
    python generate_anki_deck.py --cards cards.json --output deck.tsv [--deck-name "My Deck"]
    python generate_anki_deck.py --cards-stdin --output deck.tsv

JSON input format (a list of cards):
    [
      {"front": "...", "back": "...", "tags": ["tag1", "tag2"]},
      ...
    ]

Cloze deletions (Anki-native): use {{c1::word}} syntax in the front field. Ignore the
back field if all your cards are cloze; the script will still produce a valid file.

The output file is tab-separated; tabs and newlines inside fields are escaped to
keep Anki happy.
"""

import argparse
import json
import sys
from pathlib import Path


def escape_field(text: str) -> str:
    """Anki TSV: escape tabs and convert newlines to <br> for HTML rendering."""
    if text is None:
        return ""
    s = str(text)
    s = s.replace("\t", "    ")
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = s.replace("\n", "<br>")
    # Wrap simple markdown-style code with HTML for Anki
    # (Anki renders HTML by default when "Allow HTML in fields" is on, which is the default.)
    import re
    s = re.sub(r"```([a-zA-Z0-9]*)\n([\s\S]*?)```",
               lambda m: f"<pre><code>{m.group(2).rstrip()}</code></pre>",
               s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s


def write_tsv(cards: list[dict], output_path: Path, deck_name: str | None) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        # Anki accepts a couple of header lines starting with #.
        f.write("#separator:tab\n")
        f.write("#html:true\n")
        if deck_name:
            f.write(f"#deck:{deck_name}\n")
        f.write("#columns:Front\tBack\tTags\n")
        for card in cards:
            front = escape_field(card.get("front", ""))
            back = escape_field(card.get("back", ""))
            tags = card.get("tags", [])
            tags_str = " ".join(t.replace(" ", "_") for t in tags) if tags else ""
            f.write(f"{front}\t{back}\t{tags_str}\n")


def write_readme(output_path: Path, deck_name: str, num_cards: int) -> None:
    """Drop a small README next to the TSV with import instructions."""
    readme = output_path.parent / f"{output_path.stem}-README.md"
    content = f"""# {deck_name} — Anki Deck Import

This folder contains an Anki-compatible TSV file with **{num_cards} cards**.

## How to import into Anki

1. Open Anki (https://apps.ankiweb.net if you don't have it).
2. Click **File → Import** (or press Ctrl/Cmd+Shift+I).
3. Select `{output_path.name}`.
4. In the import dialog:
   - **Type:** Basic
   - **Deck:** {deck_name} (or pick / create another)
   - **Field separator:** Tab
   - **Allow HTML in fields:** ON (the file uses some HTML for formatting)
5. Click **Import**.

## Reviewing

- Anki will schedule cards using its FSRS / SM-2 algorithm. Just hit "Show Answer", then rate Again / Hard / Good / Easy.
- Aim for ~20 minutes a day — short, daily reviews beat long weekend cram sessions.
- If you find yourself failing the same card repeatedly, the card is probably testing too much at once. Edit it and split.

## Updating the deck

If you re-run the generator and re-import, Anki will update existing cards based on the front field as the unique key. New cards will be added; existing card scheduling is preserved.
"""
    readme.write_text(content, encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cards", type=Path, help="Path to JSON file with card list")
    p.add_argument("--cards-stdin", action="store_true", help="Read JSON cards from stdin")
    p.add_argument("--output", type=Path, required=True, help="Output TSV path")
    p.add_argument("--deck-name", default=None, help="Name of the Anki deck (added as comment header)")
    p.add_argument("--no-readme", action="store_true", help="Skip README generation")
    args = p.parse_args()

    if args.cards_stdin:
        try:
            cards = json.loads(sys.stdin.read())
        except json.JSONDecodeError as e:
            print(f"Error: invalid JSON on stdin: {e}", file=sys.stderr)
            return 1
    elif args.cards:
        try:
            cards = json.loads(args.cards.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading cards file: {e}", file=sys.stderr)
            return 1
    else:
        print("Error: must provide --cards <file> or --cards-stdin", file=sys.stderr)
        return 1

    if not isinstance(cards, list):
        print("Error: cards JSON must be a list of {front, back, tags} objects", file=sys.stderr)
        return 1

    deck_name = args.deck_name or args.output.stem.replace("-anki", "").replace("_", " ").title()
    write_tsv(cards, args.output, deck_name)
    if not args.no_readme:
        write_readme(args.output, deck_name, len(cards))

    print(f"Wrote {len(cards)} cards to {args.output}")
    if not args.no_readme:
        print(f"Wrote import instructions to {args.output.parent / (args.output.stem + '-README.md')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
