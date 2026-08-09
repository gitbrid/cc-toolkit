# Source Distillation

When the user hands you source material — links, PDFs, articles, transcripts, code, books, pasted text — your first job is **not** to summarize it. Summarizing is a parlor trick LLMs are fine at. Your actual job is to *distill* the material into the structure that makes it learnable.

Distillation = identifying the **load-bearing claims**, the **mental models**, the **implicit prerequisites**, and the **traps** — and discarding the prose that surrounds them.

## How to ingest

Match the source to the right tool:

| Source | Tool / approach |
|---|---|
| URLs | `WebFetch` — fetch all of them in parallel before doing anything else |
| Local files (markdown, txt, code) | `Read` |
| PDFs | `Read` with the `pages` parameter for large ones |
| Library docs / current tech | `context7` MCP — your training data may be stale |
| Existing codebase | `Read` + `Glob` + `Grep` to understand structure first |
| YouTube / podcasts | Ask for transcript; can't watch video directly |
| Long pasted text | Just read it; don't ask the user to chunk it |

Fetch in parallel where possible. Don't make the user wait while you serially fetch 6 URLs.

## After ingestion: tell the user what you took in

A short reality check before you start teaching:

> *"OK — I read all four links and the PDF. About 14k words. The PDF is mostly background on X; the four links are split between mechanism (links 1–2) and applications (links 3–4). Anything missing?"*

This catches two failures fast: you misread the relevance of a piece, or the user forgot to include something. Either way, better to find out now than after you've built a plan around bad inputs.

## Distill the material

For each source (or for the corpus as a whole when sources are tightly related), pull out:

### 1. The load-bearing claims (3–10)

What does the author actually want the reader to take away? Not every sentence — the **central claims** that, if removed, would gut the piece.

Distinguish from:
- Background / setup material
- Examples (illustrative, not load-bearing)
- Hedging / caveats (real but lower-leverage)
- Storytelling / hooks

A good test: if the user only retained the load-bearing claims, would they have the value of the article? If yes, you've distilled correctly.

### 2. The implicit prerequisites

What does the source assume the reader already knows? Often this is the gap that makes a piece feel hard. List the prereqs explicitly:

> *"This article assumes you know what an event loop is, basic async/await syntax, and roughly what a Promise represents in JavaScript. Are you solid on those, or should we cover any first?"*

This is the difference between throwing the user into the deep end and meeting them where they are.

### 3. The mental model the source uses

Authors usually have a mental image of the topic, even if implicit. Surface it:

> *"This author is thinking about it as a producer-consumer queue with backpressure. That's the lens — keep that picture in mind as we go through it."*

Sometimes the source uses a *bad* mental model, or one that conflicts with another source. Flag that:

> *"Source A frames this as a 'tree of decisions'; source B treats it as 'a sequence of state transitions'. Both work, but they emphasize different things — we should pick one."*

### 4. Traps and footguns

What does the source warn about (or fail to warn about)? What will the user get wrong if they only read the article and don't go further?

This is some of the highest-density learning content. Even a long article often has 2–3 specific gotchas embedded — pull them out.

### 5. Open questions / "you should go look up"

What does the source mention but not explain? What would a curious reader want to know more about? Note these — they may become future learning sessions or quick side-quests.

## Distinguishing source quality

Not all sources are equal. Calibrate your trust based on type:

- **Official docs / specs** — high authority on syntax, behavior, and the canonical version. Often weak on motivation and practical wisdom.
- **Textbooks** — high authority on concepts and structure. Often outdated on tooling.
- **Peer-reviewed papers** — high authority for empirical claims, with the caveat that they describe one specific finding, not "the consensus".
- **Quality blog posts (well-known authors, technical, recent)** — variable; usually strong on practical wisdom, sometimes weak on rigor.
- **Random blog posts / forum answers** — useful for "someone hit this problem before" context. Don't treat as authoritative without checking.
- **Marketing materials / vendor whitepapers** — directionally useful, but every claim has an angle.

When teaching from a mix of sources, weight your distillation accordingly. If one source disagrees with three others, name the disagreement and explain why you're trusting whom.

## When sources conflict

If you find conflicting claims between sources, **don't quietly pick one**. Surface it:

> *"Heads up: link 2 says X, link 4 says Y — these are direct contradictions. From context, link 4 is from 2018, link 2 is from 2024 and references a newer version of the API. I'd trust link 2, but you should know there's drift."*

This builds the user's source-criticism skills *and* prevents them from confidently repeating outdated or wrong information.

## Grounding artifacts to source

Once you've distilled the source, every learning artifact you generate must be **traceable back** to at least one claim, section, or example in it. Scripts in `scripts/` will serialize whatever you hand them — including fabrications — so the discipline lives here, at the generation step.

