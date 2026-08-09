# jztan/pdf-mcp

> 2026-08-09 收录。面向 AI Agent 的“外科手术式”PDF 访问 MCP，适合论文、教材、财报等大 PDF，避免整本塞进上下文。

## 本地位置

- 源码：`D:\program\CC 工具库\mcp\pdf-mcp`
- 版本：2.1.0（master）

## 能力

- 混合检索：BM25 关键词 + 语义向量，RRF 融合
- 分页/分节读取，只把需要的页交给模型
- 表格、图片、目录结构化提取
- 扫描版 OCR（Tesseract，按页并行）
- 中文/日文/韩文竖排与多栏阅读顺序
- SQLite 缓存，重复读取秒回
- 文件夹级 corpus 预热与跨文档搜索
- 隐藏文字/水印检测，防止把不可见内容当正文

## 安装方式

推荐直接用 uv 运行，不污染系统 Python：

```powershell
# 用 CC 工具库已装好的 uv
C:\Users\subrid\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\Scripts\uv.exe tool run pdf-mcp --help
```

也可以源码安装：

```powershell
cd D:\program\CC 工具库\mcp\pdf-mcp
py -m pip install .
```

多栏 PDF 增强：

```powershell
py -m pip install "pdf-mcp[multicolumn]"
```

## Codex 全局配置

`~/.codex/config.toml` 已增加：

```toml
[mcp_servers.pdf-mcp]
type = "stdio"
command = "C:\\Users\\subrid\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\Scripts\\uv.exe"
args = ["tool", "run", "pdf-mcp"]
```

## 适用场景

- 论文阅读器：先 `pdf_info` 再看关键页
- 伴学书库：中文扫描版教材 OCR 后按页检索
- 审计报告/作业：几十页 PDF 快速定位段落

## 注意

- 首次运行会下载 fastembed 语义模型（约 67MB）与 Python 依赖
- OCR 使用免管理员便携 Tesseract：`D:\program\CC 工具库\tools\tesseract-portable`（含 chi_sim/eng/osd），已写入用户 PATH 与 TESSDATA_PREFIX，Codex 的 `[mcp_servers.pdf-mcp.env]` 也已配置；重启 Codex 后生效
- Intel macOS Python 3.14+ 无 onnxruntime wheel，需用 Python <= 3.13
