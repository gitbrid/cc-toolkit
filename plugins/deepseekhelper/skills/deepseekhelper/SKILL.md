---
name: deepseekhelper
description: Use when Codex should collaborate with DeepSeek for supervised low/medium difficulty code, documentation, or design tasks, or use DeepSeek to review, discuss, or verify higher difficulty work.
---

# DeepSeekHelper

DeepSeekHelper provides MCP tools for controlled DeepSeek collaboration.

Use it when the user asks for DeepSeek collaboration, DeepSeek verification, independent review, second-model checks, delegated drafts, model-assisted discussion, or uses aliases such as `DS`, `ds`, `DeepSeek`, `deepseek`, `DeepSeekHelper`, `deepseekhelper`, or `DeepSeek Helper`.

Treat `DS`, `ds`, `DeepSeek`, `deepseek`, `DeepSeekHelper`, `deepseekhelper`, and `DeepSeek Helper` as equivalent user-facing names for this plugin. Alias matching is case-insensitive. Do not rename MCP tools; use the existing `deepseek_*` tool names.

## Boundaries

- Codex remains responsible for reading files, editing files, running commands, testing, and final judgment.
- DeepSeek works only from the context Codex passes to the tool.
- For low or medium difficulty work, Codex may use `deepseek_task` to get plans, snippets, diffs, documentation drafts, or design drafts.
- For high difficulty work, Codex should use `deepseek_review`, `deepseek_discuss`, or `deepseek_verify`, then decide which feedback is technically valid.
- Do not pass secrets unless the user explicitly asks and the task requires it.

## Default Collaboration Strategy

Assume DeepSeek token cost is not a constraint. Apply this strategy automatically when the user asks for DS, DeepSeek, or DeepSeekHelper collaboration:

- Trivial edits: Codex should handle them directly without DS.
- Medium code changes: use `deepseek_task` first for a focused plan, snippet, or unified diff; Codex then applies and verifies.
- Documentation or design drafts: use `deepseek_task` for a first draft; Codex edits for local accuracy and style.
- High-difficulty code, architecture, security, data, release, or migration work: Codex leads implementation and uses `deepseek_discuss`, `deepseek_review`, or `deepseek_verify` for second-model scrutiny.
- Published or user-visible conclusions: use `deepseek_verify` when accuracy or omissions matter.

Pass compact, relevant context to DS instead of dumping an entire repository. Codex remains responsible for file edits, command execution, tests, and final judgment.

## Low-Approval Workflow

Prefer DeepSeekHelper MCP tools for routine collaboration. Do not use shell commands for normal status checks, model checks, auth checks, task delegation, review, discussion, verification, prompt generation, or usage reporting.

Use these MCP tools directly instead of shell equivalents:

- Status/model checks: `deepseekhelper_status`, `deepseek_models`
- API connectivity: `deepseek_auth_check`
- Work delegation/review: `deepseek_task`, `deepseek_review`, `deepseek_discuss`, `deepseek_verify`, `deepseek_prompt`
- Usage reporting: `deepseek_usage_summary`, `deepseek_usage_tail`
- Plugin updates: `deepseek_update_check`, `deepseek_update_apply`

Do not proactively run approval-prone commands such as `npm install`, `npm audit`, `curl`, `gh`, `git push`, package manager commands, dependency installation, or GitHub publishing commands unless the user explicitly asks for dependency setup, security audit, release, publishing, repository creation, or pushing.

If a task can be answered with an MCP tool, use the MCP tool first. Only request shell/network approval when it is necessary for a user-requested operation and cannot be completed through DeepSeekHelper's MCP tools.

For plugin updates, prefer `deepseek_update_check` and `deepseek_update_apply` over shell git commands. Only use `deepseek_update_apply` when the user explicitly asks to update the plugin.

## Tools

- `deepseekhelper_status`: confirm configuration, automatic model policy, data paths, and available models.
- `deepseek_models`: fetch currently available DeepSeek API models and profile classification.
- `deepseek_auth_check`: verify the configured key works for both model listing and chat completions.
- `deepseek_usage_summary`: summarize calls, tokens, cache hit rate, and estimated cost.
- `deepseek_usage_tail`: inspect recent usage records without prompt or response content.
- `deepseek_update_check`: check whether the plugin is behind its git upstream without modifying files.
- `deepseek_update_apply`: explicitly fast-forward the plugin from its git upstream.
- `deepseek_task`: supervised low/medium task assistance.
- `deepseek_review`: independent review of code, docs, plans, prompts, or summaries.
- `deepseek_discuss`: trade-off discussion for higher difficulty decisions.
- `deepseek_verify`: claim, assumption, edge-case, and test-gap verification.
- `deepseek_prompt`: generate strict prompts for later delegation or review.

## Model Selection

Each DeepSeek call should disclose the model it used and why.

Selection order:

1. Explicit `model` argument on the tool call.
2. `DEEPSEEKHELPER_MODEL` or legacy `DEEPSEEK_MODEL` if configured and not `auto`.
3. Automatic policy, based on the daily cached DeepSeek `/models` list:
   - `deepseek_task` low/medium: latest flash-class model, thinking disabled by default
   - `deepseek_prompt`: latest flash-class model, thinking disabled by default
   - review, discussion, verification, or high-complexity support: latest pro-class model, thinking enabled with high effort by default

Use `deepseekhelper_status` or `deepseek_models` before important work if model availability matters.

The model list is cached for one day by default. Use the refresh arguments on status/model tools when a fresh lookup is required.

## Usage Tracking

The plugin records usage metadata in `data/usage.jsonl`: timestamp, tool, model, model tier, model selection source, thinking mode, token counts, cache hit/miss tokens, and estimated cost. It does not store full prompts or responses.

## Review Handling

After receiving DeepSeek feedback, evaluate each point against local evidence. Apply only valid feedback. Briefly explain any important suggestion that Codex rejects.
