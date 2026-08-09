# Rubrum95/rag-mcp-server

> 2026-08-09 收录。一个给 Claude Code 等 MCP 客户端提供 PDF/代码/文档语义检索的 RAG MCP Server，与已有 `rag-mcp` 互为备选。

## 本地位置

- 源码：`D:\program\CC 工具库\mcp\rag-mcp-server`
- 版本：0.1.0（master）

## 能力

- 索引 PDF、代码、Markdown、Office 文档
- 语义检索后返回原文片段 + 页码引用
- 增量更新索引，只处理新增/变更文件
- 可选 Tesseract OCR，支持扫描版 PDF
- 默认 multilingual embedding 模型，西语/英语效果好，中文场景建议换 `config.yaml` 里的 embedding 模型

## 安装与配置

```powershell
cd D:\program\CC 工具库\mcp\rag-mcp-server
# 建议用 uv 或 venv 安装
py -m pip install .
```

Claude Code 配置：

```json
{
  "mcpServers": {
    "rag": {
      "command": "rag-mcp-server"
    }
  }
}
```

配置文件：复制 `config.yaml` 到 `~/.rag-mcp-server/config.yaml` 后调整 `embedding_model`、`chunk_size`、`top_k`、`ocr_languages`。

## 与现有 rag-mcp 的关系

伴学项目目前用的是 `Kamalesh-Kavin/rag-mcp`（本地 llama.cpp + bge-m3 + ChromaDB，中文效果好）。本仓库作为备选，若需要 OCR + 页码引用更完整的方案再切换。

## 注意

- 首次运行会下载约 500MB embedding 模型
- OCR 需要系统安装 Tesseract
- 中文扫描版仍建议先用 OCR 再索引
