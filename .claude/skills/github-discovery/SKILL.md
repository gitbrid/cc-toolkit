---
name: github-discovery
description: 在 GitHub 上搜索和发现优质项目，评估质量后推荐并下载到本工具库
disable-model-invocation: true
---

# GitHub 项目发现技能

在 GitHub 上搜索好项目，评估质量，推荐下载。专为本工具库设计——发现、评估、收集、整理一条龙。

## 工作流程

### 第一步：明确搜索意图

问清楚用户想要什么类型的项目：
- **关键词**：python / skills / agent / testing / cli / tools / ...
- **用途**：学习、集成到项目、参考架构
- **质量要求**：Stars 门槛、最近更新时间、许可证类型

### 第二步：搜索

使用 WebSearch 或 gh CLI 搜索：

```
WebSearch: "github <keyword> stars:<min> language:python"
```

或使用 gh CLI（如果配置了）：
```bash
gh search repos "<keyword>" --sort stars --limit 10
```

### 第三步：评估

对每个候选项目，通过 GitHub 页面信息评估：

| 维度 | 看什么 | 阈值 |
|------|--------|------|
| **流行度** | Stars、Forks | > 100 stars |
| **活跃度** | 最近 commit 时间 | 最近 6 个月内 |
| **文档质量** | README 长度、是否有中文 | 有完整 README |
| **代码规模** | 文件数、语言组成 | 不空壳 |
| **许可证** | MIT/Apache/... | 有许可证 |

### 第四步：推荐

用表格呈现前 3-5 个推荐，包含：
- 项目名 + URL
- Stars / Forks
- 一句话描述
- 推荐理由

### 第五步：下载和整理

用户选定后，执行：
```bash
git clone --depth 1 <url> "D:/program/CC 工具库/<项目名>"
```

然后按照工具库规范：
1. 读 README，了解项目内容
2. 在 `docs/<项目名>-介绍.md` 写中文介绍文档
3. 更新 `docs/README.md` 索引
4. 保存记忆到 `memory/`

## 搜索建议

优质 skills/agents 项目的常见特征：
- 仓库名包含 `skill`、`agent`、`claude`、`codex` 等关键字
- README 中有 `SKILL.md`、`CLAUDE.md`、`npx skills` 等字样
- 话题标签包含 `claude-code`、`agent-skills`、`ai-agent`
- 作者是有名气的开发者或组织

## 已知优质来源

定期关注以下组织/用户的新项目：
- `github.com/anthropics` — Anthropic 官方
- `github.com/mattpocock` — TypeScript/工程工作流
- `github.com/wshobson` — Python 代码质量
- `github.com/alchaincyf` — 思维蒸馏
- GitHub Topics: `claude-code`、`agent-skills`、`ai-coding-agent`
