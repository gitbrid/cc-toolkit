# Interleaving and Variation

The intuitive way to study is to do all the problems on topic A, then all the problems on topic B, then all the problems on topic C. **Block practice.** It feels efficient. It produces fast in-session improvement.

It also produces poor long-term retention and worse transfer to novel problems.

The counter-intuitive better approach is to **interleave** — mix problems from A, B, and C in a single session. Each problem requires the user to first *figure out which technique applies*, which is the part that gets used in real life. Block practice removes that step entirely.

Use this when:
- The user is learning a set of related techniques/concepts that they'll need to *choose between* in real situations
- The user is preparing for an exam or interview where they don't know which kind of problem is coming
- The user has been practicing only block-style and is plateauing

## How to use interleaving

### 1. Identify the choice points

What categories of problem/situation does the user need to recognize? For each, what's the trigger that identifies it?

> Example, for SQL query optimization:
> - "Slow because of full table scan" → add index
> - "Slow because of bad join order" → fix stats / rewrite predicates
> - "Slow because of N+1" → batch queries / eager loading
> - "Slow because the data really is large" → physical layout / partitioning

The categories don't have to be mutually exclusive — many real problems have multiple causes. But the user has to be able to *recognize each pattern when they see it*.

### 2. Build the mixed problem set

Take problems from each category and interleave them. Don't sort, don't group, don't label by category. Random or quasi-random order.

For a learning session: 6–10 problems mixed together, with the user expected to *first identify the type* before solving.

### 3. Slow down on the recognition step

The crucial pedagogical move with interleaving is forcing the user to articulate their classification:

> *"Before you solve this, tell me — which kind of problem is this, and how did you decide?"*

If they get the type right but the solution wrong: they have classification but not technique — drill the technique.

If they get the type wrong: they have technique but not recognition — keep interleaving more, drill the cues that distinguish types.

### 4. Re-mix on subsequent sessions

The exact same set of problems on day 2 isn't real interleaving. Bring in new problems, in new orders, with new variations. The user should never know what's coming.

## Variation

Closely related to interleaving: vary the surface details of problems while keeping the underlying structure constant. This forces the user to extract the *structure* and not memorize the surface.

> Example, for the algorithm "two-pointer technique":
> - Problem 1: Find pair summing to X in sorted array.
> - Problem 2: Find longest substring with at most K distinct characters.
> - Problem 3: Reverse a string in-place.
> - Problem 4: Remove duplicates from sorted array in-place.
>
> All "two-pointer", but the surface is wildly different. A user who solves all four has internalized the *structure*, not the *example*.

When the user solves a problem, ask: *"What other problem we've done is this the same as, structurally? Where else would this approach show up?"*

## When this is the wrong technique

- **Very early in learning a topic.** Block practice is better when the user is just getting the basic technique into their head. Interleave *after* they can do each technique in isolation.
- **When techniques aren't really distinct.** If the "categories" you're choosing between are actually the same thing in different clothing, interleaving doesn't add value.

## Common failure modes

- **Pseudo-interleaving.** Alternating ABABAB still has a predictable pattern — the user catches on. Use random orders.
- **Skipping the classification step.** If you let the user dive straight into solving, you've removed the very part interleaving was supposed to train.
- **Not enough variation in surface.** Using 4 problems that are all "find the duplicate" with different array sizes is variation in number, not in structure. Vary the *story*, not the parameters.
- **Mixing too widely.** Interleaving SQL questions with poetry analysis isn't useful. Mix within a coherent domain where the choice points are real.

## Why this technique works

When you study one type of problem in a block, your brain doesn't have to retrieve the technique — it's already loaded. You're rehearsing application, but not retrieval.

When you interleave, every problem requires:
1. Reading the problem
2. Retrieving the technique that fits ← this is the missing part of block practice
3. Applying the technique

Step 2 is what gets used in the wild — when someone hands you a problem, they don't tell you the technique. Block practice produces students who can't recognize problems they've solved a hundred times.

## Example

A user is preparing for a coding interview, has been blasting through "trees" problems all week, feels strong on trees.

**Bad practice round** (block):
> 5 tree-traversal problems in a row. User solves all 5 in 30 minutes. Feels great.

**Better practice round** (interleaved):
> 5 problems, mixed:
> 1. Sorted-array search → expects binary search (not tree)
> 2. Tree path sum → expects DFS
> 3. Subarray with target sum → expects two-pointer or hashmap
> 4. Validate BST → expects in-order traversal with bounds
> 5. Find duplicate in array → expects hashmap or Floyd's
>
> Before each: *"Talk me through which technique you'd use and why."*

In the interleaved set, the user has to spend the first 30 seconds on classification — exactly what they'll do in a real interview. In the block set, they didn't have to think about it at all.

After the session: which problems did they misclassify? Those are the cues to drill more.
