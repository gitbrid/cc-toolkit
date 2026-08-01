# cexll/myclaude — 技能详细介绍

> 来源：https://github.com/cexll/myclaude  
> 本地路径：`D:\program\CC 工具库\skills\cexll-skills\`  
> 导入自：cc-switch 远程安装（2026-08-01）

---

## 项目概述

cexll 的个人 Claude 技能合集，偏**自动化与工作流**——浏览器自动化、多 Agent 编排、产品需求、测试用例。质量参差：一部分是自研的完整工作流，一部分**依赖外部 CLI（codeagent-wrapper）**，未安装对应工具时用不上。

---

## 技能列表（11 个）

### 推荐使用
1. **browser** ⭐ — 浏览器自动化（Chrome DevTools Protocol），导航、执行 JS、截图、选 DOM
2. **do** ⭐ — 结构化功能开发工作流（`/do` 命令触发，5 阶段：理解→澄清→设计→实现→完成）
3. **harness** ⭐ — 多会话自治 Agent 工作（进度检查点、失败恢复、任务依赖管理）
4. **skill-install** ⭐ — 从 GitHub 安装技能，带自动安全扫描
5. **product-requirements** — 交互式产品负责人，需求收集 → PRD 生成
6. **test-cases** — 从 PRD 生成结构化测试用例
7. **prototype-prompt-generator** — 生成 UI/UX 原型设计的详细结构化 prompt
8. **omo** — 多 Agent 编排（`/omo` 触发）：代码分析 / 缺陷排查 / 修复计划 / 实现

### 依赖外部 CLI（未装则无意义）
9. **codeagent** — 调用 `codeagent-wrapper` 执行多后端 AI 任务（需安装该 CLI）
10. **dev** — 端到端开发工作流，强制 90% 测试覆盖，但所有代码变更走 `codeagent-wrapper`（需安装该 CLI）

### 小众方法论
11. **sparv** — SPARV 工作流（Specify→Plan→Act→Review→Vault），10 分 spec 门槛 + 统一日志

---

## 使用建议

- **codeagent / dev 依赖 `codeagent-wrapper` CLI**：若未安装，可放心从 cc-switch 删除或不用
- **omo / sparv / harness**：看个人是否常用多 Agent 编排和长任务自治
