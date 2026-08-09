# the-learning-skill

A portable [Agent Skill](https://www.anthropic.com/news/skills) that turns Claude (or any compatible agent) into a study coach. Instead of dumping a wall of text in response to "teach me X", it runs a real learning session: framing the goal, ingesting source material, diagnosing gaps, picking proven techniques (Feynman, first-principles, active recall, spaced repetition, deliberate practice), running the first session live, and leaving behind durable artifacts you can use offline.

## What you get

For every run, the skill creates an isolated working directory under `stuff_to_learn/<topic-slug>-<timestamp>/` containing some combination of:

- `notes.md` — markdown study notes / cheat sheet
- `flashcards.html` — self-contained, click-to-open flashcard app
- `quiz.html` — self-contained quiz app with scoring
- `anki.tsv` — Anki-importable deck for spaced repetition
- `schedule.md` / `schedule.ics` — spaced-review calendar
- `cheatsheet.pdf` — printable, fold-up review card

`stuff_to_learn/` is gitignored — these are personal artifacts, not project source.

## Where it works

This is a standard Agent Skill, packaged as a single self-contained directory (`the-learning-skill/`) with a `SKILL.md` manifest, supporting reference docs, and helper scripts. It works in **any environment that supports skills**, including:

- **Claude Code** (CLI) — drop the directory into `~/.claude/skills/` or your project's `.claude/skills/`
- **Claude.ai** — upload the skill via the skills interface
- **Claude API / Agent SDK** — load it as a skill on any agent you build
- **Copilot CLI**, **Gemini CLI**, **Codex**, and other skill-aware agent runtimes — the same directory ingests directly

The skill follows the [Agent Skills spec](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills): a frontmatter-tagged `SKILL.md` (name + ≤1024-char description), progressively-disclosed reference files in `references/`, and executable helpers in `scripts/`. No platform-specific assumptions.

## Install

### Claude Code

```bash
# user-level (available in all projects)
cp -r the-learning-skill ~/.claude/skills/

# or project-level
mkdir -p .claude/skills && cp -r the-learning-skill .claude/skills/
```

### Other runtimes

Point your runtime at the `the-learning-skill/` directory however it ingests skills (upload, plugin install, config path, etc.). The directory is self-contained.

## Usage

Just ask. The skill triggers on a wide range of phrasing:

- "teach me X"
- "help me learn X"
- "I have an exam on X next week"
- "quiz me on X"
- "make flashcards for X"
- "I keep forgetting X"
- "study guide for X"
- "I have these articles, can you teach me?" + links/PDFs/pasted text

It also triggers when you hand over source material without an explicit ask — it'll check whether you want to learn it before summarizing.

## Layout

```
the-learning-skill/
    SKILL.md                  # manifest + master flow
    references/               # progressively-disclosed technique docs
        feynman-technique.md
        first-principles.md
        active-recall.md
        spaced-repetition.md
        deliberate-practice.md
        ...
    scripts/                  # generators for artifacts
        generate_anki_deck.py
        generate_flashcards_html.py
        generate_quiz_html.py
        generate_schedule.py
        generate_cheatsheet_pdf.py
    assets/
    evals/
```

## License

See [LICENSE](LICENSE).
