# DeepSeekHelper

[![Version](https://img.shields.io/badge/version-0.3.4-blue)](https://github.com/UrgencyWu/deepseekhelper)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Node](https://img.shields.io/badge/node-%3E%3D18-brightgreen)](https://nodejs.org)
[![Codex Plugin](https://img.shields.io/badge/codex-plugin-8A2BE2)](https://github.com/anthropics/claude-code)

<p align="center">
  <img src="assets/banner.svg" alt="DeepSeekHelper banner" width="800">
</p>

[English](#english) | [中文](#中文)

A [Codex](https://github.com/anthropics/claude-code) plugin that exposes DeepSeek-powered MCP tools for supervised collaboration. Codex delegates, reviews, discusses, and verifies work with DeepSeek while keeping final edits, tests, and judgment inside Codex.

---

一个 Codex 插件，通过 MCP 工具让 Codex 与 DeepSeek 进行有监督的协作。Codex 可以将中低难度的工作委托给 DeepSeek，也可以使用 DeepSeek 进行审查、讨论和验证，同时将最终编辑、测试和判断保留在 Codex 内。

---

## Star History

<a href="https://www.star-history.com/?type=date&repos=UrgencyWu%2Fdeepseekhelper">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=UrgencyWu/deepseekhelper&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=UrgencyWu/deepseekhelper&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=UrgencyWu/deepseekhelper&type=date&legend=top-left" />
 </picture>
</a>
---

## English

### About

DeepSeekHelper adds twelve local MCP tools to Codex, each wrapping the DeepSeek API with structured supervision boundaries:

`DS`, `ds`, `DeepSeek`, `deepseek`, `DeepSeekHelper`, `deepseekhelper`, and `DeepSeek Helper` are equivalent names in everyday prompts. Alias matching is case-insensitive. For example, "Ask DS to review this diff" and "ask deepseek to review this diff" should trigger the same workflow as "Ask DeepSeekHelper to review this diff."

- **Delegation** — `deepseek_task` sends scoped, low/medium difficulty work to DeepSeek for drafts, plans, snippets, and documentation.
- **Review** — `deepseek_review` gets an independent second pair of eyes on code, docs, plans, prompts, or implementation summaries.
- **Discussion** — `deepseek_discuss` compares trade-offs, risks, and alternatives for higher-difficulty decisions.
- **Verification** — `deepseek_verify` checks claims, assumptions, edge cases, and test gaps against the evidence Codex provides.
- **Prompt generation** — `deepseek_prompt` creates strict delegation or review prompts so Codex can hand off work with clear constraints.
- **Model management** — `deepseekhelper_status`, `deepseek_models`, and `deepseek_auth_check` surface available models, automatic Flash/Pro classification, and API connectivity.
- **Usage tracking** — `deepseek_usage_summary` and `deepseek_usage_tail` report token counts, cache hit rates, and estimated costs without logging prompt or response content.
- **Explicit updates** — `deepseek_update_check` and `deepseek_update_apply` let users check and apply git upstream updates on demand.

The plugin automatically selects the right DeepSeek model for the job: Flash-class for drafting and prompt generation, Pro-class with thinking for review, discussion, and verification. Every call records anonymous usage metadata locally so you can audit cost and cache efficiency over time.

### Features

- Supervised low and medium difficulty task assistance.
- Independent review for code, documentation, plans, prompts, and implementation summaries.
- Design and architecture discussion with trade-offs.
- Verification of claims, assumptions, edge cases, and test gaps.
- Automatic Flash/Pro model selection from the DeepSeek `/models` list.
- Token, cache hit/miss, and estimated cost tracking.

### Requirements

- Codex with local plugin support.
- Node.js 18 or newer.
- A DeepSeek API key.

### Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/UrgencyWu/deepseekhelper.git
cd deepseekhelper
npm install
```

Install or register the plugin in Codex using the plugin directory. The plugin includes:

```text
.codex-plugin/plugin.json
.mcp.json
skills/deepseekhelper/SKILL.md
scripts/server.mjs
```

The included `.mcp.json` starts the MCP server with:

```json
{
  "mcpServers": {
    "deepseekhelper": {
      "command": "node",
      "args": ["scripts/server.mjs"]
    }
  }
}
```

If your Codex plugin host does not start MCP servers from the plugin root, replace `scripts/server.mjs` with the absolute path to your local `scripts/server.mjs`.

### Configuration

Set your DeepSeek API key before starting Codex:

```bash
export DEEPSEEK_API_KEY="your-deepseek-api-key"
```

On macOS, Codex launched as a desktop app may not inherit shell variables. You can set the key through `launchctl` and restart Codex:

```bash
launchctl setenv DEEPSEEK_API_KEY "your-deepseek-api-key"
```

DeepSeekHelper falls back to `launchctl getenv DEEPSEEK_API_KEY` on macOS if the variable is not present in the direct process environment.

Optional settings:

```bash
export DEEPSEEKHELPER_MODEL=auto
export DEEPSEEKHELPER_MODEL_CACHE_DAYS=1
export DEEPSEEK_BASE_URL=https://api.deepseek.com
```

Do not commit `.env` files or real API keys. See `.env.example` for a template.

### Tools

| Tool | Purpose |
|---|---|
| `deepseekhelper_status` | Show configuration, model policy, data paths, and available models. |
| `deepseek_models` | Fetch available DeepSeek models and show profile classification. |
| `deepseek_auth_check` | Verify the key can call both `/models` and chat completions. |
| `deepseek_task` | Ask DeepSeek to handle low or medium difficulty work under Codex supervision. |
| `deepseek_review` | Ask DeepSeek for independent review. |
| `deepseek_discuss` | Ask DeepSeek to compare options and risks. |
| `deepseek_verify` | Ask DeepSeek to verify claims, assumptions, edge cases, and test gaps. |
| `deepseek_prompt` | Ask DeepSeek to create a strict delegation or review prompt. |
| `deepseek_usage_summary` | Summarize calls, tokens, cache hit rate, and estimated cost. |
| `deepseek_usage_tail` | Show recent usage records without prompt or response content. |
| `deepseek_update_check` | Check whether the plugin is behind its git upstream without modifying files. |
| `deepseek_update_apply` | Explicitly fast-forward the plugin from its git upstream. |

### Model Selection

Selection order:

1. Explicit `model` argument on a tool call.
2. `DEEPSEEKHELPER_MODEL` or legacy `DEEPSEEK_MODEL`, if configured and not `auto`.
3. Automatic policy using the daily cached DeepSeek `/models` list.

Automatic policy:

- `deepseek_task` low/medium: latest Flash-class model, thinking disabled by default.
- `deepseek_prompt`: latest Flash-class model, thinking disabled by default.
- `deepseek_review`, `deepseek_discuss`, `deepseek_verify`: latest Pro-class model, thinking enabled with high effort by default.

The model list is cached for one day by default in `data/models-cache.json`. Use the refresh arguments on `deepseekhelper_status` or `deepseek_models` to force a fresh lookup.

### Default Collaboration Strategy

DeepSeek token cost is treated as non-constraining. Codex should apply this strategy automatically when the user asks for DS, DeepSeek, or DeepSeekHelper collaboration:

- Trivial edits: Codex should handle them directly without DS.
- Medium code changes: use `deepseek_task` first for a focused plan, snippet, or unified diff; Codex then applies and verifies.
- Documentation or design drafts: use `deepseek_task` for a first draft; Codex edits for local accuracy and style.
- High-difficulty code, architecture, security, data, release, or migration work: Codex leads implementation and uses `deepseek_discuss`, `deepseek_review`, or `deepseek_verify` for second-model scrutiny.
- Published or user-visible conclusions: use `deepseek_verify` when accuracy or omissions matter.

Codex should pass compact, relevant context to DS instead of dumping an entire repository. Codex remains responsible for file edits, command execution, tests, and final judgment.

### Usage Tracking

Each DeepSeek API call appends metadata to:

```text
data/usage.jsonl
```

The log records timestamps, tool name, model, model tier, thinking mode, token counts, cache hit/miss tokens, and estimated cost. It does not record prompts or responses.

`data/` is ignored by git and should remain local.

### Low-Approval Workflow

For routine use, ask Codex to call DeepSeekHelper MCP tools directly. Normal status checks, model checks, auth checks, task delegation, review, discussion, verification, prompt generation, and usage reports should not require shell commands.

Use phrases such as:

```text
Use DeepSeekHelper to review this diff.
Ask DeepSeekHelper to discuss these design options.
Show today's DeepSeekHelper token usage.
Run a DeepSeekHelper auth check.
```

Avoid approval-prone shell workflows for everyday use. Commands such as `npm install`, `npm audit`, `curl`, `gh`, `git push`, dependency installation, and GitHub publishing should only be run when you explicitly ask for setup, audit, release, or publishing work.

### Updating

DeepSeekHelper updates are explicit. The plugin does not update itself in the background.

Use:

```text
Ask DeepSeekHelper to check for updates.
Ask DeepSeekHelper to update itself.
Ask DeepSeekHelper to update itself and install dependencies if needed.
```

The update tools use the plugin's git upstream:

- `deepseek_update_check`: checks branch, upstream, cleanliness, and ahead/behind state. It does not modify files.
- `deepseek_update_apply`: refuses to run if the working tree is dirty, runs `git fetch --prune`, then `git pull --ff-only`.

If `package.json` or `package-lock.json` changes, `deepseek_update_apply` only runs `npm install` when called with `install_dependencies: true`.

After an update, reload or restart Codex so the MCP server uses the new code.

### Development Checks

Run:

```bash
node --check scripts/server.mjs
npm audit --omit=dev
```

If you have the Codex plugin creator validation script available, run:

```bash
python3 /path/to/plugin-creator/scripts/validate_plugin.py .
```

### Security

Never commit API keys, `.env`, `data/`, `node_modules/`, usage logs, or model cache files. See `SECURITY.md`.

### Contributing

See `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`.

### License

MIT

---

## 中文

### 关于

DeepSeekHelper 为 Codex 提供了十二个本地 MCP 工具，每个工具封装了 DeepSeek API，并带有结构化的监督边界：

在日常提示中，`DS`、`ds`、`DeepSeek`、`deepseek`、`DeepSeekHelper`、`deepseekhelper` 和 `DeepSeek Helper` 都表示同一个插件。别名匹配不区分大小写。例如“让 DS 复核这个 diff”、“让 deepseek 复核这个 diff”和“让 DeepSeekHelper 复核这个 diff”应触发相同工作流。

- **委托** — `deepseek_task` 将限定范围的中低难度工作发送给 DeepSeek，获取草稿、计划、代码片段和文档。
- **审查** — `deepseek_review` 让 DeepSeek 作为独立的第二双眼睛，审查代码、文档、计划、提示词或实现总结。
- **讨论** — `deepseek_discuss` 对比权衡、风险和替代方案，辅助高难度决策。
- **验证** — `deepseek_verify` 根据 Codex 提供的证据，检查声明、假设、边界情况和测试盲区。
- **提示词生成** — `deepseek_prompt` 创建严格的委托或审查提示词，让 Codex 以清晰的约束交付工作。
- **模型管理** — `deepseekhelper_status`、`deepseek_models` 和 `deepseek_auth_check` 展示可用模型、自动 Flash/Pro 分类以及 API 连通性。
- **用量跟踪** — `deepseek_usage_summary` 和 `deepseek_usage_tail` 报告 token 数量、缓存命中率和预估费用，不记录提示词或响应内容。
- **显式更新** — `deepseek_update_check` 和 `deepseek_update_apply` 让用户按需检查并应用 git 上游更新。

插件会自动为任务选择合适的 DeepSeek 模型：草稿和提示词生成使用 Flash 级模型，审查、讨论和验证使用带思考模式的 Pro 级模型。每次调用都会在本地匿名记录用量元数据，方便随时审计成本和缓存效率。

### 功能

- 有监督的中低难度任务辅助。
- 对代码、文档、计划、提示词和实现总结的独立审查。
- 带权衡分析的设计和架构讨论。
- 对声明、假设、边界情况和测试盲区的验证。
- 基于 DeepSeek `/models` 列表的自动 Flash/Pro 模型选择。
- Token、缓存命中/未命中和预估费用跟踪。

### 环境要求

- 支持本地插件的 Codex。
- Node.js 18 或更高版本。
- DeepSeek API 密钥。

### 安装

克隆仓库并安装依赖：

```bash
git clone https://github.com/UrgencyWu/deepseekhelper.git
cd deepseekhelper
npm install
```

在 Codex 中通过插件目录安装或注册插件。插件包含：

```text
.codex-plugin/plugin.json
.mcp.json
skills/deepseekhelper/SKILL.md
scripts/server.mjs
```

插件内置的 `.mcp.json` 启动 MCP 服务器：

```json
{
  "mcpServers": {
    "deepseekhelper": {
      "command": "node",
      "args": ["scripts/server.mjs"]
    }
  }
}
```

如果你的 Codex 插件宿主不从插件根目录启动 MCP 服务器，请将 `scripts/server.mjs` 替换为本地的绝对路径。

### 配置

启动 Codex 前设置 DeepSeek API 密钥：

```bash
export DEEPSEEK_API_KEY="your-deepseek-api-key"
```

在 macOS 上，以桌面应用方式启动的 Codex 可能无法继承 Shell 环境变量。可以通过 `launchctl` 设置密钥并重启 Codex：

```bash
launchctl setenv DEEPSEEK_API_KEY "your-deepseek-api-key"
```

在 macOS 上，如果直接进程环境中没有该变量，DeepSeekHelper 会回退到 `launchctl getenv DEEPSEEK_API_KEY`。

可选设置：

```bash
export DEEPSEEKHELPER_MODEL=auto
export DEEPSEEKHELPER_MODEL_CACHE_DAYS=1
export DEEPSEEK_BASE_URL=https://api.deepseek.com
```

不要提交 `.env` 文件或真实 API 密钥。参考 `.env.example` 模板。

### 工具

| 工具 | 用途 |
|---|---|
| `deepseekhelper_status` | 显示配置、模型策略、数据路径和可用模型。 |
| `deepseek_models` | 获取可用 DeepSeek 模型及分类。 |
| `deepseek_auth_check` | 验证密钥是否能调用 `/models` 和聊天补全接口。 |
| `deepseek_task` | 委托中低难度工作给 DeepSeek，由 Codex 监督。 |
| `deepseek_review` | 请 DeepSeek 进行独立审查。 |
| `deepseek_discuss` | 请 DeepSeek 对比选项和风险。 |
| `deepseek_verify` | 请 DeepSeek 验证声明、假设、边界情况和测试盲区。 |
| `deepseek_prompt` | 请 DeepSeek 创建严格的委托或审查提示词。 |
| `deepseek_usage_summary` | 汇总调用次数、token、缓存命中率和预估费用。 |
| `deepseek_usage_tail` | 查看最近的用量记录（不含提示词和响应内容）。 |
| `deepseek_update_check` | 检查插件是否落后于 git 上游，不修改文件。 |
| `deepseek_update_apply` | 显式从 git 上游快进更新插件。 |

### 模型选择

选择优先级：

1. 工具调用时显式传入的 `model` 参数。
2. `DEEPSEEKHELPER_MODEL` 或旧版 `DEEPSEEK_MODEL`（如已配置且不为 `auto`）。
3. 基于每日缓存的 DeepSeek `/models` 列表的自动策略。

自动策略：

- `deepseek_task` 中低难度：最新 Flash 级模型，默认关闭思考模式。
- `deepseek_prompt`：最新 Flash 级模型，默认关闭思考模式。
- `deepseek_review`、`deepseek_discuss`、`deepseek_verify`：最新 Pro 级模型，默认开启高力度思考模式。

模型列表默认缓存一天，存储在 `data/models-cache.json`。使用 `deepseekhelper_status` 或 `deepseek_models` 的刷新参数可强制更新。

### 默认协作策略

DeepSeek token 成本视为非约束。用户要求使用 DS、DeepSeek 或 DeepSeekHelper 协作时，Codex 应自动应用以下策略：

- 极简单改动：Codex 直接完成，不调用 DS。
- 中等代码修改：先用 `deepseek_task` 获取聚焦方案、代码片段或 unified diff；再由 Codex 应用并验证。
- 文档或方案草稿：先用 `deepseek_task` 起草；再由 Codex 根据本地上下文和风格修订。
- 高难度代码、架构、安全、数据、发布或迁移工作：Codex 主导实现，并使用 `deepseek_discuss`、`deepseek_review` 或 `deepseek_verify` 做第二模型复核。
- 对外发布或用户可见的重要结论：当准确性和遗漏风险重要时，使用 `deepseek_verify`。

Codex 应传递精简且相关的上下文给 DS，而不是发送整个仓库。文件修改、命令执行、测试和最终判断仍由 Codex 负责。

### 用量跟踪

每次 DeepSeek API 调用的元数据追加到：

```text
data/usage.jsonl
```

日志记录时间戳、工具名、模型、模型层级、思考模式、token 数量、缓存命中/未命中 token 以及预估费用。不记录提示词或响应内容。

`data/` 已被 git 忽略，应保留在本地。

### 低批准工作流

日常使用时，直接让 Codex 调用 DeepSeekHelper 的 MCP 工具。常规状态检查、模型检查、认证检查、任务委托、审查、讨论、验证、提示词生成和用量报告都不需要通过 Shell 命令完成。

可以这样说：

```text
用 DeepSeekHelper 复核这个 diff。
让 DeepSeekHelper 讨论这些设计方案。
查看今天 DeepSeekHelper 的 token 用量。
运行 DeepSeekHelper 认证检查。
```

避免在日常使用中触发需要批准的 Shell 工作流。`npm install`、`npm audit`、`curl`、`gh`、`git push`、依赖安装和 GitHub 发布命令，只有在你明确要求安装、审计、发布或推送时才应运行。

### 更新

DeepSeekHelper 的更新是显式触发的。插件不会在后台自动更新自己。

可以这样说：

```text
让 DeepSeekHelper 检查更新。
让 DeepSeekHelper 更新自己。
让 DeepSeekHelper 更新自己，并在需要时安装依赖。
```

更新工具使用插件所在仓库的 git 上游：

- `deepseek_update_check`：检查分支、上游、工作区是否干净，以及 ahead/behind 状态。不修改文件。
- `deepseek_update_apply`：如果工作区有本地改动会拒绝执行；否则运行 `git fetch --prune`，再运行 `git pull --ff-only`。

如果 `package.json` 或 `package-lock.json` 变化，`deepseek_update_apply` 只有在调用参数 `install_dependencies: true` 时才运行 `npm install`。

更新后需要重新加载或重启 Codex，让 MCP server 使用新代码。

### 开发检查

运行：

```bash
node --check scripts/server.mjs
npm audit --omit=dev
```

如果你有 Codex 插件创建器验证脚本，运行：

```bash
python3 /path/to/plugin-creator/scripts/validate_plugin.py .
```

### 安全

切勿提交 API 密钥、`.env`、`data/`、`node_modules/`、用量日志或模型缓存文件。详见 `SECURITY.md`。

### 参与贡献

详见 `CONTRIBUTING.md` 和 `CODE_OF_CONDUCT.md`。

### 许可证

MIT
