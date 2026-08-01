# obra/superpowers — 技能详细介绍

> 来源：https://github.com/obra/superpowers  
> 本地路径：`D:\program\CC 工具库\superpowers-skills\`  
> 导入自：cc-switch 远程安装（2026-08-01）

---

## 项目概述

Jesse Vincent（obra）维护的工程工作流技能合集，把一套完整的「**设计 → 计划 → 执行 → 审查 → 验证**」开发流程固化为可强制执行的技能。特点是 HARD-GATE（硬性门禁）：没做完设计不写代码、没写完计划不执行、没验证不说完成。与 mattpocock/skills 定位互补——mattpocock 偏工程实践细节，superpowers 偏**流程纪律**。

---

## 技能列表（14 个）

### 流程主线
1. **using-superpowers** ⭐ — 总入口，任何对话开始时建立如何使用本套技能的规则
2. **brainstorming** ⭐ — 创意/功能开发前必须执行：探索意图 → 逐个提问 → 提方案 → 设计文档获批后才允许写代码
3. **writing-plans** ⭐ — 把 spec 转化为多步实现计划
4. **executing-plans** ⭐ — 带审查检查点的计划执行
5. **subagent-driven-development** ⭐ — 用子 Agent 并行执行计划中的独立任务
6. **dispatching-parallel-agents** — 面对 2+ 个无依赖的独立任务时并行派发
7. **test-driven-development** ⭐ — 先写测试再实现
8. **requesting-code-review** — 完成功能/合并前请求审查
9. **receiving-code-review** — 接收审查反馈时的应对纪律（先验证再执行，不盲目同意）
10. **verification-before-completion** ⭐ — 声称"完成/修复"前必须实际运行验证命令，用证据代替断言
11. **systematic-debugging** ⭐ — 调试铁律：先定位根因，禁止症状修复
12. **writing-skills** — 创建/编辑/验证新技能的完整流程

### git 相关
13. **using-git-worktrees** — 用 git worktree 隔离工作区
14. **finishing-a-development-branch** — 功能完成、测试通过后决定如何合并

---

## 使用建议

- **建议全量保留**：这套技能互相依赖（brainstorming 的产物喂给 writing-plans，writing-plans 喂给 executing-plans），建议整套启用
- 与 mattpocock/skills 的 `to-spec`、`to-tickets`、`implement` 有部分流程重叠，可按个人习惯二选一
