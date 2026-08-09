# Learning Roadmap

A roadmap is the difference between *learning a topic* and *meandering near a topic*. It is a sequenced, time-bounded plan that takes the user from where they are now to a stated outcome, with checkpoints along the way that prove they've actually moved.

Use this for any goal that meaningfully exceeds a single session — a multi-week or multi-month learning effort. Don't roadmap a 30-minute Q&A.

## The shape

Every roadmap has the same structure:

```
[Starting point] → [Stage 1] → [Stage 2] → ... → [Stated outcome]
                       ↓             ↓
                  [Checkpoint]  [Checkpoint]
```

Each **stage** is a coherent chunk of learning that produces a defined ability. Each **checkpoint** is a concrete demonstration that the stage has actually been internalized — not a fuzzy "I feel comfortable with this".

## Building the roadmap

### Step 1 — Get the destination right

Force specificity. *"Learn data engineering"* is not a destination. Possible refinements:

- *"By Aug 1, ship a self-serve daily-batch ELT pipeline that ingests our Salesforce export into a BigQuery warehouse and powers a Looker dashboard"*
- *"By Aug 1, pass the Snowflake SnowPro Core certification"*
- *"By Aug 1, be able to lead the design discussion for our next pipeline rebuild"*

These three goals require *very different* roadmaps. You cannot design the road without the destination.

### Step 2 — Audit the starting point

Quickly figure out what the user already knows. (See `references/weakness-assessment.md` for the deeper version.) For a roadmap, you need a rough read, not a full audit:

- What's their background?
- What have they tried before?
- What do they think their main gaps are?

### Step 3 — Lay out 3–7 stages

Stages should be:

- **Sequenced**: each stage builds on the previous. If stage 3 doesn't depend on stage 2, you may have non-sequential prerequisites — restructure.
- **Bounded in time**: each stage gets a target duration (e.g., "Week 1–2", "Days 1–3"). The whole thing should add up to the user's time budget, not exceed it.
- **Self-contained outcomes**: each stage should produce a tangible ability. *"Understand X"* is fuzzy; *"Be able to write Y"* is testable.

A typical 3-month roadmap has 5–6 stages. A 2-week roadmap has 3–4. Don't pad with subdivisions; if a stage is 2 days, that's fine.

### Step 4 — Add resources to each stage

For each stage, name **specific** resources:

- **Reading**: book chapters, articles, papers, docs sections (with URLs/page numbers)
- **Watching**: courses, lectures, talks (with timestamps when relevant)
- **Doing**: exercises, problems, mini-projects
- **Asking**: who/what to consult when stuck

Specific is the operative word. *"Read about indexing"* is bad; *"Read Postgres docs § 11.3 (Multicolumn Indexes) and Chapter 8 of 'Database Internals' by Petrov"* is good. If you don't know the right resource, say so and offer to research.

### Step 5 — Define checkpoints

A checkpoint is a *test* that the stage was actually internalized. Forms:

- A working artifact ("by end of stage 2, you have a working `n`-gram language model in 50 lines of Python")
- A teach-back ("explain this back to me without notes")
- An applied problem ("solve this 3-problem set in under an hour")
- An external test (a unit on a course; a quiz)

Tie each checkpoint to a **measurable threshold**. "I sort of get it" is not a checkpoint.

### Step 6 — Set the cadence

How often does the user touch this? Realistic options:

- **Daily**: 30 min/day, sustainable for ~3–6 weeks before fatigue
- **Weekday**: 1 hour, every workday — for serious goals
- **Twice-weekly**: 2 hours, sustainable for months
- **Weekend**: 3–4 hours per weekend, slow burn for a year+

Match the cadence to the time budget *and* the user's actual life. A roadmap that requires 2 hours a day will fail if the user has a job and small kids. Talk about the realistic budget.

## Format

Output as a markdown file. Sample structure:

```markdown
# [Topic] Learning Roadmap — [Time horizon]

**Goal:** [one-sentence destination]
**Time budget:** [hours/week, total horizon]
**Starting point:** [user's current level]

## Stage 1 — [Stage name] (Week 1)

**Outcome:** [What you'll be able to do after this stage]

**Resources:**
- [Specific resource 1 with link]
- [Specific resource 2 with link]
- [Practice problem set]

**Checkpoint:** [How we'll test that this stage stuck]

## Stage 2 — [...]

...

## Reviews & spaced repetition

[Note where reviews of earlier stages happen — typically a 30-min retrieval block once a week]

## When you finish

[What "graduation" looks like — the project, certificate, talk you can give, etc.]
```

## Common failure modes

- **Non-falsifiable outcomes.** "Become comfortable with X" — can't be checked. Replace with a checkpoint.
- **Resource dumps.** Listing 30 books per stage. Pick 1–3 high-leverage resources per stage; over-listing is a way to avoid choosing.
- **Linear-only structure.** Real learning is iterative — you go back to earlier topics with more sophistication. Build in *spiral* reviews where stage 4 reuses stage 1's content at a higher level.
- **No spaced reviews.** Without weekly recall checkpoints on prior stages, the user finishes the roadmap having forgotten stages 1–3.
- **Mismatched difficulty curve.** Stage 1 is "read intro chapter", stage 2 is "implement BERT". Smooth the curve.
- **Imaginary time budget.** The user said "I have 3 hours a week", you built a 10-hour-a-week plan. The plan dies in week 2.
- **No re-planning.** Roadmaps are wrong on first contact. Build in a re-planning checkpoint at ~25% — *"At end of week 1, revisit this and adjust based on actual pace."*

## Example: 6-week Rust roadmap

Goal: be able to write idiomatic Rust for a small CLI tool by week 6, comfortable enough to maintain it without continuous reference-checking.

```markdown
## Stage 1 — Ownership, borrowing, lifetimes (Week 1)
**Outcome:** Can read and explain ownership-related compiler errors. Can write simple functions that pass references correctly.
**Resources:** "The Rust Programming Language" Ch. 4. Rustlings exercises 1–10.
**Checkpoint:** Take 5 ownership-error-producing snippets, explain what's wrong with each.

## Stage 2 — Structs, enums, pattern matching, error handling (Week 2)
**Outcome:** Can model a small domain in Rust types. Can use Result/Option idiomatically.
**Resources:** TRPL Ch. 5–6, 9. Rustlings 11–25.
**Checkpoint:** Build a tiny CLI that takes a path, parses a CSV, returns errors via Result.

## Stage 3 — Traits, generics, lifetimes-in-types (Week 3)
**Outcome:** Can write generic code with constraints. Comfortable reading trait bounds.
**Resources:** TRPL Ch. 10. "Crust of Rust" YouTube series, episodes on lifetimes.
**Checkpoint:** Build an iterator adapter that takes a function and skips items matching it.

## Stage 4 — Async/await, tokio basics (Week 4)
**Outcome:** Can write an async function, understand .await, use tokio for I/O.
**Resources:** Tokio mini-tutorial. "Async Book" Ch. 1–3.
**Checkpoint:** Tiny TCP echo server with tokio.

## Stage 5 — Build the project (Weeks 5–6)
**Outcome:** A working CLI tool of your choosing (~500 lines).
**Resources:** clap docs, your earlier projects, std docs as needed.
**Checkpoint:** Demo the tool, walk through the architecture in your own words.

## Reviews
- Every Sunday: 30-min recall block on the previous week's concepts (we'll use the flashcards we generate).
- End of week 3: revisit week 1's ownership material — you'll see it with new eyes.
```

That's a roadmap a user can actually follow.
