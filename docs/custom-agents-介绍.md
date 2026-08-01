# 自定义 Agent 介绍

> 本地路径：`D:\program\CC 工具库\custom-agents\`  
> 提取自：`CC 3 for b站视频阅读器` 项目

---

## 概述

从实际项目中提取的 4 个中文自定义 Claude Code Agent。这些 Agent 针对 Python 项目的具体需求定制，可以作为模板复用到其他项目。

---

## Agent 列表

### 1. code-reviewer（代码审查专家）
- **模型**：Sonnet
- **文件**：`code-reviewer.md`
- **功能**：Python 代码审查，覆盖 5 个维度：
  - **正确性** — 逻辑错误、边界条件
  - **性能** — 瓶颈、资源泄漏
  - **可维护性** — 代码结构、可读性
  - **安全性** — 注入、敏感信息
  - **健壮性** — 异常处理、错误恢复
- **特色**：包含项目特定检查（API 密钥安全、Bilibili API 速率限制、Whisper 模型管理、Obsidian 文件编码、GUI 线程安全），输出带严重性标注的结构化报告（blocking/important/nit）

### 2. code-guardian（代码质量守门员）
- **模型**：Haiku
- **文件**：`code-guardian.md`
- **语言**：中文
- **功能**：代码提交前自动检查三道防线：
  - 🔴 **红线（安全）** — 无 API Key/Cookie 泄露、无硬编码密钥、gitignore 检查
  - 🟡 **黄线（质量）** — 无裸 except、API 超时/重试配置、无 print 调试
  - 🟢 **绿线（风格）** — 编码声明、docstring、类型提示
- **触发方式**：敏感文件修改时自动触发或用户主动请求

### 3. test-runner（测试运行专家）
- **模型**：Haiku
- **文件**：`test-runner.md`
- **功能**：运行 pytest 测试套件，分析失败原因，区分代码 bug 和测试本身的问题，并修复。覆盖测试命名规范、mock 要求（外部依赖如 Bilibili API、LLM API、faster-whisper）

### 4. project-manager（项目管家）
- **模型**：Haiku
- **文件**：`project-manager.md`
- **语言**：中文
- **功能**：维护 `PROJECT_GOALS.md` 和 `PROJECT_ROADMAP.md`，追踪里程碑进度，识别风险和阻塞任务，排定下一步优先级。理解完整项目架构，针对独立开发者调优

---

## 复用指南

这些 Agent 可以复制到新项目中直接使用，但需要根据新项目的实际情况调整：
1. **code-reviewer** — 把"项目特定检查"部分换成新项目的关注点
2. **code-guardian** — 把敏感文件列表换成新项目的关键文件
3. **test-runner** — 修改 mock 要求中的外部依赖列表
4. **project-manager** — 把模块列表换成新项目的模块
