# MCP 收藏库

本子库收集和推荐好用的 **MCP（Model Context Protocol）服务器**，与 `skills/` 子库对应。其他项目可从这里复制 MCP 配置，或参考推荐清单挑选适合自己场景的 MCP。

> **规则**：每次新增 MCP 相关内容后，更新本文档和 `docs/README.md` 的索引。

---

## 一、官方全家桶（Anthropic 出品，质量最稳）

| MCP | 用途 |
|-----|------|
| **GitHub** | 操作仓库、PR、Issue、搜索代码，日常最常用 |
| **Filesystem** | 本地文件读写，比默认工具更灵活 |
| **Google Drive / Slack / Notion** | 办公协作、知识库接入 |
| **Fetch** | 抓取网页内容转成结构化文本 |
| **Sequential Thinking** | 深度多步思考，处理复杂问题 |
| **Memory** | 知识图谱长期记忆，跨会话记得用户偏好 |

## 二、开发者高频之选（社区口碑好）

| MCP | 用途 |
|-----|------|
| **Playwright** | 浏览器自动化，测试 / 截图 / 抓取动态网页 |
| **Context7** | 实时查任意库的官方文档，防止训练数据过时 |
| **Tavily / Exa** | AI 优化的网络搜索，比普通搜索更懂意图 |
| **PostgreSQL / SQLite / MySQL / MongoDB** | 直接连数据库做查询和建模 |
| **Docker / Kubernetes** | 容器与集群运维操作 |
| **Sentry** | 错误监控，让 Agent 直接读报错并定位 |

## 三、按场景速查

| 我想... | 用哪个 |
|--------|-------|
| 找一个库的最新文档 | Context7 |
| 让 Agent 直接操作 GitHub | GitHub MCP |
| 自动化浏览器测试 / 抓取 | Playwright |
| 长期记住用户偏好 | Memory |
| 连上项目数据库 | PostgreSQL / SQLite MCP |
| 网页内容抓取成文本 | Fetch |
| 精确的语义搜索 | Tavily / Exa |
| 深度分析复杂问题 | Sequential Thinking |
| 对本地 PDF/文档库做语义检索 | rag-mcp + llama.cpp（见下方「本地 RAG」） |
| 在 MCP 客户端里直接调用 DeepSeek | deepseek-mcp-server（见下方「DeepSeek MCP Server」） |
| 大 PDF 精准读取 / OCR / 表格提取 | pdf-mcp（见下方「pdf-mcp」） |

## 四、pdf-mcp（2026-08-09 收录）

**本地路径**：`D:\program\CC 工具库\mcp\pdf-mcp`

对论文、教材、财报等大 PDF 做“外科手术式”读取：混合检索、分页读取、表格/图片提取、扫描版 OCR、SQLite 缓存。

Codex 全局配置已挂载：

```toml
[mcp_servers.pdf-mcp]
type = "stdio"
command = "C:\\Users\\subrid\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\Scripts\\uv.exe"
args = ["tool", "run", "pdf-mcp"]
```

详细说明见 [docs/pdf-mcp-介绍.md](../docs/pdf-mcp-介绍.md)。

## 五、RAG MCP 备选（2026-08-09 收录）

| 方案 | 位置 | 用途 |
|---|---|---|
| rag-mcp（实战在用） | `mcp/rag-mcp` | llama.cpp + bge-m3 + ChromaDB，中文教材语义检索 |
| rag-mcp-server | `mcp/rag-mcp-server` | Rubrum95 备选，OCR + 页码引用，配置见 [docs/rag-mcp-server-介绍.md](../docs/rag-mcp-server-介绍.md) |

## 六、DeepSeek MCP Server（2026-08-09 收录）

**本地路径**：`D:\program\CC 工具库\mcp\deepseek-mcp-server`

| 工具 | 用途 |
|---|---|
| `deepseek_chat` | 对话、思考模式、函数调用、JSON Schema 校验 |
| `deepseek_fim` | 代码补全（前缀/后缀填空） |
| `deepseek_sessions` | 多轮会话管理（list / clear / delete） |

Codex 全局配置（`~/.codex/config.toml`）：

```toml
[mcp_servers.deepseek]
type = "stdio"
command = "node"
args = ["--env-file=D:/program/CC 工具库/mcp/deepseek-mcp-server/.env", "D:/program/CC 工具库/mcp/deepseek-mcp-server/dist/index.js"]
```

`.env` 已写入 `DEEPSEEK_API_KEY` 与 `DEEPSEEK_BASE_URL`，被 gitignore 排除。Cursor / Claude Code 接入时复制该 server 配置即可。

## 七、如何在 Claude Code 中安装

### 方式一：交互式（推荐）

在 Claude Code 中运行 `/mcp`，按提示选择添加 MCP 服务器并配置。

### 方式二：编辑配置文件

