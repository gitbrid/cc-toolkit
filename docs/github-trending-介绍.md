# GitHub 每周热点收集（2026-08-09 上线）

自动收集 GitHub 热点项目并归档为 Obsidian 可直接打开的 Markdown 库。归档根目录：`D:\program\CC 工具库\github-trending\`。

## 使用方式

用 Obsidian 打开 `D:\program\CC 工具库\github-trending\` 文件夹即可。每个自然周一个子文件夹，命名格式 `YYYY MM.DD-MM.DD`（例如 `2026 01.05-01.11`），根目录 `README.md` 是总索引。

每个周文件夹包含：

- `index.md`：本周汇总与榜单链接
- `周榜-新建-star.md`：周期内新建仓库按 Star 数排序，Top 10-15
- `周榜-trending.md`：GitHub 官方 Trending 周榜，Top 10-15
- `周榜-star增速.md`：本周 Star 增速榜，Top 10-15（从 2026-08-10 所在周开始积累快照）
- `月榜-YYYY-MM.md`：该周所属自然月的月榜，Top 10-15
- `raw-data.json`：原始抓取数据

## 榜单口径

| 口径 | 说明 | 历史可回溯 |
|------|------|-----------|
| 新建 Star Top | GitHub Search API，按周期内创建时间过滤，按 Star 排序 | 是 |
| 官方 Trending | 抓取 GitHub Trending 页面 | 否，仅当前状态 |
| Star 增速 | 每周保存仓库 Star 快照，对比上周得出增量 | 否，从 2026-08-10 开始积累 |

历史补录（2026-01-01 至 2026-08-09，共 32 周）已全部使用「新建 Star Top」口径生成。

## 命令

```powershell
$PY = "C:\Users\subrid\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

# 生成指定周（传该周周一日期）
& $PY "D:\program\CC 工具库\tools\github-trending\collect.py" --week 2026-08-10

# 生成指定月
& $PY "D:\program\CC 工具库\tools\github-trending\collect.py" --month 2026-08

# 历史补录
& $PY "D:\program\CC 工具库\tools\github-trending\collect.py" --backfill --start 2026-01-01 --end 2026-08-09 --max 15
```

可选参数：`--max` 控制榜单最大数量（默认 15）、`--top` 控制基准数量（默认 10）、`--token` 传入 GitHub Token（也可用环境变量 `GITHUB_TOKEN`）、`--with-readme` 抓取 README 摘要（会增加 API 请求，历史补录默认关闭以规避匿名限速）。

## 每周自动化

一键脚本：

- `D:\program\CC 工具库\tools\github-trending\run-weekly.bat`
- `D:\program\CC 工具库\tools\github-trending\run-weekly.ps1`

推荐每周一 09:00 运行一次，自动生成上一周的报告。配置方式任选其一：

- Codex 应用内创建每周自动任务：每周一 09:00 运行 `D:\program\CC 工具库\tools\github-trending\run-weekly.bat`。
- Windows 任务计划程序：新建每周任务，操作指向 `run-weekly.bat`，时间为每周一 09:00。

每周任务生成后，可用 Codex 对 `raw-data.json` 润色项目介绍与「你可能用到」推荐，再提交归档。

## 脚本结构

`tools\github-trending\`：

| 文件 | 职责 |
|------|------|
| `collect.py` | CLI 入口与流程串联 |
| `dates.py` | 周/月日期计算 |
| `github_api.py` | GitHub Search API、仓库信息、README 抓取，限速重试 |
| `trending_parser.py` | GitHub Trending 页面解析 |
| `snapshot.py` | Star 快照持久化与增量计算 |
| `recommend.py` | 「你可能用到」推荐理由规则 |
| `report.py` | Markdown 报告与 Obsidian 归档生成 |

测试：`tools\github-trending\tests\`，用 Python 标准库 `unittest`。
