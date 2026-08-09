# First-Principles Reasoning

Most explanations are built on a tower of assumed concepts. First-principles teaching kicks the tower out, hands the user the foundation stones, and lets them rebuild the tower themselves. Use this when memorizing surface facts isn't enough and the user needs to *reason about novel situations*.

Use this when:
- The user will face problems that don't match what they've seen before
- They've memorized a procedure but can't explain why it works
- The standard textbook treatment hides the "why" behind layers of formalism
- The user is asking questions like "but why does X work that way?"
- You're modernizing legacy understanding ("we've always done it this way" → "but should we?")

## How to run it

### Step 1 — Find the irreducible building blocks

For the topic at hand, ask: *what are the things that can't be questioned without leaving the domain entirely?*

For example:
- Physics: conservation of energy, conservation of momentum, the speed of light, Coulomb's law for charges, etc.
- Software: the machine executes a stream of instructions; memory is finite; computation takes time; networks fail.
- Economics: people respond to incentives; resources are scarce; trades happen when both sides see gain.

These aren't always the textbook-listed "fundamentals" — they're the things that, if you removed them, the rest of the field would collapse.

The skill of doing this well is identifying which assumed truths are actually *consequences* of more fundamental things. "A linked list lets you insert in O(1)" is a consequence; "memory access takes time and pointers refer to addresses" is closer to a primitive.

### Step 2 — Question received wisdom

For each "rule" the user has been taught about the topic, ask:

- *Is this actually true, or is it true under some conditions that we should make explicit?*
- *Is this a fundamental fact, or a consequence of something deeper?*
- *Could the opposite be true in a different context?*

Make the user uncomfortable with their own knowledge — temporarily. The discomfort is what creates the *opportunity* to rebuild.

Example: the user "knows" that databases are slow and you should cache aggressively. First-principles probe: *why are databases slow? What makes them slow? Are all queries slow, or specific kinds? When is caching strictly worse than just hitting the database?*

### Step 3 — Rebuild the idea from the bottom

Now construct the topic, step by step, from the building blocks. Each step should feel inevitable: *given X, Y must follow because...* The goal is for the user to feel: "oh, I could have figured this out myself."

A good first-principles rebuild:
- Has 3–6 steps from primitives to the final concept
- At each step, makes the *reason* for the move explicit
- Stops to check: "could it have gone a different way? Why didn't it?"

### Step 4 — Stress-test with a novel case

This is the payoff. Ask the user to apply the rebuilt understanding to a case they've never seen:

- *"Given what we just derived, what would happen if [novel situation]?"*
- *"Could you design a system where the opposite is true? What would have to change?"*
- *"What's the simplest counterexample to [common belief in this field]?"*

If the user can reason through the novel case, they have first-principles understanding. If they can only recite the rebuild, they've memorized your explanation — go back and re-derive a step.

## Common failure modes

- **Pseudo-primitives.** Using "fundamental" things that are actually mid-level abstractions. "OOP encapsulation" is not a primitive. If you find yourself using a domain term, ask whether it can be reduced further.
- **Reverse-engineering instead of deriving.** It's easy to "rebuild" a concept by working backward from the answer. If the user couldn't have derived the next step on their own with a small hint, you skipped a level.
- **Too many primitives.** If you list 15 building blocks, you've kicked the tower over only to put it right back. Aim for the smallest set that lets you rebuild.
- **Forgetting to stress-test.** Without a novel application, you don't know if the user actually built understanding or just followed your story.

## When this is the wrong technique

First-principles is heavy. Don't use it for:
- Pure vocabulary or fact-based memorization (use spaced repetition)
- Procedural skills where the "why" doesn't help in the moment (sometimes you just need to drill the procedure)
- Topics where the user needs working knowledge fast and depth is overkill

## Example

Topic: *Why does virtual memory exist?*

**Surface answer (not first-principles):**
> Virtual memory lets each process think it has its own contiguous address space, isolated from other processes.

**First-principles rebuild:**
> Start with the primitives:
> 1. Physical RAM is a finite resource.
> 2. Multiple programs need to run "simultaneously" on one machine.
> 3. Programs are written assuming they have predictable memory addresses.
> 4. Programs shouldn't be able to read or corrupt each other's memory.
>
> Given (2) and (3), if every program just used physical addresses, two programs would collide. So we need a layer of indirection: each program sees a "fake" address that gets translated to a real one. That's the virtual address.
>
> Given (4), the OS has to control the translation, so user programs can't access translations they shouldn't. That's the page table living in kernel-protected memory.
>
> Given (1), if the working set across all programs exceeds RAM, the OS has to spill some pages to disk and load them on demand. That's swapping/paging.
>
> Notice that virtual memory wasn't designed; it was *forced* by the constraints. Could there be a system without it? Yes — single-program embedded systems often have none. The need only appears when (2) becomes a goal.
>
> **Stress test:** A new system has infinite RAM and runs only one program at a time. Do you still need virtual memory? Why or why not?

The stress test reveals whether the user understands that virtual memory is a *response to constraints*, not a thing-in-itself.
