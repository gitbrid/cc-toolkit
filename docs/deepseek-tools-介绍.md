# DeepSeek 工具集

> 2026-08-09 收录。目标：给 Codex、Cursor、Claude Code 等环境补齐 DeepSeek 的审查、MCP 调用与视觉能力，并按项目实际场景部署。

## 收录清单

### 1. DeepSeekHelper（Codex 插件，已安装）

- 仓库：`UrgencyWu/deepseekhelper`，版本 0.3.4
- 本地源码：`D:\program\CC 工具库\plugins\deepseekhelper`
- 市场：`cc-toolbox`，Codex 插件 ID：`deepseekhelper@cc-toolbox`
- 能力：任务委托、独立审查、方案讨论、结论验证、提示词生成、Flash/Pro 自动选型、用量与缓存统计、显式更新
- 配置：`plugins/deepseekhelper/.env`（已写入 `DEEPSEEK_API_KEY`、`DEEPSEEK_BASE_URL`），gitignore 排除，不回显
- 用途：Codex 主模型为 DeepSeek 时，用它做“第二模型”复核和低成本任务分流

### 2. DeepSeek MCP Server（MCP Server，已挂载）

- 仓库：`arikusi/deepseek-mcp-server`，版本 2.2.0
- 本地源码：`D:\program\CC 工具库\mcp\deepseek-mcp-server`
- Codex 全局配置：`~/.codex/config.toml` 中 `[mcp_servers.deepseek]`
- 能力：`deepseek_chat`、`deepseek_fim`、`deepseek_sessions`，支持思考模式、函数调用、JSON Schema 校验、模型回退与成本统计
- 配置：`mcp/deepseek-mcp-server/.env`（已写入 `DEEPSEEK_API_KEY`、`DEEPSEEK_BASE_URL`），gitignore 排除
- 用途：让支持 MCP 的客户端直接调用 DeepSeek，后续可复制同一套配置给 Cursor / Claude Code

### 3. DeepSeek Vision（Codex 插件，已安装，待配视觉 API）

- 仓库：`wssfk12138/deepseek-vision`，版本 1.3.2
- 本地源码：`D:\program\CC 工具库\plugins\deepseek-vision`
- 市场：`cc-toolbox`，Codex 插件 ID：`deepseek-vision@cc-toolbox`
- 能力：图片分析、OCR、扫描 PDF 转 DOCX、表格提取、国际音标核对、DOCX 渲染质检
- 配置：插件根目录 `.env` 已生成模板，需要用户填写 `MCP_OCR_BASE_URL`、`MCP_OCR_API_KEY`、`MCP_OCR_MODEL`；依赖 `uv`（已安装到 bundled Python Scripts）
- 用途：给纯文本 DeepSeek 补“眼睛”，服务伴学拍照答疑、资料整理 OCR、论文扫描件处理

## 部署映射

| 目标 | 部署内容 | 状态 |
|---|---|---|
| Codex 全局 | DeepSeekHelper 插件 + DeepSeek Vision 插件 + DeepSeek MCP Server | 已配置 |
| CC 3 for b站视频阅读器 | 模型改为 `deepseek-v4-flash`，保留官方 Base URL | 已更新 |
| CC 1 for study(伴学) | 通过 Codex 全局 Vision / Helper 间接受益 | 待实际使用验证 |
| CC 1 for study1(论文) | 通过 Codex 全局 Vision / Helper 间接受益 | 待实际使用验证 |
| CC 1 for study2(整理) | 通过 Codex 全局 Vision / Helper 间接受益 | 待实际使用验证 |

## 未收录（仅参考）

- `SALIPE/rag-obsidian`：CLI RAG，与已有 rag-mcp + ChromaDB 重复，暂不部署
- `golddream-y/obsidian-ratel`：Obsidian 语义检索插件，等有明确 vault 检索需求再评估
- `Yima-Gu/obsidian-lecture-lens`：讲义/白板转笔记，等伴学界面需要时再评估

## 安全说明

- 所有 API Key 只写进各项目 `.env`，均已加入 gitignore，不进入版本库
- DeepSeek Vision 会把图片发送到用户配置的视觉 API，敏感图片谨慎处理
- Codex 配置中的 MCP 命令指向本地源码，不包含密钥
