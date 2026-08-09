# Contributing

Thanks for improving DeepSeekHelper.

## Getting started

```bash
git clone https://github.com/UrgencyWu/deepseekhelper.git
cd deepseekhelper
npm install
```

No build step is required — the MCP server runs directly with Node.js.

## Project layout

```text
.codex-plugin/plugin.json   — Codex plugin manifest
.mcp.json                    — MCP server launcher
scripts/server.mjs           — MCP server (all tool implementations)
skills/deepseekhelper/       — Codex skill definition
data/                        — Local usage logs and model cache (gitignored)
```

## Before submitting a PR

```bash
node --check scripts/server.mjs
```

If you have the Codex plugin creator validation script:

```bash
python3 /path/to/plugin-creator/scripts/validate_plugin.py .
```

## Conventions

- The server is a single-file stdio MCP server. Keep it that way unless there is a strong reason to split.
- Tool names use `deepseek_` or `deepseekhelper_` prefixes to avoid collisions.
- Usage tracking appends JSON lines to `data/usage.jsonl`. Do not store prompt or response content.
- Model selection logic lives in `resolveModel()` and `automaticModelFor()`. New tools should reuse these.
- Error messages must pass through `sanitizeErrorMessage()` before surfacing to the user.

## Pull requests

- Keep changes focused and minimal.
- Do not commit secrets, `.env`, `data/`, or `node_modules/`.
- Update `README.md` and `skills/deepseekhelper/SKILL.md` when behavior changes.
- Include validation output or explain why it cannot be run.

## Conduct

Participation is governed by `CODE_OF_CONDUCT.md`.