Run this checklist before producing flashcards, quiz items, or cheatsheets:

1. **Every flashcard front** corresponds to a load-bearing claim, definition, or worked example you actually extracted from the source.
2. **Every flashcard back** is a paraphrase tight enough that someone holding the source could verify it in under 30 seconds. Fact cards should carry a source tag (`[from: link 2]`, `[from: PDF §3.2]`).
3. **Every quiz question** targets a trap, decision rule, or distinction the source emphasizes — not a generic *"what is X"* you could ask of any topic on the planet. Distractors are misreadings of the source, not invented alternatives.
4. **Every cheatsheet bullet** survives the question: *"Where in the source does this come from?"* If the answer is *"I just know this from training"*, cut it or flag it.
5. **Analogies, mnemonics, sequencing, and retrieval prompts are exempt** — those are your invention and that's the point. But the *thing* the analogy explains must be source-grounded. An analogy that explains a fabricated fact is double-poisoned.

When you catch yourself wanting to add a fact, example, or claim that isn't in the source, you have three options, in order of preference:

- **Cut it.** The source defines the scope. Honor it.
- **Surface it.** Tell the user: *"I almost added X — that's not in your sources. Want me to research it, or skip?"* Now they choose, with eyes open.
- **Mark it.** If you keep it, prefix with *"Beyond source:"* or *"My synthesis:"* so the user knows what they're about to memorize is your inference, not the source's claim.

Default to cutting. The user will not miss what they don't know was missing — but they *will* be hurt by memorizing a confident-sounding fabrication.

## Distillation as the input to other techniques

Once you've distilled, you can run any of the techniques in this skill on the distilled content:

- **Feynman** the load-bearing claims in plain language
- **First-principles** the mental model — why is this the right shape?
- **Active recall** with questions targeting each claim
- **Spaced repetition cards** for the high-density facts
- **Knowledge summary** that's faithful to the distillation, not a parrot of the source
- **Deliberate practice** drills derived from the source's worked examples

The distillation is the **substrate**. The techniques are how you make it stick.

## Common failure modes

- **Re-summarizing instead of distilling.** Producing a "shorter version" of the article. Useless. Distillation reorganizes around *what's learnable*, not *what's said*.
- **Dropping the prereqs.** Diving into teaching without checking whether the user has the assumed background. Half the time that's the actual problem.
- **Single-source bias.** Treating one article as gospel. Cross-check against other sources or your own knowledge when possible.
- **Listing claims without ranking.** All claims are not equal. Identify the load-bearing ones explicitly.
- **No structural read.** Just listing facts. The structure (mental model, hierarchy, decision tree) is *more important* than the individual facts for retention.
- **Filling gaps with training-data plausibility.** When the source is silent on a question, the temptation is to produce a confident-sounding answer from general knowledge. This is the single highest-risk hallucination mode in this skill, because the user encodes the answer into spaced repetition and rehearses it until it feels true. If the source doesn't say it, either flag the gap or research it explicitly — never silently fill it in.

## Example

User pastes a 3000-word article on PostgreSQL `EXPLAIN ANALYZE` output.

**Bad distillation (summarization mode):**
> "The article explains how to read EXPLAIN ANALYZE output, including operators, costs, and timing. It covers seq scans, index scans, joins, and sort operations. It includes examples and warns about misleading planner cost estimates."

**Good distillation:**
> *"OK, here's the structure. The author's mental model: an EXPLAIN plan is a tree, executed bottom-up, with each node consuming rows from its children. That's the lens.*
>
> *Load-bearing claims:*
> 1. *`actual time` is per-loop; if `loops > 1`, multiply by loops to get total wall-time at that node.*
> 2. *Cost estimates are unitless 'planner-bucks', meaningful only relative to other nodes in the same plan.*
> 3. *The biggest issue is usually `Rows estimated vs actual` — when these diverge by 10x, the planner is making decisions on bad info; ANALYZE the table.*
> 4. *`Buffers: shared hit/read` distinguishes cache hits from disk I/O — far more useful than time, which is noisy.*
>
> *Prereqs the article assumes: you know what a sequential scan vs index scan is, basic SQL.*
>
> *Traps:*
> - *Don't compare cost numbers across different queries — different plans have different baselines.*
> - *EXPLAIN without ANALYZE doesn't actually run the query — the costs are estimates only.*
> - *EXPLAIN ANALYZE on writes (INSERT/UPDATE/DELETE) actually executes them — wrap in BEGIN/ROLLBACK.*
>
> *That last one is the article's most-easily-missed point. Worth flagging as a flashcard.*"

Now you have something to teach with.
