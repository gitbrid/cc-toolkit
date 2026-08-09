# Deliberate Practice

Most "practice" isn't. Repeating things you already do well is rehearsal, not practice. **Deliberate practice** is the targeted work of attempting things just past your current ability, with feedback, on weaknesses you've identified — not just the parts you enjoy.

Use this for *skills*, not just facts. Anywhere the user has to *do* something well — write code, write prose, give a talk, sight-read music, solve problems on a whiteboard, debug, design — deliberate practice is the engine of getting better.

## The four conditions

Deliberate practice requires all four. Skip any one and it becomes ordinary practice (which improves you slowly) or recreational engagement (which doesn't improve you at all).

1. **A specific weakness as the target.** Not "practice piano" — *"work on legato passage transitions in measures 12–18."* Not "practice coding" — *"work on writing recursive solutions without first writing the iterative version."*
2. **Just past the edge of current ability.** Easy enough that effort produces correct output sometimes, hard enough that you fail often.
3. **Feedback within seconds-to-minutes.** Without feedback you reinforce errors. The faster the feedback, the faster the learning.
4. **Repetition with intentional variation.** The same drill 100 times in a row is rehearsal. The same skill drilled across varied contexts builds transfer.

## How to design a deliberate-practice session

### Step 1 — Identify a specific skill weakness

Use the diagnostic from `references/weakness-assessment.md`, or if the user already knows: *"What's the thing you keep getting stuck on?"*

Push for **specificity**. Not "I'm bad at SQL" — *"I'm bad at writing window functions; I always have to look up the syntax for partition vs. order"*.

If the user can't articulate a specific weakness, run a 5-minute live exercise where they attempt a skill task — you'll see the weakness in the doing.

### Step 2 — Design a drill

A drill is a small, repeatable exercise that targets *just* the weakness. Not a project, not a full problem — a sliver.

Examples:
- **Window function syntax** → drill of: 10 small queries, each requiring one window function with subtle differences (running total, rank, lag, etc.). Solve each in <2 minutes, check your answer, move on.
- **Recursive thinking** → drill of: 8 problems where you write the recursive solution *first*, no iterative draft. Each ~15 lines, ~5 min each.
- **Sight-reading rhythms** → drill of: 30 four-bar rhythms increasing in syncopation, played with a metronome.
- **Prose conciseness** → drill of: take 10 wordy sentences from your own writing, cut each by 30% without losing meaning.

The signature of a good drill: *if you did this for 20 minutes a day for two weeks, you would visibly improve at the specific skill*.

### Step 3 — Calibrate difficulty live

After the first 2–3 reps, ask:

- *"How hard did that feel? 1–10."*
- If 3 or below: too easy, raise difficulty.
- If 4–7: good zone, continue.
- If 8 or above: too hard, drop down a level.

You're aiming for what learning science calls **desirable difficulty** — failing maybe 20–30% of the time. Constant success means too easy; constant failure means too hard.

### Step 4 — Provide feedback per rep

After each attempt:
- Did it succeed? (Yes/no, immediately.)
- If no, where did it go wrong? (Specifically, not "it didn't work".)
- What was the right answer / approach? (Just enough — don't lecture.)
- How does the next rep change because of this?

Feedback should be **actionable for the next rep**. "You used the wrong window function — for running totals you want SUM() OVER (...ORDER BY...)" is actionable. "Try harder" isn't.

### Step 5 — End before fatigue

Deliberate practice is intense. 20–30 minutes is often the right session length. After that, attention drops, errors compound, and the user starts reinforcing wrong patterns.

End on a successful rep when possible. The last attempt is what they remember.

## Coupling deliberate practice with other techniques

- **After deliberate practice → spaced repetition.** Drill skills today, schedule a refresher tomorrow, three days from now, etc.
- **Before deliberate practice → first-principles or Feynman.** If the user doesn't understand the *why*, drilling the *how* will produce brittle skill that breaks under variation.
- **Within deliberate practice → interleaving.** Mix problem types within the drill to force recognition.

## Common failure modes

- **Drilling strengths.** Practicing what you're already good at is comfortable but useless. Always pick the weakness.
- **Practice-as-performance.** Doing your existing best work over and over isn't deliberate practice — it's *performance*. Practice should produce many failures.
- **No feedback loop.** Solving 50 problems and then checking all answers at the end means the user repeated their misconceptions 50 times. Check after each rep, ideally.
- **Marathon sessions.** Two hours of intense drilling produces 30 minutes of practice and 90 minutes of degraded performance. Time-box.
- **Confusing volume with practice.** "I did 200 leetcode problems this month" is a metric, not a result. Did the *quality* improve? Did *new* kinds of problems become solvable?
- **No variation.** The exact same drill for two weeks. Vary the surface or the ordering.

## Distinct from "putting in the hours"

A common misconception: deliberate practice is about *amount* of work. It isn't. A deliberate-practice session can be 20 minutes. The defining feature is *quality of attention to weakness* — not duration.

Many people who put in massive hours don't improve, because their hours are spent on what they already know. The 20-minute deliberately-targeted session beats the 3-hour drift session.

## Example

User is a junior dev preparing for system-design interviews. They report: *"I always freeze at the part where the interviewer asks about scaling — I just start listing things instead of reasoning."*

That's the weakness. Specific. Actionable.

**Drill design:**
- 5 system-design starter prompts (URL shortener, chat app, image upload, ride matching, paste service).
- For each, the user has 5 minutes to produce a single answer to: *"Now, scale this from 1k users to 10M users. Walk me through what changes and why."*
- Constraint: they must reason in cause-and-effect order, not list features.
- Format constraint: each answer must include three "what breaks" and three "what we add" points.

**Feedback per rep:**
- After each, you say: *"Where in your answer did you stop reasoning and start listing? What was the trigger?"* If they listed without reasoning, name the moment. The user starts noticing the pattern.

**Variation:**
- After 3 reps with that constraint, swap to: *"Same 5 prompts, but this time scale from 10M to 100M and there's a 10x cost reduction requirement."* Different forcing function, same skill (causal reasoning under scale).

In two 20-minute sessions, this user has worked the exact failure mode they'll face. That's deliberate practice.
