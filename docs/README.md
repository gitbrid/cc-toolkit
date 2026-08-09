# Skills 与 MCP 收集文档

本项目的 skills 与 MCP 集合。skills 按来源分类，每个来源的详细介绍见下方子文档；MCP 推荐清单见 [mcp/README.md](../mcp/README.md)。

> **规则**：每次新增 skills / MCP 项目后，更新本文档和对应的详细介绍子文档。

---

## 已收集的 Skills 项目

### 1. [mattpocock/skills](./mattpocock-skills-介绍.md)

**作者**：Matt Pocock（TypeScript 知名布道师）

**定位**：为"真正的工程开发"设计的 Agent Skills，强调软件工程基础（小步反馈、领域建模、红绿重构），而非 vibe coding。

**技能数量**：41 个技能（22 个推广 + 19 个未推广/开发中/已废弃），分工程类和生产力类。

**一句话总结**：把几十年的软件工程经验压缩成可复用的 AI Agent 技能，帮你写出能维护的代码而不是一次性原型。

---

### 2. [alchaincyf/nuwa-skill](./nuwa-skill-介绍.md) ✅

**作者**：花叔（Huashu，AI Native Coder，独立开发者）

**定位**：蒸馏名人的思维方式——心智模型、决策启发式、表达 DNA。不是蒸馏同事，而是蒸馏乔布斯、马斯克、芒格等顶尖人物。

**技能数量**：14 个人物 + 1 个主题（X/Twitter 运营）。

**一句话总结**：用 AI 镜像任何人的思维模式，让 Agent 以特定人物的风格和决策方式思考和回应。

