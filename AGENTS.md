# CC 工具库 — Codex Skills 工具箱

## 项目定位

这是我的**中央 Skills + MCP 仓库**，收集和整理各类 Codex / Agent Skills 和好用的 MCP 服务器。其他项目不直接修改这里的文件，而是从这里**复制所需技能 / MCP 配置**到自己的项目里。

## 目录结构

```
CC 工具库/
├── AGENTS.md                    ← 你在这里
├── docs/                        ← 所有技能的详细介绍文档
│   ├── README.md                ← 总索引（先看这个）
│   ├── deepseek-tools-介绍.md   ← DeepSeek 工具集（2026-08-09 收录）
│   ├── mattpocock-skills-介绍.md
│   ├── nuwa-skill-介绍.md
│   ├── wshobson-skills-介绍.md
│   ├── anthropics-skills-介绍.md
│   ├── superpowers-skills-介绍.md
│   ├── cexll-skills-介绍.md
│   ├── misc-skills-介绍.md
│   └── custom-agents-介绍.md
├── skills/                      ← 所有技能的来源子库
│   ├── mattpocock-skills/       ← mattpocock/skills (41个技能)
│   ├── nuwa-skill/              ← alchaincyf/nuwa-skill (15个思维视角)
│   ├── wshobson-skills/         ← wshobson/agents (4个Python深度技能)
│   ├── anthropics-skills/       ← anthropics/skills (17个通用技能)
│   ├── superpowers-skills/      ← obra/superpowers (14个工程工作流技能)
│   ├── cexll-skills/            ← cexll/myclaude (11个自动化技能)
│   ├── misc-skills/             ← 杂项技能 (1个)
│   ├── custom-agents/           ← 自定义Agent (4个中文Agent)
│   └── the-learning-skill/      ← 学习教练技能（toddward，2026-08-09收录）
├── plugins/                     ← Codex / Obsidian 插件源码（deepseekhelper / deepseek-vision / obsidian-deepseek-note-helper）
└── mcp/                         ← MCP 收藏子库
    └── README.md                ← MCP 推荐清单与收藏索引
```

## 技能清单速览

| 来源 | 数量 | 定位 | 什么时候用 |
|------|------|------|-----------|
| **mattpocock/skills** | 41个 | 工程工作流 | 需要完整开发流程：需求对齐→spec→实现→审查 |
| **nuwa-skill** | 15个 | 名人思维蒸馏 | 需要以特定人物视角思考（乔布斯/马斯克/芒格...） |
| **wshobson/agents** | 4个 | Python代码质量 | 写Python项目时需要深度代码审查/调试/优化/测试 |
| **anthropics/skills** | 17个 | 官方通用能力 | 设计、文档处理(PDF/Word/Excel)、MCP、技能开发、Web测试 |
| **superpowers-skills** | 14个 | 工程流程纪律 | 需要强制「设计→计划→执行→审查→验证」流程，防返工 |
| **cexll-skills** | 11个 | 自动化工作流 | 浏览器自动化、多Agent编排、PRD、测试用例（部分依赖外部CLI） |
| **misc-skills** | 1个 | 杂项 | B站字幕提取等零散技能 |
| **custom-agents** | 4个 | 中文Agent模板 | 需要代码审查/质量检查/测试运行/项目管理Agent |

### 场景速查表

