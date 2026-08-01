# wshobson/agents — 技能详细介绍

> 来源：https://github.com/wshobson/agents  
> 本地路径：`D:\program\CC 工具库\skills\wshobson-skills\`  
> 提取自：`CC 1 for study(论文)` 项目

---

## 项目概述

wshobson/agents 是一套专注于**代码质量和工程实践**的 Agent Skills 集合。与 mattpocock/skills 侧重工作流不同，wshobson 的技能更聚焦于具体的编码技术：代码审查、调试、性能优化、测试。

---

## 技能列表（4 个）

### 1. code-review-excellence
- **类型**：模型调用
- **功能**：掌握高效代码审查实践——建设性反馈、系统化分析、PR 审查清单、严重级别区分、各语言特定模式。覆盖审查心态、流程阶段（上下文收集→高层审查→逐行审查→总结）、反馈技巧（提问式方法、严重性标注）、Python 和 TypeScript 特定模式、安全检查清单、处理分歧的方法。
- **场景**：审查 PR 时自动参考，或写代码后自查

### 2. debugging-strategies
- **类型**：模型调用
- **功能**：覆盖任何技术栈的系统化调试方法。包含：调试的科学方法、复现检查清单、假设形成、二分调试法、差分调试、跟踪调试、内存泄漏检测。覆盖 JavaScript/TypeScript（Chrome DevTools、VS Code）、Python（pdb、breakpoint、cProfile）、Go（Delve）工具。还有间歇性 Bug、性能问题和生产环境调试的模式。
- **场景**：遇到复杂 Bug 时，配合 mattpocock 的 `/diagnosing-bugs` 使用

### 3. python-performance-optimization
- **类型**：模型调用
- **功能**：用 cProfile、内存分析器等进行 Python 性能分析与优化。覆盖分析类型、优化策略（算法级、缓存、并行化、原生扩展）、常见陷阱。包含详细参考资料。
- **场景**：Python 项目性能调优

### 4. python-testing-patterns
- **类型**：模型调用
- **功能**：pytest 综合测试策略——fixtures、mock、参数化、TDD。覆盖测试类型（单元/集成/功能/性能）、AAA 模式、测试组织、命名规范、重试行为测试、freezegun 时间模拟、标记、覆盖率报告。包含详细参考资料。
- **场景**：Python 项目写测试时自动参考

---

## 与 mattpocock/skills 的关系

两组技能互补：
- **mattpocock/skills** 提供**工作流**（怎么组织开发过程）
- **wshobson/agents** 提供**技术深度**（怎么写好 Python 代码）