**本地路径**：`D:\program\CC 工具库\skills\nuwa-skill\`

---

### 3. [wshobson/agents](./wshobson-skills-介绍.md) ✅

**作者**：wshobson

**定位**：代码质量和工程实践深度技能——代码审查、调试、Python 性能优化、测试模式。

**技能数量**：4 个技能。

**一句话总结**：为 Python 开发者提供技术深度的 Agent 技能，补足工作流技能在具体编码实践上的盲区。

**本地路径**：`D:\program\CC 工具库\skills\wshobson-skills\`

---

### 4. [anthropics/skills](./anthropics-skills-介绍.md) ✅

**作者**：Anthropic 官方

**定位**：官方通用能力扩展——前端设计、文档处理、MCP 构建、技能发现/创建、Web 测试、设计工具。Apache 2.0 许可。

**技能数量**：17 个技能。

**一句话总结**：官方维护的高质量通用技能，覆盖设计、文档、开发、测试全场景。

**本地路径**：`D:\program\CC 工具库\skills\anthropics-skills\`

---

### 5. [自定义 Agent](./custom-agents-介绍.md) ✅

**来源**：从实际项目中提取

**定位**：针对 Python 项目的中文 Claude Code Agent——代码审查、质量守门、测试运行、项目管理。

**数量**：4 个 Agent。

**一句话总结**：经过实战验证的中文 Agent 模板，可直接复用或按需定制。

**本地路径**：`D:\program\CC 工具库\skills\custom-agents\`

---

### 6. [obra/superpowers](./superpowers-skills-介绍.md) ✅

**作者**：Jesse Vincent（obra）

**定位**：工程工作流技能合集——设计→计划→执行→审查→验证的完整流程纪律，带 HARD-GATE 硬性门禁。

**技能数量**：14 个技能。

**一句话总结**：把「没设计不写码、没验证不完成」固化为可强制执行的技能，与 mattpocock/skills 流程互补。

**本地路径**：`D:\program\CC 工具库\skills\superpowers-skills\`

---

### 7. [cexll/myclaude](./cexll-skills-介绍.md) ✅

**作者**：cexll

**定位**：自动化与工作流合集——浏览器自动化、多 Agent 编排、产品需求、测试用例、技能安装。

**技能数量**：11 个技能（其中 codeagent/dev 依赖外部 CLI codeagent-wrapper）。

**一句话总结**：实用的自动化技能，部分依赖外部工具，按需选用。

**本地路径**：`D:\program\CC 工具库\skills\cexll-skills\`

---

### 8. [杂项技能](./misc-skills-介绍.md) ✅

**来源**：零散收集（hamsterider-m/bilibili-subtitle 等）

**定位**：暂未成合集的单一技能。

**技能数量**：1 个技能。

**一句话总结**：B站字幕提取等杂项技能，按需启用。

**本地路径**：`D:\program\CC 工具库\skills\misc-skills\`

---

## MCP 收藏

好用的 MCP 服务器推荐与收藏见 [mcp/README.md](../mcp/README.md)，涵盖官方全家桶、社区高频、按场景速查。

### DeepSeek 工具集（2026-08-09 收录）✅

**[DeepSeek 工具](./deepseek-tools-介绍.md)** — DeepSeekHelper（Codex 插件）、DeepSeek MCP Server、DeepSeek Vision（Codex 插件）已收录并部署：
- DeepSeekHelper：Codex 与 DeepSeek 监督协作，委托/审查/讨论/验证/用量统计
- DeepSeek MCP Server：`deepseek_chat` / `deepseek_fim` / `deepseek_sessions`
- DeepSeek Vision：给纯文本 DeepSeek 补图片分析、OCR、扫描 PDF 转 DOCX
- B站视频阅读器已切到 `deepseek-v4-flash`

### 本地 RAG（知识库检索，实战验证）✅

**[rag-mcp + llama.cpp](./rag-mcp-介绍.md)** — 对本地 PDF/文档库做向量检索，数据不出本机。伴学项目（60+ 本教材书库）实战收录：
- 工具：`index_document` / `search_docs` / `list_indexed_docs` / `delete_document`
- embedding 后端：llama.cpp `llama-server` + bge-m3（1024 维多语言，中文好），端口 8080，OpenAI 兼容 `/v1/embeddings`
- 存储：ChromaDB 持久化；中文教材扫描版需先 OCR；数学公式页读图而非 OCR

### 2026-08-09 第二批工具 ✅

- [rag-mcp-server](./rag-mcp-server-介绍.md)：Rubrum95 RAG MCP 备选，OCR + 页码引用
- [pdf-mcp](./pdf-mcp-介绍.md)：大 PDF 精准读取 MCP，混合检索 + OCR + 表格提取，已挂到 Codex
- [the-learning-skill](./the-learning-skill-介绍.md)：学习教练 Agent Skill，已复制到伴学项目
- [obsidian-deepseek-note-helper](./obsidian-deepseek-note-helper-介绍.md)：Obsidian 侧边栏 DeepSeek 助手插件

### 本地 OCR（便携 Tesseract）✅

**[tesseract-portable-介绍](./tesseract-portable-介绍.md)** — 免管理员便携 Tesseract（chi_sim/eng/osd），为 pdf-mcp 和 deepseek-vision 提供本地 OCR 兜底；DeepSeek 官方 API 不支持图片，图片/扫描 PDF 默认走本地识别。

---

## 更新日志

| 日期 | 变更 |
|------|------|
| 2026-07-24 | 初始创建，收录 mattpocock/skills、alchaincyf/nuwa-skill |
| 2026-07-24 | 新增 wshobson/agents、anthropics/skills、自定义 Agent |
| 2026-08-01 | 新增 obra/superpowers（14）、cexll/myclaude（11）、杂项（1）；anthropics/skills 扩充至 17 |
| 2026-08-01 | 目录重组：所有技能来源收进 `skills/` 子库，新增 `mcp/` 子库 |
| 2026-08-01 | MCP 排障：移除 time（官方包下架 404）与 fetch（npm 同名包为蜜罐），本机收敛为 4 个可用 MCP |
| 2026-08-01 | 新增本地 RAG：rag-mcp + llama.cpp + bge-m3（伴学项目实战收录），见 [rag-mcp-介绍.md](./rag-mcp-介绍.md) |
| 2026-08-09 | 新增 DeepSeek 工具集：DeepSeekHelper、DeepSeek MCP Server、DeepSeek Vision，见 [deepseek-tools-介绍.md](./deepseek-tools-介绍.md) |
| 2026-08-09 | 第二批：rag-mcp-server、pdf-mcp、the-learning-skill、obsidian-deepseek-note-helper 收录 |
| 2026-08-09 | 本地 OCR：便携 Tesseract（chi_sim/eng/osd）+ deepseek-vision 本地兜底，更新全部 DeepSeek key |

## GitHub 热点归档（2026-08-09 新增）

新增 [github-trending-介绍.md](./github-trending-介绍.md)：每周自动收集 GitHub 热点项目（周榜/月榜，三种口径 Top 10-15），归档为 Obsidian 库 `github-trending/`，并已补录 2026-01-01 至今共 32 周。