| 我想... | 用哪个 |
|--------|-------|
| 开始一个新功能前对齐需求 | mattpocock: `/grill-with-docs` |
| 把想法变成可执行的任务 | mattpocock: `/to-spec` → `/to-tickets` → `/implement` |
| 修一个难搞的 Bug | mattpocock: `/diagnosing-bugs` + wshobson: `debugging-strategies` |
| 代码变成一坨烂泥了 | mattpocock: `/improve-codebase-architecture` |
| 写高质量 Python 测试 | wshobson: `python-testing-patterns` |
| 用乔布斯视角做产品决策 | nuwa-skill: `steve-jobs-perspective` |
| 用第一性原理拆解问题 | nuwa-skill: `elon-musk-perspective` |
| 做一个漂亮的 UI | anthropics: `frontend-design` |
| 处理 PDF / Word / Excel | anthropics: `pdf` / `docx` / `xlsx` |
| 开发一个 MCP 服务器 | anthropics: `mcp-builder` |
| 自己开发一个新 Skill | anthropics: `skill-creator` |
| 动手前先想清楚设计（防返工） | superpowers: `brainstorming` → `writing-plans` → `executing-plans` |
| 要写代码先写测试 | superpowers: `test-driven-development` |
| 声称"完成"前验证一下 | superpowers: `verification-before-completion` |
| 并行跑多个独立任务 | superpowers: `dispatching-parallel-agents` |
| 浏览器自动化操作 | cexll: `browser` |
| 生成 PRD / 测试用例 | cexll: `product-requirements` → `test-cases` |
| 提取 B站视频字幕 | misc: `bilibili-subtitle` |
| 本地 PDF/文档库语义检索 | mcp/README 的「本地 RAG」→ [docs/rag-mcp-介绍.md](docs/rag-mcp-介绍.md) |
| 从 GitHub 找好项目 | 本项目的 `github-discovery` 技能 |

## 如何给其他项目安装技能

### 方式一：手动复制（推荐，保持独立）

```bash
# 在新项目的 .Codex/skills/ 下创建技能目录
cp -r "D:/program/CC 工具库/skills/wshobson-skills/python-testing-patterns" \
      "目标项目/.Codex/skills/python-testing-patterns"
```

### 方式二：在新项目的 AGENTS.md 中引用

在目标项目的 `AGENTS.md` 中加入以下提示：

```markdown
## Skills 工具箱

本项目的 skills 依赖位于 `D:\program\CC 工具库` 的中央工具箱。

- **可用技能清单**：先读 `D:\program\CC 工具库\docs\README.md` 了解所有可用技能
- **日常开发工作流**：参考 mattpocock/skills（`/grill-with-docs`, `/to-spec`, `/implement` 等）
- **Python 代码质量**：参考 wshobson/agents（`code-review-excellence`, `python-testing-patterns` 等）
- **UI 设计**：参考 anthropics/skills 中的 `frontend-design`
- **需要时从工具箱复制**：从 `D:\program\CC 工具库\skills\$来源\技能名` 复制到 `.Codex/skills/`

当需要某个技能时，先去工具箱查看是否有合适的，然后复制到本项目使用。
```

## 如何添加新技能

### 从 GitHub 发现项目（使用 github-discovery）

```
/github-discovery <搜索关键词>
```

例如：`/github-discovery python testing skills agent`

### 手动添加流程

1. 找到目标 GitHub 仓库
2. 克隆到本工具库：`git clone --depth 1 <url> "D:/program/CC 工具库/skills/<项目名>"`
3. 阅读 README 了解技能内容
4. 写介绍文档到 `docs/<项目名>-skills-介绍.md`
5. 更新 `docs/README.md` 的索引
6. 保存记忆到 `memory/`

## 收藏项目来源

以下 GitHub 仓库/组织是已知的优质 skills 来源：

- `mattpocock/skills` — 工程工作流（已收集）
- `alchaincyf/nuwa-skill` — 思维蒸馏（已收集）
- `wshobson/agents` — Python 代码质量（已收集）
- `anthropics/skills` — 官方通用技能（已收集）
- 更多待 `github-discovery` 发现...

## MCP 收藏

好用的 MCP 服务器推荐与收藏见 [mcp/README.md](mcp/README.md)。

### 手动收藏流程

1. 找到目标 MCP 项目（GitHub 或官方文档）
2. 在 `mcp/` 下新建 `<项目名>/` 子目录，保存安装配置与要点
3. 更新 `mcp/README.md` 的推荐清单
4. 更新 `docs/README.md` 的索引