在 `~/.claude.json`（全局）或项目的 `.mcp.json`（项目级）中添加：

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "<你的 token>" }
    }
  }
}
```

## 八、本机已启用的 MCP

以下 MCP 已在本机 Claude Code 会话中启用，可在当前环境中直接使用：

- **context7** — 库文档查询
- **memory** — 知识图谱记忆
- **sequential-thinking** — 深度思考
- **playwright** — 浏览器自动化

> **Playwright 配置要点**：本机未装 Playwright 自带浏览器时，`@playwright/mcp` 启动会自动下载浏览器导致握手很慢/超时。解决：在配置的 `env` 中设置 `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH` 指向系统已装的 Chrome（如 `C:/Program Files/Google/Chrome/Application/chrome.exe`），即可跳过下载、秒级启动。
>
> **协议提示（2026-08 实测）**：新版 MCP SDK（≥1.30）的 stdio 协议已改为 **JSON Lines**（每条消息一行 JSON，`\n` 分隔），不再使用旧的 `Content-Length` 帧头。手动测试 MCP 服务器时注意此变化。

### 踩坑记录（2026-08-01 实测）

- **`@modelcontextprotocol/server-time` 已从 npm 下架（404）**：官方 time 服务器不再发布 JS 包，照抄旧配置会连接失败。time 功能可由 Claude Code 自带的时间上下文替代，无需额外 MCP。
- **npm 上的 `mcp-server-fetch` 是安全研究蜜罐（canary）包，切勿用于生产**：该包安装/执行时只向外发送最小遥测，不提供任何 MCP 功能——npx 包名混淆的典型案例。官方 fetch JS 版 `@modelcontextprotocol/server-fetch` 也已下架；仅 PyPI 官方版 `mcp-server-fetch` 可通过 `uvx` 使用（需安装 uv）。
- 排查结论：本机 4 个 MCP（context7 / memory / sequential-thinking / playwright）全部可用。

---

## 九、本地 RAG（知识库向量检索，数据不出本机）

对本地 PDF / Markdown / 代码库做语义检索，适合**大量资料无法整本进上下文**的场景（如几十本教材的书库）。

| 方案 | 说明 |
|------|------|
| **rag-mcp + llama.cpp**（实战验证 ✅） | 详细介绍见 [docs/rag-mcp-介绍.md](../docs/rag-mcp-介绍.md)。索引切块 → bge-m3 本地向量化 → ChromaDB 持久化 → `search_docs` 语义检索。用户偏好直接 llama.cpp（无 GUI），已改造客户端走 OpenAI 兼容 `/v1/embeddings` |
| Rubrum95/rag-mcp-server | 强备选：自带多语言模型 + OCR + 页号引用，Python 3.10+，中文/扫描版场景可切换 |
| eztakesin/doc-indexer-mcp | Rust + Qdrant + Voyage Key，重、默认需 Key，缓选 |

**快速上手**：
```bash
pip install uv
git clone --depth 1 https://github.com/Kamalesh-Kavin/rag-mcp D:/program/tools/rag-mcp
cd D:/program/tools/rag-mcp && cp .env.example .env && uv sync
# embedding 后端（llama.cpp，端口 8080）
llama-server.exe -m bge-m3.gguf --embedding --pooling cls --host 127.0.0.1 --port 8080
```
项目 `.mcp.json` 中加 `rag` server（uv 用完整路径，env 里配 `OLLAMA_BASE_URL=http://127.0.0.1:8080`、`OLLAMA_EMBED_MODEL=bge-m3`、`CHROMA_PERSIST_DIR`）。

> **要点**：① embedding 用 bge-m3（1024 维多语言，中文好）；② 中文教材常是扫描版需先 OCR；③ 数学公式靠 OCR 会乱码，公式页让 Claude 读图；④ llama.cpp 与 Ollama 的 bge-m3 向量一致（余弦=1.0），索引可通用。

---

## 收藏新 MCP 的流程

1. 找到目标 MCP 项目（GitHub 或官方文档）
2. 在 `mcp/` 下新建 `<项目名>/` 子目录，保存其安装配置、README 要点
3. 在本文档的对应章节补充条目
4. 更新 `docs/README.md` 的索引

## 更新日志

| 日期 | 变更 |
|------|------|
| 2026-08-01 | 初始创建，收录官方全家桶 + 社区高频 MCP 推荐 |
| 2026-08-01 | 本机配置 Playwright MCP（@playwright/mcp 0.0.78），用系统 Chrome 跳过浏览器下载 |
| 2026-08-01 | 排障：移除 time（官方包 npm 404）与 fetch（npm 同名包为蜜罐），本机收敛为 4 个可用 MCP |
| 2026-08-01 | 新增「本地 RAG」：rag-mcp + llama.cpp + bge-m3 + ChromaDB（伴学项目实战收录），详见 docs/rag-mcp-介绍.md |
| 2026-08-09 | 新增「DeepSeek MCP Server」：arikusi/deepseek-mcp-server v2.2.0，已挂载到 Codex 全局 |
| 2026-08-09 | 新增「pdf-mcp」与 RAG MCP 备选：pdf-mcp 已挂载 Codex 全局，rag-mcp/rag-mcp-server 收录源码 |
