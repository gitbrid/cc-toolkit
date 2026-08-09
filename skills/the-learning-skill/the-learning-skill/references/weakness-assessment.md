# Targeted Weakness Assessment

A weakness assessment is a structured diagnostic that reveals the user's actual gaps — not the gaps they think they have. People are systematically wrong about their own knowledge: they're confident on topics they've encountered often (familiarity ≠ understanding), and dismissive of topics they actually know well.

Use this when:
- The user is preparing for an evaluative event (exam, interview, certification)
- The user has been studying a topic for a while and wants to know "where am I really"
- The user has a vague sense of "I'm bad at X" but can't articulate what specifically
- A learning session is starting and you need to set the level

## How to run it

### 1. Set the contract

Tell the user what's coming and why. *"I'm going to ask you a series of questions across [topic] — some easy, some hard, adjusted as we go. The point is to find your weak spots, not to prove you're smart. Honest answers help, even if it's 'I don't know'."*

This matters. Users who feel tested perform worse and lie to themselves. Users who feel diagnosed are honest.

### 2. Sample broadly

A diagnostic that hits only one corner of the topic gives you a narrow signal. Spread questions across:

- **Foundations** (basic facts, vocabulary)
- **Mechanism** (how things work)
- **Application** (use the concept in a new case)
- **Edge cases** (where common rules break)
- **Trade-offs** (decisions between options)
- **Failures** (common mistakes, footguns)

A typical assessment is 8–12 questions covering most of these. Don't ask 12 application questions and call it a diagnostic.

### 3. Adapt difficulty as you go

Start at *medium* difficulty. Then:

- If they get a question right confidently → next one harder
- If they get it right with hesitation → same level
- If they get it wrong → easier, on a related concept (you want to find the *floor* of their knowledge in this area, not just confirm they're weak)

Track this mentally as a 2D grid: across topics, down by difficulty. By question 8 you'll have a rough heatmap.

### 4. Probe for false confidence

The most dangerous gaps are the ones the user doesn't know they have. Watch for:

- Strong confidence on a question, then a vague answer ("yeah definitely, it's like... when you... use the thing")
- Pattern-matched answers ("oh that's just like X" — but they didn't show why)
- Skipping over a key qualifier in your question ("you said 'except when N is large' — what changes there?")

When you spot one, dig in: *"Walk me through that more carefully."* Often the confidence collapses.

### 5. Record the heatmap

You're not just asking questions; you're building a diagnosis. Internally (or out loud, depending on the user's preference), categorize each topic-skill cell as:

- **Solid**: confident, correct, can extend
- **Functional**: correct on common cases, shaky on edges
- **Fragile**: gets it sometimes, can't justify it
- **Missing**: doesn't know

The action plan flows from this heatmap.

### 6. Deliver the diagnosis honestly

When the assessment is done, tell the user what you found. Be direct but specific:

> *"You're solid on the basics of how SQL joins work — every kind of join you described correctly. Where you're shakier is on optimization: you know indexes exist but couldn't explain when a query ignores one. You also confused B-tree with hash indexes when I asked about range queries. Here's what I'd focus on..."*

Not:

> *"You did pretty well overall, with some areas to work on."* (Useless — could describe anyone.)

End with **2–3 specific recommendations**, each tied to a gap you found. Not 10. Two or three.

## Designing the question bank

For a structured diagnostic, generate the question bank ahead of asking. Some heuristics:

- **2–3 foundation questions** to confirm the floor
- **2–3 mechanism questions** that require explanation, not recognition
- **2 application questions** with novel scenarios
- **1–2 edge cases / traps** you suspect they'll miss
- **1 trade-off question** ("when would you pick X over Y?")

For an exam-prep context, weight toward the kinds of questions the actual assessment uses. For a practitioner-skill context, weight toward application and trade-offs.

## Common failure modes

- **Too easy.** A diagnostic where everything is gettable produces no signal. Push to the edge.
- **Too hard, too fast.** A wall of expert questions makes the user shut down and quit. Calibrate.
- **One-domain blindness.** Only asking about syntax when the topic also requires reasoning about behavior. Spread.
- **Acceptance of vague answers.** "Yeah it does that thing where the data..." doesn't count as correct. Push for specifics or mark fragile.
- **Soft diagnosis.** Hedging on the actual gaps in the summary. The user came to you to know — tell them.
- **No follow-up plan.** A diagnosis without next-steps is a list of things to feel bad about. Always tie weaknesses to actions.

## Example: diagnostic for a junior dev preparing for a systems interview

Topic: distributed systems, focus on consistency models.

**Q1 (foundation):** *In one sentence, what's the difference between consistency and availability in CAP theorem terms?*

User: "Consistency means all nodes see the same data, availability means every request gets a response."

→ Solid on foundation. Push harder.

**Q2 (mechanism):** *Walk me through what eventual consistency actually does — say I write to node A, then read from node B 50ms later.*

User: "Yeah, the read might not have your write yet, it'll get it eventually."

→ Functional but shallow. Probe.

**Q2.5:** *What mechanism makes the eventual part actually happen? What's the algorithm or process that gets the write from A to B?*

User: "Uh, gossip? Replication?"

→ Fragile. They've memorized the term but not the underlying mechanism.

**Q3 (application):** *Suppose you're building a counter that goes up — like total page views. Two nodes. Node A says 100, node B says 102. They reconcile. What do you want the answer to be? What's that called?*

User: "Hmm, you want 102? Or maybe sum, so 202?"

→ Missing. They don't know about CRDTs or convergent counters. Crucial gap for a systems interview.

[continue...]

**Diagnosis:**
> *"Solid on the high-level CAP framing, but your mechanism-level understanding is thin: you couldn't say what makes 'eventual' actually happen, and you'd never heard of CRDTs. For interview prep, I'd prioritize: (1) gossip/anti-entropy protocols — read up on Cassandra's repair docs; (2) CRDTs — Marc Shapiro's intro paper or the Riak DB docs are great; (3) read-your-writes vs. monotonic-reads — the difference between session and full eventual consistency. We can do active recall on these next session."*

That's a diagnostic that produces a plan.
