# mattpocock/skills — 技能详细介绍

> 来源：https://github.com/mattpocock/skills  
> 安装：`npx skills@latest add mattpocock/skills`  
> 本地路径：`D:\program\CC 工具库\skills\`

---

## 项目概述

Matt Pocock 是 TypeScript 社区的知名布道师（Total TypeScript 创始人）。他基于几十年软件工程经验，构建了这套 Agent Skills，核心理念是**"为真正的工程开发而设计，而非 vibe coding"**。

### 解决的四大问题

| 问题 | 解决方案 | 对应技能 |
|------|---------|---------|
| Agent 没理解你想要什么 | **质询会话**（Grilling Session），让 Agent 在动手前问清楚所有细节 | `/grill-me`, `/grill-with-docs` |
| Agent 太啰嗦 | **共享语言**（Shared Language），建立领域术语表，让 Agent 用精简词汇交流 | `/grill-with-docs`, `/domain-modeling` |
| 代码跑不通 | **反馈循环**（Feedback Loops），红绿重构 + 诊断循环 | `/tdd`, `/diagnosing-bugs` |
| 代码变成一坨烂泥 | **持续关注设计**（Design Every Day），深模块、干净接口 | `/improve-codebase-architecture`, `/codebase-design` |

---

## 技能分类

所有技能分两个维度分类：
- **用户调用（User-invoked）**：只能由用户手动输入 `/xxx` 触发，负责编排流程
- **模型调用（Model-invoked）**：用户或 Agent 都可以触发，存放可复用的规范

---

## 一、工程类技能

### 用户调用

#### 1. `/ask-matt`
- **类型**：用户调用
- **功能**：技能路由导航。不知道用哪个技能？告诉它你的情况，它会推荐最合适的技能。
- **场景**：每次不确定该用什么技能时首先使用

#### 2. `/grill-with-docs`
- **类型**：用户调用
- **功能**：质询会话 + 自动构建项目领域模型。Agent 会深入盘问你需求，同时更新 `CONTEXT.md` 和 ADR（架构决策记录），建立共享语言。
- **场景**：**最有价值的技能之一**。任何改动开始前使用，同时完成需求对齐和术语统一。
- **依赖**：底层使用模型调用的 `grilling` 技能

#### 3. `/setup-matt-pocock-skills`
- **类型**：用户调用
- **功能**：配置向导。设置 issue 追踪器（GitHub/Linear/本地文件）、分类标签、文档存储位置等。
- **场景**：每个项目只需运行一次，在使用其他工程技能之前

#### 4. `/triage`
- **类型**：用户调用
- **功能**：通过状态机管理 issue 的分类流转。
- **场景**：有 issue 需要分类和优先级排序时

#### 5. `/improve-codebase-architecture`
- **类型**：用户调用
- **功能**：扫描代码库，找出可以"深化"的模块（深模块 = 大量功能 + 简洁接口），生成可视化 HTML 报告，然后质询式讨论要改哪个。
- **场景**：每隔几天运行一次，防止代码库熵增

#### 6. `/to-spec`
- **类型**：用户调用
- **功能**：把当前对话内容综合成一份 spec 规格文档，发布到 issue 追踪器。
- **场景**：讨论完后需要正式记录下来时

#### 7. `/to-tickets`
- **类型**：用户调用
- **功能**：把计划/spec/对话拆成一组"曳光弹"ticket，声明每个 ticket 的前置依赖关系，生成本地文件或写入追踪器。
- **场景**：有了 spec 后，需要拆分为可执行的任务时

#### 8. `/implement`
- **类型**：用户调用
- **功能**：按 spec 或 ticket 集合执行实现，在预定的接口边界驱动 `/tdd`，完成后跑 `/code-review` 再提交。
- **场景**：完整的实现工作流，从开始到提交

#### 9. `/wayfinder`
- **类型**：用户调用
- **功能**：规划超过一个 Agent 会话能完成的大型工作。在 issue 追踪器上创建调查类 ticket 的地图，一个个解决直到路径清晰。
- **场景**：大型功能或重构，一次会话做不完

### 模型调用

#### 10. `/prototype`
- **类型**：模型调用
- **功能**：构建一次性原型来回答设计问题——状态/逻辑问题用可运行终端应用，UI 方案则在同一路由下做几个可切换的变体。
- **场景**：不确定怎么做时，先快速原型验证

#### 11. `/diagnosing-bugs`
- **类型**：模型调用
- **功能**：严谨的 Bug 诊断循环：复现 → 最小化 → 假设 → 打点 → 修复 → 回归测试。
- **场景**：任何难以定位的 Bug 或性能回归

#### 12. `/research`
- **类型**：模型调用
- **功能**：针对某个问题，从高可信度一手来源做调研，把发现写成带引用的 Markdown 文件存入仓库，以后台 Agent 方式运行。
- **场景**：需要调研技术方案或了解某个领域知识

#### 13. `/tdd`
- **类型**：模型调用
- **功能**：测试驱动开发，红-绿-重构循环。一次做一个垂直切片（从 API 到 UI）。
- **场景**：所有功能开发和 Bug 修复，提供持续的反馈信号

#### 14. `/domain-modeling`
- **类型**：模型调用
- **功能**：主动构建和打磨项目的领域模型——用术语表挑战术语，用边界场景做压力测试，更新 `CONTEXT.md` 和 ADR。
- **场景**：项目术语开始混乱，或需要统一团队对业务概念的理解

#### 15. `/codebase-design`
- **类型**：模型调用
- **功能**：共享的代码设计规范和词汇——如何设计深模块：大功能、小接口、放在干净的接缝处、可通过接口测试。
- **场景**：写代码时自动参考，不需要手动触发

#### 16. `/code-review`
- **类型**：模型调用
- **功能**：双轴审查自某个固定点以来的 diff。**标准轴**检查是否符合项目代码规范 + Fowler 坏味道基线；**Spec 轴**检查是否忠实实现了原始 issue/PRD。两轴并行运行，互不污染。
- **场景**：提交前、PR 审查时

#### 17. `/resolving-merge-conflicts`
- **类型**：模型调用
- **功能**：逐个处理 git merge/rebase 冲突，按意图追溯每一边的原始来源解决，完成后继续操作——绝不 `--abort`。
- **场景**：遇到合并冲突时

---

## 二、生产力类技能

### 用户调用

#### 18. `/grill-me`
- **类型**：用户调用
- **功能**：质询会话纯享版。Agent 会毫不留情地盘问你关于计划/设计的每个细节，直到决策树的每个分支都有答案。
- **场景**：非代码场景（设计方案、架构决策、职业规划等），不需要生成文档
- **依赖**：底层使用模型调用的 `grilling` 技能

#### 19. `/handoff`
- **类型**：用户调用
- **功能**：把当前对话压缩成交接文档，让另一个 Agent 可以无缝接手。
- **场景**：对话太长、切换模型、或需要把工作转移给另一个人/Agent

#### 20. `/teach`
- **类型**：用户调用
- **功能**：用多会话方式教用户新技能或概念，把当前目录作为有状态的"教学工作室"。
- **场景**：学习新技术栈或概念

#### 21. `/writing-great-skills`
- **类型**：用户调用
- **功能**：写 Skill 的参考手册——写好 Skill 所需的词汇和原则。
- **场景**：自己开发新 Skill 时参考

### 模型调用

#### 22. `/grilling`
- **类型**：模型调用
- **功能**：质询的核心循环——不断盘问直到所有分支都解决。被 `grill-me` 和 `grill-with-docs` 共用。
- **场景**：底层引擎，通常不直接调用

---

## 未推广的类别

项目还有以下文件夹（共 **19 个额外技能**），但这些技能不活跃、不通用或不推荐：

### `skills/misc/` — 4 个（保留但很少用）

| 技能 | 类型 | 说明 |
|------|------|------|
| **git-guardrails-claude-code** | 模型调用 | 设置 Claude Code PreToolUse hook，拦截危险 git 命令（push、reset --hard、clean、branch -D 等） |
| **migrate-to-shoehorn** | 模型调用 | 把测试文件中的 `as` 类型断言迁移到 `@total-typescript/shoehorn` (`fromPartial`, `fromAny`) |
| **scaffold-exercises** | 模型调用 | 创建练习目录结构（section、problem、solution、explainer）并通过 lint 验证 |
| **setup-pre-commit** | 模型调用 | 用 Husky + lint-staged 设置 pre-commit hook（Prettier、类型检查、测试） |

### `skills/personal/` — 2 个（作者个人配置专用）

| 技能 | 类型 | 说明 |
|------|------|------|
| **edit-article** | 用户调用 | 按信息依赖 DAG 重组文章结构，每段不超过 240 字符 |
| **obsidian-vault** | 模型调用 | 搜索/创建/管理 Matt 的 Obsidian 笔记库，使用 wikilink 和 title-case 命名 |

### `skills/in-progress/` — 9 个（开发中的草稿）

| 技能 | 类型 | 说明 |
|------|------|------|
| **batch-grill-me** | 用户调用 | 一次性质询所有前沿问题，每轮同时问多条 |
| **claude-handoff** | 用户调用 | 把对话交接给后台 Agent（`claude --bg --name`） |
| **loop-me** | 用户调用 | 找到用户生活中的循环模式，spec 给实现者 Agent |
| **setup-ts-deep-modules** | 用户调用 | 给 TS 仓库配置 dependency-cruiser，每个 package 作为深模块 |
| **to-questionnaire** | 用户调用 | 把无法回答的决策做成 Markdown 问卷，让别人异步填写 |
| **wizard** | 用户调用 | 从模板生成交互式 bash 向导，引导人类逐步操作 |
| **writing-beats** | 用户调用 | 写作阶段：把素材编排成选你自己的冒险风格旅程 |
| **writing-fragments** | 用户调用 | 写作阶段：从质询中挖出原始片段，以 `---` 分隔 |
| **writing-shape** | 用户调用 | 写作阶段：逐段打磨文章，带对话式 pushback |

### `skills/deprecated/` — 4 个（已废弃）

| 技能 | 类型 | 说明 |
|------|------|------|
| **design-an-interface** | 模型调用 | 用 3+ 种不同约束并行生成接口设计方案，对比选出最优 |
| **qa** | 模型调用 | 交互式 QA 会话：用户口述 Bug，Agent 后台探索代码库并提交 issue |
| **request-refactor-plan** | 模型调用 | 通过用户访谈创建重构计划，拆成小 commit |
| **ubiquitous-language** | 用户调用 | 从对话中提取 DDD 通用语言词汇表 |

---

> **总计**：41 个技能（22 个推广 + 19 个非推广），其中 24 个用户调用，17 个模型调用

---

## 安装方式

### 方式一：skills.sh 安装器（推荐用于自定义）
```bash
npx skills@latest add mattpocock/skills
```
- 把技能文件复制到你的项目，可以自由修改
- 选择安装哪些技能和哪些 Agent

### 方式二：Claude Code 插件（推荐用于自动更新）
```
/plugin marketplace add mattpocock/skills
/plugin install mattpocock-skills@mattpocock
```
- 只读安装，作者更新时自动同步
- 不能自己改，但始终是最新版本

---

## 推荐使用顺序

1. `/setup-matt-pocock-skills` — 一次性配置
2. `/grill-with-docs` — 每次改动前，对齐需求 + 建立共享语言
3. `/to-spec` → `/to-tickets` → `/implement` — 完整的开发流水线
4. `/improve-codebase-architecture` — 每隔几天运行一次，防止代码腐化
5. 遇到 Bug 时让 Agent 用 `/diagnosing-bugs`
