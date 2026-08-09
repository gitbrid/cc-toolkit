# 便携 Tesseract（本地 OCR）

> 2026-08-09 部署。免管理员、免安装的 Windows 便携版 Tesseract，用于扫描 PDF 和图片 OCR，补上 DeepSeek 纯文本模型的“眼睛”。

## 本地位置

- 运行目录：`D:\program\CC 工具库\tools\tesseract-portable`
- 可执行文件：`tesseract.exe`（v4.1.1，x64）
- 语言包：`tessdata\` 内含 `chi_sim` / `eng` / `osd`

## 环境变量（已写入用户级环境）

- `PATH` 已追加 `D:\program\CC 工具库\tools\tesseract-portable`
- `TESSDATA_PREFIX=D:\program\CC 工具库\tools\tesseract-portable\tessdata`
- 新开的 Codex / 终端会话生效；当前已开的会话请重启 Codex

## 为什么用本地 OCR

- DeepSeek 官方 API（deepseek-v4-flash / v4-pro）只接受文本，不支持图片输入
- 本地 OCR 免费、数据不出本机、免管理员安装
- 适用于书页、截图、扫描 PDF；复杂图表、水印、手写建议后续配置多模态视觉 API

## 用法

图片直接识别：

```powershell
& "D:\program\CC 工具库\tools\tesseract-portable\tesseract.exe" "图片.png" stdout -l chi_sim+eng --psm 6
```

PDF 逐页识别（配合 deepseek-vision 插件的 local_ocr.py）：

```powershell
uv tool run --python 3.12 --with pypdfium2 --with pillow python "D:\program\CC 工具库\plugins\deepseek-vision\plugins\deepseek-vision\scripts\local_ocr.py" "扫描书.pdf" --out "OCR结果" --lang chi_sim+eng
```

## 与 pdf-mcp 的关系

- pdf-mcp 的 `pdf_read_pages(ocr=True)` 依赖系统能找到 `tesseract`
- Codex 全局 MCP 配置 `[mcp_servers.pdf-mcp.env]` 已写入 `TESSDATA_PREFIX`
- 重启 Codex 后，`server_info` 中 `extraction.ocr.available` 会变为 true
