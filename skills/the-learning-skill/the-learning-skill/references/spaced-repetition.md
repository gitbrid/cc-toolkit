# Spaced Repetition

The most efficient way to move information from "I learned it today" to "I still know it next year" is to review it at expanding intervals — just before you would have forgotten. This is **spaced repetition**, and it is the single most underused tool in self-directed learning.

The intuition: every time you successfully retrieve a fact, the next "forgetting curve" is flatter. The interval until your next review can therefore be longer. Each retrieval at the right time *strengthens* the memory more than re-reading ever could.

Use this for any content the user wants to retain beyond the current session — vocabulary, formulas, dates, names, definitions, code patterns, conceptual relationships, anything.

## The schedule

A simple, evidence-aligned starting schedule for a new piece of information:

- Day 0: First exposure (the lesson)
- Day 1: First review (~24 hours later)
- Day 3: Second review
- Day 7: Third review
- Day 14: Fourth review
- Day 30: Fifth review
- Day 60: Sixth review
- Day 120 / 6 months / 1 year: Long-tail reviews

If the user **passes** a review, push the next interval out further (multiply by ~2.5).
If the user **fails** a review (or hesitates badly), reset their interval to Day 1 for that item.

You don't need to invent a custom algorithm — Anki's SM-2 and FSRS already do this. If the user uses Anki, they get this for free; just generate the deck.

## Three ways to deliver spaced repetition

### Option A: Anki deck (recommended for serious memorization)

The gold standard. Generate a TSV file the user can import. They run reviews in Anki, which handles all the scheduling.

Use `scripts/generate_anki_deck.py`. The output is:
- `<topic>-anki.tsv` — tab-separated `front\tback\ttags` rows
- A short README explaining how to import it into Anki

Pros: scheduling is automatic, syncs across devices, mature ecosystem.
Cons: requires Anki software.

### Option B: Self-contained HTML flashcard app

A single `.html` file the user can open in a browser. Includes:
- Flippable cards
- "I got it" / "I didn't get it" buttons
- LocalStorage-based review schedule
- Progress tracking

Use `scripts/generate_flashcards_html.py`.

Pros: zero install, works offline, can share with friends.
Cons: less robust than Anki for serious long-term memorization.

### Option C: Markdown schedule

A plain markdown file with dated review prompts. The user manually reviews on the right day.

Use `scripts/generate_schedule.py`.

Pros: maximally portable, no software dependency.
Cons: requires user to actually open and follow it; no automatic re-scheduling on failure.

**Default offer:** unless the user has a preference, offer Anki TSV + a markdown schedule. Adventurous users get the HTML option.

## Designing good cards

The single biggest determinant of whether spaced repetition works is **card quality**. Bad cards waste the user's time and erode trust in the system.

### The minimum information principle

Each card should test **one** thing. If a card has three sub-points on the back, split it into three cards. Multi-fact cards get partial-failed often, which corrupts the scheduling signal.

### Make the question specific enough to have one answer

Bad: *"Tell me about transformers."*
Good: *"What does the 'attention is all you need' paper claim is sufficient for sequence modeling?"*

Bad: *"What's an index?"*
Good: *"In Postgres, what does a B-tree index on a single column let you do efficiently? What's its weakness for range queries on `<>`?"*

### Make the answer concise

A good answer fits in 1–3 lines. If it's longer, that card is testing too much; split.

### Use cloze deletions for sentences with key terms

Cloze cards (fill-in-the-blank) work well for definitions and statements:

> Front: A **{{c1::B-tree}}** index supports equality and range queries efficiently but not unanchored `LIKE '%foo%'` patterns.
> Back: B-tree

This format is supported by Anki natively.

### Add context for ambiguity

If "the answer is 7" depends on context, put the context on the front:

> Bad: *"What's the answer?"* → 7
> Good: *"In the example with 3 servers and 2 replicas each, what's the total number of containers?"* → 7 (3 × 2 + 1 controller)

### Include "why" cards

For deeper-than-fact knowledge, ask "why":

> Front: Why does Postgres prefer sequential scans over index scans on small tables?
> Back: When the table fits in a few pages, sequential I/O is cheaper than index lookup + heap fetch. The optimizer estimates page reads via `effective_cache_size` and `random_page_cost`.

## Workflow for generating cards from a session

After a learning session, generate cards via this process:

1. Identify the 5–15 things the user should retain. Not 50. Be ruthless. The user's review time is finite — only the most-important things deserve cards.
2. For each, draft a single card following the rules above.
3. Run the cards by the user briefly: *"Quick check — does each of these look like the right level of granularity?"*
4. Output as Anki TSV (or chosen format).

Don't try to make cards for everything covered. The point is the **most-leveraged** information.

## Common failure modes

- **Volume over quality.** Generating 100 cards "to be safe" — the user will quit after a week. Aim for 10–20 quality cards from a session.
- **Compound cards.** A card that tests three facts at once gives unclear feedback. Always split.
- **Image-on-front, text-on-back asymmetry.** Whatever's on the front is what you're testing. Decide the testing direction deliberately.
- **No feedback into the schedule.** If the user reports they failed half their reviews, you should *contract* the schedule, not march onward. The schedule is a tool, not a dogma.
- **One-shot delivery.** Generating cards once and never returning. Offer to add new cards as the user learns more, and to merge them with existing decks.

## When the user already has a system

Ask. Many users use Anki, Mochi, RemNote, Notion, or paper. Adapt to what they use:

- Anki users: generate TSV, give import instructions.
- Mochi users: generate Markdown with cloze syntax.
- Notion users: offer to write to their workspace via the Notion MCP.
- Paper users: generate a printable Markdown card list and tell them to make physical cards.
