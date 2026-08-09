# The Feynman Technique

Named for Richard Feynman, the Nobel-winning physicist who insisted that if you can't explain something to a beginner, you don't truly understand it. The technique is a loop: explain → invite the user to re-explain → find the gaps → re-explain better.

Use this when:
- The topic is jargon-heavy and the user is intimidated by it
- The user has heard the topic explained before but it didn't click
- The user is stuck recognizing terms but not generating ideas in their own language
- The user says things like "I sort of get it but..." or "I keep losing the thread"

## How to run it

### Step 1 — Explain in plain language

Pick a single, well-defined chunk. Not "explain machine learning" — *"explain what gradient descent is doing".* Then explain it as if to someone who's smart but new:

- Use everyday words. Replace jargon with plain English; if you have to use a technical term, define it the first time and then use it normally.
- Use one running example or analogy. Don't introduce three.
- Keep paragraphs short. ~3 sentences each.
- Avoid the trap of "let me first give some background" — start at the heart of the idea and back-fill only what's needed.

A good Feynman explanation feels almost too simple to people who already know the topic. That's the point.

### Step 2 — Hand it back to the user

The user must produce, not just acknowledge. Pick one of these:

- *"In your own words, what's actually happening here?"*
- *"How would you describe this to a friend who hasn't taken this class?"*
- *"If I gave you a [concrete instance], walk me through what would happen."*

Then **stop and wait for their answer**. Do not preempt by writing "you might say something like...". The user has to do the retrieval.

### Step 3 — Diagnose the gaps

When the user replies, read their answer for three things, in priority order:

1. **Outright errors.** They've said something factually wrong. Name it — gently — and correct.
2. **Hand-wavy bits.** They glossed over a step ("and then it kind of just figures it out"). Press in: *"What happens at that step exactly?"*
3. **Missing connections.** They got the parts but didn't link them. Ask: *"Why does X lead to Y here?"*

If they nailed it, say so explicitly and *advance to the next chunk*. Don't make them re-explain something they have. Move forward.

### Step 4 — Re-explain better

When you re-explain after a gap, target the gap directly. Don't restart from the top. If they fumbled the gradient direction, explain that one piece, then ask them to redo just that piece.

Loop until the user's explanation is clean. Then chunk forward.

## Common failure modes

- **Verbosity.** The technique fails when you produce a 1000-word "simple explanation". If your explanation is longer than what would fit on a napkin, it isn't Feynman. Cut it.
- **Premature jargon.** "It's just gradient descent on a loss landscape" is not a Feynman explanation; it's vocabulary. If a beginner can't picture it, it doesn't count.
- **Closed questions.** Asking *"does that make sense?"* gets a worthless yes. Always ask for production: an explanation, an example, a prediction.
- **Accepting parroted answers.** If the user repeats your phrasing back, that's recognition, not understanding. Press for a different example, a different framing, or a prediction about a new case.
- **Skipping the loop.** It's tempting to explain, accept "got it", and move on. The retrieval step is where learning actually happens.

## When the user resists

Some users resist being asked to explain — it feels like school, or like they're being tested. Reduce the friction:

- Frame it as collaboration, not interrogation: *"Let's see if I explained it well — try it on me."*
- Use lower-stakes prompts: *"Even just rough words is fine — what's the rough idea?"*
- If they really won't, ask them to predict instead: *"If I changed [X], what would happen?"* Prediction is also retrieval and feels less performative.

## Example

User wants to learn what an HTTP 401 vs 403 status code means.

**Bad (lecture mode):**
> 401 Unauthorized indicates that authentication is required and has failed or has not yet been provided. 403 Forbidden indicates the server understood the request but refuses to authorize it...

**Good (Feynman mode):**
> Easiest way to remember it: 401 means *"I don't know who you are"* — the server doesn't have a valid identity for you, log in. 403 means *"I know who you are and you can't have this"* — your identity is fine, but you don't have permission for this resource.
>
> Quick check — imagine you log into Gmail with the wrong password. Which one does the server send back? And what about if you log in correctly but try to read someone else's inbox?

[Wait for their answer. If they swap them, gently correct and re-pose the same shape of question with a different example.]
