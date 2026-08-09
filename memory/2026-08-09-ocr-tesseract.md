# 2026-08-09：便携 Tesseract 部署 + 视觉方案决策

- DeepSeek 官方 API（deepseek-v4-flash / v4-pro）实测不支持图片输入（chat/completions 只接受 text content）
- 视觉/OCR 方案：本地便携 Tesseract（免管理员）+ chi_sim/eng/osd，部署在 `D:\program\CC 工具库\tools\tesseract-portable`
- 用户级环境变量已写入：PATH 追加 tesseract 目录；TESSDATA_PREFIX 指向 tessdata
- deepseek-vision 插件新增 `scripts/local_ocr.py` 本地兜底（图片/PDF 均可，PDF 用 pypdfium2 渲染），并更新 image-analysis / pdf-ocr-conversion 两个技能的说明
- pdf-mcp 的 MCP 配置已加 `[mcp_servers.pdf-mcp.env] TESSDATA_PREFIX`
- API key 更新：用户新给的 DeepSeek key 已替换到 deepseek-mcp-server/.env、deepseekhelper/.env（CC 工具库 + cache）、B站阅读器 settings.json、三个 Obsidian vault 的 data.json
- 待办：重启 Codex 后验证 pdf-mcp `server_info` 的 OCR available
