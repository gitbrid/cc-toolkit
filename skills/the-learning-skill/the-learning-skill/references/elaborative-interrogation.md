# Elaborative Interrogation

Elaborative interrogation is the technique of repeatedly asking *"why?"* until you've replaced rote facts with a web of causal relationships. It's the difference between knowing *that* the sky is blue and knowing *why* — and why that's not the whole story (the sky is also red sometimes — why?).

Use this when:
- The user has a fact-shaped knowledge of a topic but can't reason past it
- You want them to integrate new information with what they already know
- The topic has visible "why" structure (causes, mechanisms, motivations) — not pure conventions

This pairs naturally with first-principles teaching. First-principles asks *"what's the bottom?"*; elaborative interrogation asks *"why does each piece sit where it does?"*

## How to run it

### 1. Make a claim

State a fact, principle, or pattern. It can be a textbook fact, something the user just said, or something you're explaining for the first time.

> *"In SQL, an index on a column generally speeds up `WHERE column = X` queries."*

### 2. Ask why

Press for the mechanism behind the claim:

- *"Why is that?"*
- *"What makes that work?"*
- *"What would have to be true for that to fail?"*

The user should give you not a restatement, but an explanation that *connects to other things they know*.

### 3. Ask why again

Once they answer, press deeper. The first "why" usually gets a surface answer. The second usually gets the actual mechanism.

> User: "Because the index lets you find the row faster."
> You: *"OK, but why is finding it faster? What's the comparison — what was the alternative way of finding the row, and what makes the index version different?"*
> User: "Without the index you scan every row, with the index you... like, look it up in a tree."
> You: *"And why is the tree faster than scanning every row?"*
> User: "Because you can binary-search it... wait, you compare against the middle, then half, then half... so it's logarithmic."
> You: *"Right — and why does that matter for *big* tables specifically?"*

By the third "why", you usually arrive at the *interesting* layer — the layer where the user genuinely connects new information to existing knowledge.

### 4. Stop when the user has reached a primitive

You're done when the user reaches an irreducible fact ("computers compare bits one operation at a time") or a primitive of the field. Don't keep asking why past that point — it becomes philosophy, not learning.

## Pacing

Don't run elaborative interrogation as a 20-question gauntlet. Use it sparingly, on **the highest-leverage facts** in a session. Three or four "why chains" in a 30-minute session is often enough to anchor everything else.

## Specific elaborative prompts

When "why?" feels repetitive, vary the form:

- *"What does that depend on?"*
- *"What problem is this solving — what was the alternative?"*
- *"What would break if this weren't true?"*
- *"How does this connect to [thing they already know]?"*
- *"In what conditions would the opposite be true?"*
- *"What's the cost of doing this — what trade-off was made?"*
- *"Who decided this was the right approach? What were they optimizing for?"*

## When this is the wrong technique

- **Pure conventions**: don't elaborate on why. *"Why is the syntax `let x = 5;` and not `5 = x;`?"* — because someone designed the language that way. Elaborative interrogation on conventions just produces "because that's how it is".
- **Topics where the user's level is below the question**: if the user is at level 1 and your why-question requires level-3 knowledge to answer, you'll just frustrate them. Drop down to first-principles teaching instead.

## Common failure modes

- **Asking why on something arbitrary.** Wastes the user's time and erodes confidence in the process.
- **Asking why too many times in a row.** "Why? Why? But why?" turns into an annoying child-mode. Mix in alternative forms.
- **Letting the user off easy.** They give a confident-sounding answer that's actually shallow. Push: *"You said 'because it's faster' — faster compared to what, and at what cost?"*
- **Forgetting to confirm.** When the chain reaches bedrock, summarize it back: *"OK so the chain is: X happens because Y, which is because Z, which is just how the hardware works."* This locks in the understanding.

## Why this technique works

The cognitive-science name for what's happening: when you encode a fact into your existing network of knowledge — when it's connected to other things via causal "why" links — you have many more retrieval paths to it. A fact with no connections is brittle (one weak retrieval path); a fact embedded in causal structure is robust (many paths to find it).

This is also why textbooks that explain *why* tend to be remembered better than textbooks that just present *what*. Use elaborative interrogation to recreate that effect on the fly.

## Example

Topic: garbage collection in Java.

> User: "Yeah, the garbage collector frees memory I'm not using."
> You: *"Why does Java need a garbage collector when C doesn't?"*
> User: "Because Java doesn't make you free memory yourself."
> You: *"Right — but why was that decision made? What problem in C was Java trying to avoid?"*
> User: "Memory leaks? Like when you forget to free something?"
> You: *"Yes — and what's the cost of that decision? What did Java give up to get safer memory?"*
> User: "...performance? Because the GC has to scan everything?"
> You: *"And what does it scan, exactly? Why is the question 'is this object still reachable' the right question?"*
> User: "Because if you can still get to it, you might use it. So... it walks references from somewhere... from the stack? From globals?"
> You: *"Yes — those are the GC roots. So now you can describe the whole arc: Java traded performance for safety, and the way it implements safety is reachability analysis from a known set of roots."*

Notice how a 3-minute exchange of why-questions has just walked the user from "GC frees memory" to a working mental model of the actual algorithm. That's the leverage of this technique.
