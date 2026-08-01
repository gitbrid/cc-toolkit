# 杂项技能 — 技能详细介绍

> 来源：https://github.com/hamsterider-m/bilibili-subtitle  
> 本地路径：`D:\program\CC 工具库\skills\misc-skills\`  
> 导入自：cc-switch 远程安装（2026-08-01）

---

## 项目概述

收录零散但有用的单一技能，暂未形成独立合集，统一放在 `misc-skills/`。

---

## 技能列表（1 个）

### bilibili-subtitle
- **来源**：hamsterider-m/bilibili-subtitle
- **功能**：用 BBDown 提取 Bilibili 视频字幕（含 AI 字幕），渲染为 Markdown 文稿 / SRT / VTT，可输出 JSON 供上层技能使用
- **依赖**：`BBDown` + `pixi` 环境（命令走 `pixi run python -m bilibili_subtitle`）
- **场景**：抓取 B站视频字幕做笔记/翻译/分析时
- **注意**：SKILL.md 无 YAML frontmatter，cc-switch 靠目录识别

---

## 使用建议

- 只在做 B站内容相关任务时启用
- 未安装 BBDown / pixi 则技能无效
