# Scripts

These scripts produce durable artifacts from learning sessions. Use them so you don't have to hand-craft HTML or schedules every time.

| Script | Purpose | Input | Output |
|---|---|---|---|
| `generate_anki_deck.py` | Make an Anki-importable deck | JSON cards `[{front, back, tags}]` | `.tsv` + README |
| `generate_flashcards_html.py` | Make a self-contained HTML flashcard app | JSON cards `[{front, back}]` | `.html` |
| `generate_quiz_html.py` | Make a self-contained HTML quiz app | JSON questions (mcq / true_false / short_answer) | `.html` |
| `generate_schedule.py` | Make a spaced-repetition schedule | `--topic`, optional intervals | `.md` + `.ics` |
| `generate_cheatsheet_pdf.py` | Make a printable PDF cheatsheet (0.5" margins) | Markdown file or `--dir` containing `notes.md` | `.pdf` |

## Common patterns

### Quick flashcard deck for a session

```bash
echo '[
  {"front": "What does the `WAL` in PostgreSQL stand for?", "back": "Write-Ahead Log"},
  {"front": "Why is WAL written before the data page changes?", "back": "Crash recovery: replaying the WAL after a crash recovers committed transactions even if data pages weren't yet flushed."},
  {"front": "What flag enables synchronous WAL writes?", "back": "synchronous_commit = on (the default)"}
]' | python generate_flashcards_html.py --cards-stdin --output postgres-wal-cards.html --title "Postgres WAL"
```

### Quiz from session

```bash
echo '[
  {"type": "mcq", "question": "Which Postgres parameter controls whether WAL records are flushed to disk before commit returns?",
   "options": ["fsync", "synchronous_commit", "wal_compression", "checkpoint_segments"],
   "answer": 1,
   "explanation": "synchronous_commit = on means commit only returns after WAL is flushed. fsync = on means writes are durable but doesnt by itself control commit-time flush."}
]' | python generate_quiz_html.py --questions-stdin --output quiz.html --title "Postgres Durability"
```

### Spaced repetition schedule

```bash
python generate_schedule.py --topic "Postgres WAL" --output-dir ./study/
# Produces:
#   ./study/postgres_wal-schedule.md
#   ./study/postgres_wal-schedule.ics  (importable into Google Calendar)
```

### Anki TSV

```bash
python generate_anki_deck.py --cards cards.json --output postgres.tsv --deck-name "Postgres Internals"
```

### Printable PDF cheatsheet

Generated at the end of a run for each artifact directory. Reads `notes.md` from the run directory (or any markdown file you point at) and writes `cheatsheet.pdf` next to it with 0.5" margins.

```bash
# Conventional: cheatsheet for a run directory containing notes.md
python generate_cheatsheet_pdf.py --dir ./postgres-wal-20260507-1430/ --title "Postgres WAL"

# Ad-hoc: explicit input/output
python generate_cheatsheet_pdf.py --input notes.md --output cheatsheet.pdf --title "Postgres WAL"
```

The script auto-detects a PDF backend (Chrome / Chromium headless → `weasyprint` → `wkhtmltopdf`). If none is installed, it writes the styled HTML, prints platform-specific install instructions, and exits non-zero — install one and re-run rather than skipping the PDF.

## Notes

- The HTML scripts inject your data into `assets/<template>.html`. Don't edit that template casually — the placeholders matter.
- All HTML output is fully standalone — no internet required, no build step.
- Anki TSV output uses `#html:true` so basic formatting (code, bold, line breaks) survives.
- The schedule script defaults to a 7-stage SM-2-inspired curve. Override `--intervals` for different cadences (e.g. weekly: `7,14,21,28,60,120`).
