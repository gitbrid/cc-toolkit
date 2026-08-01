# Skills 工具箱引用模板

> **用法**：把下面这段内容复制到新项目的 `CLAUDE.md` 中，即可让 Agent 自动从中央工具箱获取技能。

---

## Skills 工具箱

本项目使用位于 `D:\program\CC 工具库` 的中央 Skills 工具箱。

### 可用技能

先去 `D:\program\CC 工具库\docs\README.md` 查看完整列表。以下是常用速查：

| 需求 | 工具箱来源 | 技能 |
|------|-----------|------|
| 需求对齐，开工前盘清楚 | mattpocock/skills | `/grill-me` 或 `/grill-with-docs` |
| 写 spec 并拆成任务 | mattpocock/skills | `/to-spec` → `/to-tickets` → `/implement` |
| 修 Bug | mattpocock/skills | `/diagnosing-bugs` |
| 代码审查 | mattpocock/skills | `/code-review` |
| Python 测试 | wshobson-skills | `python-testing-patterns` |
| Python 调试 | wshobson-skills | `debugging-strategies` |
| Python 性能优化 | wshobson-skills | `python-performance-optimization` |
| 前端/UI 设计 | anthropics-skills | `frontend-design` |
| 用名人视角分析问题 | nuwa-skill | 选择对应人物 |
| 发现更多技能 | anthropics-skills | `find-skills` |

### 安装技能

从工具箱复制到本项目的 `.claude/skills/` 或 `.agents/skills/`：

```bash
# 示例：安装 python-testing-patterns
cp -r "D:/program/CC 工具库/skills/wshobson-skills/python-testing-patterns" \
      ".claude/skills/python-testing-patterns"
```

### 自定义 Agent

工具箱中有 4 个经过实战验证的中文 Agent 模板，位于 `D:\program\CC 工具库\skills\custom-agents\`。直接复制到本项目的 `.claude/agents/` 目录，并根据项目情况定制（把文件中的项目特定检查项换成自己的）。
