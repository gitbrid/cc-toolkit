# 2026-08-09 工具库第二批收录与部署

## 新增收录

- `mcp/rag-mcp`：Kamalesh-Kavin/rag-mcp 源码归档（本地运行副本的 git HEAD）
- `mcp/rag-mcp-server`：Rubrum95/rag-mcp-server，RAG MCP 备选，OCR + 页码引用
- `mcp/pdf-mcp`：jztan/pdf-mcp v2.1.0，大 PDF 精准读取 MCP，已挂载 Codex 全局
- `skills/the-learning-skill`：toddward/the-learning-skill，学习教练 Agent Skill
- `plugins/obsidian-deepseek-note-helper`：Obsidian 侧边栏 DeepSeek 助手，已编译

## 配置结果

- Codex 全局新增 `[mcp_servers.pdf-mcp]`，用 uv tool run 运行，依赖已预下载
- the-learning-skill 复制到伴学 `.claude/skills` 与 `.agents/skills`
- Obsidian 插件 release 产物：`plugins/obsidian-deepseek-note-helper/release/`
- Obsidian 插件已安装到 `D:\program\Codex\Codex\.obsidian\plugins\deepseek-note-helper` 与 `D:\Obsidian\b站视频文稿\.obsidian\plugins\deepseek-note-helper`
- 追加安装：`D:\Albert's vault\.obsidian\plugins\deepseek-note-helper` 也已启用并配置
- 已写入三个 vault 的 `community-plugins.json` 与插件 `data.json`（官方 API、`deepseek-v4-flash`）

## 待用户操作

- 重启 Obsidian 并重载 vault；若受限模式开启，先关闭再启用 deepseek-note-helper
- 需要扫描版 PDF OCR 时，在 Windows 安装 Tesseract 后启用 pdf-mcp 的 OCR 能力
- rag-mcp-server 作为备选保留，不默认启用
