# Active Recall

Active recall is the single best-evidenced technique in the cognitive-science of learning. The act of *retrieving* a piece of information — not re-reading it — is what strengthens the memory. Reading creates the illusion of competence; recalling builds the actual skill.

The mantra: **if the information isn't being retrieved, it isn't being learned.**

Use this technique constantly, not occasionally. It threads through every other technique in this skill.

## Forms of active recall

Different forms suit different content:

| Type | Best for | Example |
|---|---|---|
| Free recall | Bigger concepts, frameworks | "Without notes, list the steps of the Krebs cycle." |
| Cued recall | Vocabulary, paired facts | "What's the symbol for sodium?" |
| Recognition (weakest) | Last resort | Multiple choice |
| Application | Skills, procedural knowledge | "Given this code, what would the output be?" |
| Generation | Deep understanding | "Make up a problem this technique would solve." |
| Teach-back | Mastery check | "Explain this to me as if I were new." |

Lean into **free recall, application, and generation**. They are harder for the user, which is exactly why they work better.

## How to run a recall session

### 1. Set the format

Tell the user what you're about to do. *"I'm going to ask you 6 questions on what we just covered. Some easy, some not. Don't look back at our conversation. Take your time."*

This matters: when users know they'll be tested, even *before* the test, they encode information differently.

### 2. Mix difficulty

Don't ask 6 easy questions in a row, or 6 hard ones. Interleave:

- 1 easy (warm-up, builds confidence)
- 2 medium (the bread and butter)
- 1 hard (forces deeper retrieval)
- 1 application (use the concept on a new case)
- 1 generation (have them produce something)

This pattern keeps engagement up and reveals ceilings without crushing them.

### 3. Wait. Really.

The most common LLM failure with active recall is asking a question and immediately answering it in the same turn. **Don't.** Send the question. Stop. Wait for the user.

### 4. Give feedback that teaches

When the user answers:

- **If correct**: name what they got right specifically. Not "yes!" but *"yes — and the key thing you nailed there is recognizing that the constraint comes from X, not Y."* This reinforces the *reason* the answer was right.
- **If partly correct**: confirm the right part, isolate the wrong part, explain it, re-ask in a slightly different shape.
- **If wrong**: don't soften it ("kind of, but..."). Be clear it was wrong. Then explain the right answer carefully and re-ask later.
- **If "I don't know"**: don't dump the answer. Give a hint first. Get them to retrieve.

### 5. Re-test what they got wrong

Anything they missed should come back later in the same session, in a slightly different form. This is **retrieval practice** — failed retrievals followed by correct retrievals are extraordinarily effective for memory.

If they missed Q3, ask Q3.5 — same concept, different framing — at Q7 or Q8. Then again next session.

## Designing good recall questions

A good question:

- Is **specific enough to have a clear answer** (not "tell me about Postgres")
- Is **deep enough that recognition won't suffice** (not "is Postgres a database? yes/no")
- **Reuses past content** (questions should connect things across the session, not silo them)
- **Includes a stretch question** (something just past current ability — the "desirable difficulty")

Avoid:

- Trivia that doesn't matter (don't ask the year something was invented unless that's the point)
- Closed yes/no questions (almost always too easy)
- Questions where the answer is in your previous message (they'll just scroll up)

## Generating questions from material

When you have source material (a chapter, a doc, a paper), pull active-recall questions out of it systematically:

1. Identify the **3–7 key claims** of the material.
2. For each, write:
   - One free-recall question ("explain X")
   - One cued-recall question ("what's the value of Y in this context?")
   - One application question ("given new scenario Z, how would X apply?")
3. From the cluster, pick a balanced mix for the session — usually 6–10 questions covers a typical 30-minute session.

These questions are also the basis for flashcards (see `spaced-repetition.md`).

## Common failure modes

- **Self-answering the question.** *"What's a closure? It's a function that captures..."* — this isn't a question, it's a sentence. Send the question, then nothing. Wait.
- **Soft-pedaling errors.** "Almost! Well, kind of..." trains the user to lower their bar. Be clear when something is wrong; warm in tone, sharp on accuracy.
- **Cramming the session.** 30 questions in one go. The user fatigues, late questions get worse answers, and the late material doesn't get retained. Cap sessions at 10 questions or 15 minutes, whichever comes first.
- **Skipping the second pass.** Asking once isn't enough for missed items. They need at least one more retrieval that day.
- **Closed multiple choice when free recall is possible.** MCQ tests recognition, which is the weakest form. Only use it when you must (e.g., the user genuinely can't produce free-recall answers yet) or when the assessment they're prepping for is multiple-choice.

## Example

You've just walked the user through the basics of how DNS works. Time to recall.

**Bad (LLM auto-answers):**
> Q: What does DNS stand for? Answer: Domain Name System. It translates...

**Good (you stop):**
> OK, quick check — without scrolling up:
>
> 1. Walk me through what happens, in order, when I type `example.com` into a browser and hit enter — focus just on the DNS part.
> 2. What's the role of a recursive resolver versus an authoritative server?
> 3. Why do TTLs exist? What goes wrong without them?
>
> Take your time.

Then *wait*. When they answer, evaluate, then queue the next one. After all six, come back to anything they fumbled with a different framing.
