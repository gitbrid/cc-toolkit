# rag-mcp — 本地 PDF/文档向量检索 MCP

> **收录日期**：2026-08-01 ｜ **来源**：[Kamalesh-Kavin/rag-mcp](https://github.com/Kamalesh-Kavin/rag-mcp)（MIT）
> **实战项目**：伴学项目（`d:\program\CC 1 for study(伴学)`）——用 Claude 当一对一老师的学习环境，60+ 本 PDF 教材的书库检索。

## 定位

个人知识库 MCP 服务器：把 PDF / Markdown / 文本 / 代码 切成块（chunk）→ 本地 embedding 向量化 → 存入 ChromaDB 持久化 → 语义检索。数据不出本机。

**暴露给 Claude 的工具**：
| 工具 | 说明 |
|------|------|
| `index_document` | 索引一个文件（绝对路径） |
| `search_docs` | 跨全部文档的语义搜索 |
| `list_indexed_docs` | 列出已索引文档 |
| `delete_document` | 删除某文档及其全部块 |
| `doc://{filename}` 资源 | 读取某文档的全部原始块 |

## 架构

```
文件 → read_file()（pypdf 读 PDF / open 读文本）→ chunk_pages()（滑动窗口 1500/200）
     → embed_chunks()（本地 embedding 服务）→ ChromaDB PersistentClient → search_docs()
```

## 评估与选型（2026-08 实测对比）

| 候选 | 栈 | 中文/扫描 | 本地/Key | 结论 |
|------|-----|-----------|---------|------|
| **Kamalesh-Kavin/rag-mcp** | Python≥3.13 + uv，ChromaDB | 中文弱需换多语言模型；扫描版需先 OCR | ✅ 全本地、无 Key | **选用**（纯 Python 最省事） |
| Rubrum95/rag-mcp-server | Python≥3.10，ChromaDB | 自带多语言模型 + OCR + 页号引用 | ✅ 全本地、无 Key | 强备选（中文/扫描不理想时切） |
| eztakesin/doc-indexer-mcp | Rust + Qdrant | 好但需 Voyage Key + 跑 Qdrant + 编译 | ❌ 默认需 Key | 缓选 |
| cluster2600/zvec-mcp | Python + zvec | 一般 | ✅ 本地 | 备选；memory 功能与 memory MCP 重叠 |

## 关键决策：embedding 后端用 llama.cpp（不用 Ollama）

- **方案**：`llama-server.exe`（llama.cpp）+ bge-m3 GGUF，`--embedding --pooling cls`，端口 8080，OpenAI 兼容 `/v1/embeddings`
- **为什么**：rag-mcp 默认对接 Ollama 的 `/api/embeddings`；用户偏好直接 llama.cpp（最轻量、无 GUI）。已改造 `ollama_client.py` 指向 `/v1/embeddings` + `/health` 健康检查
- **关键验证**：llama.cpp 与 Ollama 对同一文本的 bge-m3 向量**余弦 = 1.000000**（同一 GGUF 权重，确定性推理），索引可通用，换后端无需重建
- **bge-m3**：1024 维，多语言（中文/中英混排好），CLS pooling，比默认 nomic-embed-text（768 维）更适合中文
- **模型获取**：`ollama pull bge-m3` 后从 Ollama 模型库 blob 提取 GGUF（`C:\Users\subrid\.ollama\models\blobs\sha256-*`，魔数校验 GGUF）；或从 HuggingFace 下 `gpustack/bge-m3-gguf`

## 安装配置

```bash
# 运行副本（不放书库根、不放工具库）
git clone --depth 1 https://github.com/Kamalesh-Kavin/rag-mcp "D:/program/tools/rag-mcp"
cd "D:/program/tools/rag-mcp" && cp .env.example .env
uv sync   # 需 uv（pip install uv），Python ≥3.13

# llama.cpp 启动（D:/program/tools/llama.cpp/start-embedding-server.bat）
llama-server.exe -m models/bge-m3.gguf --embedding --pooling cls --host 127.0.0.1 --port 8080
```

`.env`（rag-mcp）：
```
OLLAMA_BASE_URL=http://127.0.0.1:8080     # llama-server，而非 Ollama
OLLAMA_EMBED_MODEL=bge-m3
CHROMA_PERSIST_DIR=D:/.../检索/chromadb
CHUNK_SIZE=1500
CHUNK_OVERLAP=200                          # 调大 chunk 减少数学公式被切碎
```

项目 `.mcp.json` 片段（uv 用完整路径，避免 PATH 找不到）：
```json
{
  "mcpServers": {
    "rag": {
      "command": "C:/Users/<user>/AppData/Local/Programs/Python/Python314/Scripts/uv.exe",
      "args": ["--directory", "D:/program/tools/rag-mcp", "run", "rag-mcp"],
      "env": {
        "OLLAMA_BASE_URL": "http://127.0.0.1:8080",
        "OLLAMA_EMBED_MODEL": "bge-m3",
        "CHROMA_PERSIST_DIR": "D:/.../检索/chromadb",
        "CHUNK_SIZE": "1500",
        "CHUNK_OVERLAP": "200"
      }
    }
  }
}
```

## 中文 PDF 检索的坑与对策（实测）

| 坑 | 对策 |
|----|------|
| 中文 embedding 弱 | bge-m3（1024 维多语言）；中文查询对英文原著也能语义命中 |
| **中文教材 PDF 常为扫描版**（pypdf 提取 0 字符） | 先测可提取性；扫描版走 OCR 镜像再索引 |
| **数学公式 OCR 不可靠**（乱码） | 公式/图形页直接让 Claude 用 Read 读 PDF 页图，OCR 只用于文字为主的页 |
| OCR 中文路径 bug（OpenCV） | PIL/numpy 读图绕开（见 `docs/../../` 项目记忆） |
| 换 embedding 模型后向量混库 | 换模型即清空 ChromaDB 重建集合 |
| 新模型 API 端点不同（Ollama vs llama.cpp） | 改造 `ollama_client.py`：`/v1/embeddings`（OpenAI 兼容）+ `/health` |

## 实测结论

- 全链路跑通：索引英文原著《In Search of Memory》780 块，**中文查询**「什么是长期记忆」「海马体在记忆中的作用」命中相关段落并带**页码**
- 索引速度：CPU 嵌入约 780 块耗时 10+ 分钟（一次性，可接受）
- 参考：`D:\program\CC 工具库\skills\anthropics-skills\pdf\`（PDF 读取/OCR 脚本）配套使用
