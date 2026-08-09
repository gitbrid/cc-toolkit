# toddward/the-learning-skill

> 2026-08-09 收录。一个可移植的 Agent Skill，把 Claude/Codex 变成“学习教练”：主动回忆、费曼、第一性原理、间隔重复、刻意练习。

## 本地位置

- 源码：`D:\program\CC 工具库\skills\the-learning-skill`
- 版本：main

## 能力

- 每次学习生成独立工作目录：`notes.md`、`flashcards.html`、`quiz.html`、`anki.tsv`、`schedule.md`、`cheatsheet.pdf`
- 支持“教教我 X / 帮我准备考试 / 给我做闪卡 / 我老忘 X”等触发语
- 与 Agent Skills 规范兼容，Claude Code、Codex、Gemini CLI 均可加载

## 安装到项目

已复制到伴学项目：

```text
D:\program\CC 1 for study(伴学)\.claude\skills\the-learning-skill
D:\program\CC 1 for study(伴学)\.agents\skills\the-learning-skill
```

其他项目手动复制：

```powershell
Copy-Item -Recurse 'D:\program\CC 工具库\skills\the-learning-skill\the-learning-skill' '目标项目\.claude\skills\the-learning-skill'
```

## 与 teacher-enhanced 的关系

伴学项目已有的 `teacher-enhanced` 是本地适配版（学情诊断/刻意练习/快速回顾）；本仓库作为上游完整实现保留，可对照升级，不重复维护。

## 注意

- 生成 PDF 需要环境支持 reportlab 等脚本依赖
- `stuff_to_learn/` 默认 gitignore，学习产物不进版本库
