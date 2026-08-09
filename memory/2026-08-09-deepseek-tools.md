# 2026-08-09 DeepSeek 工具收录与部署记录

## 决策

- DeepSeekHelper、DeepSeek MCP Server、DeepSeek Vision 三个项目收录进 CC 工具库。
- DeepSeek API 接入采用官方直连，Base URL `https://api.deepseek.com`，复用现有 key，只写入 gitignore 的 `.env`。
- B站视频阅读器模型从 `deepseek-chat` 更新为 `deepseek-v4-flash`。
- 不做重复建设：不克隆 rag-obsidian / obsidian-ratel / lecture-lens，只在 docs 中留参考。

## 部署状态

- Codex 插件市场：`cc-toolbox`，来源 `D:\program\CC 工具库`
- 已安装插件：`deepseekhelper@cc-toolbox`、`deepseek-vision@cc-toolbox`
- 已挂载 MCP：`~/.codex/config.toml` 的 `[mcp_servers.deepseek]`
- DeepSeek Vision 的视觉 API 配置待用户填写（插件根 `.env`）

## 注意

- Vision 插件依赖 `uv`，已安装到 bundled Python Scripts，.mcp.json 使用绝对路径
- 新增插件后需重启 Codex 才能加载 MCP server
- 后续切换 new-api 网关时，只改各 `.env` 的 `DEEPSEEK_BASE_URL` 和 key，无需改代码
