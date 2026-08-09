# Changelog

## 0.3.3 — 2026-05-25

- Two new tools: `deepseek_update_check` and `deepseek_update_apply` for explicit git upstream update management.
- Plugin alias support: `DS`, `ds`, `DeepSeek`, `deepseek`, `DeepSeekHelper`, `deepseekhelper`, and `DeepSeek Helper` are equivalent names (case-insensitive).
- Low-approval workflow guidance: MCP tools for everyday use, shell commands only for explicit setup/audit/release work.
- Update safety: `deepseek_update_apply` refuses dirty working trees and uses `--ff-only` pulls.

## 0.3.2 — 2026-05-25

- First public release.
- Ten MCP tools: `deepseekhelper_status`, `deepseek_models`, `deepseek_auth_check`, `deepseek_task`, `deepseek_review`, `deepseek_discuss`, `deepseek_verify`, `deepseek_prompt`, `deepseek_usage_summary`, `deepseek_usage_tail`.
- Automatic Flash/Pro model selection from the cached DeepSeek `/models` list.
- Configurable model override via `DEEPSEEKHELPER_MODEL` and legacy `DEEPSEEK_MODEL`.
- Thinking mode control: disabled by default for Flash-class tasks, enabled with high reasoning effort for Pro-class review/discussion/verification.
- Token, cache hit/miss, and estimated cost tracking in `data/usage.jsonl`.
- Local model cache with configurable TTL (`DEEPSEEKHELPER_MODEL_CACHE_DAYS`).
- macOS `launchctl` fallback for `DEEPSEEK_API_KEY`.
- `sanitizeErrorMessage` redacts API keys and bearer tokens from error output.
