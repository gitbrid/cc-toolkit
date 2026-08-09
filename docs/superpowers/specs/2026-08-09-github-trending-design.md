# GitHub 每周热点收集 设计文档

日期：2026-08-09
状态：已获用户确认，待实施

## 1. 目标

在本项目内建立一个可被 Obsidian 直接打开的 GitHub 热点归档库，实现：

- 每周自动生成「周榜」与「月榜」报告。
- 三种榜单口径：周期内新建仓库 star Top、GitHub 官方 Trending、star 增速。
- 从 2026-01-01 补录历史榜单，历史部分使用可回溯的口径 1。
- 每个项目提供完整介绍与「你可能用到」推荐理由，不只给一行描述。

## 2. 归档结构

Obsidian 库根目录：`github-trending/`（用户之后用 Obsidian 打开此文件夹）。

```
github-trending/
├── README.md
├── 2026 01.01-01.04/
│   ├── index.md
│   ├── 周榜-新建-star.md
│   ├── 月榜-2026-01.md
│   └── raw-data.json
├── 2026 01.05-01.11/
│   ├── index.md
│   ├── 周榜-新建-star.md
│   ├── 周榜-trending.md
│   ├── 周榜-star增速.md
│   ├── 月榜-2026-01.md
│   └── raw-data.json
└── ...
```

### 2.1 周文件夹命名

- 格式：`YYYY MM.DD-MM.DD`，例如 `2026 01.05-01.11`。
- 周定义：周一至周日。
- 补录起点 2026-01-01 落在周四，第一个文件夹为 `2026 01.01-01.04`，之后均为完整自然周。
- 当前周（2026-08-09 所在周）为 `2026 08.03-08.09`。

### 2.2 周文件夹内容

- `index.md`：本周汇总，包含三个榜单链接、生成时间、数据口径说明。
- `周榜-新建-star.md`：口径 1，默认 10 个，最多 15 个。
- `周榜-trending.md`：口径 2，默认 10 个，最多 15 个；仅当前/未来周可生成。
- `周榜-star增速.md`：口径 3，默认 10 个，最多 15 个；从 2026-08-10 所在周开始积累快照，第二周起有完整榜单。
- `月榜-YYYY-MM.md`：该周所属自然月的月榜（口径 1），默认 10 个，最多 15 个。
- `raw-data.json`：该周的原始 API/页面数据，供校验和后续增速计算。

## 3. 榜单口径

### 3.1 口径 1：周期内新建仓库，按 star 数排序

- 数据源：GitHub Search API。
- 查询：`created:YYYY-MM-DD..YYYY-MM-DD sort:stars order:desc`。
- 周榜取自然周、月榜取自然月。
- 历史补录与未来周报口径完全一致，可复现。

### 3.2 口径 2：GitHub 官方 Trending

- 数据源：`https://github.com/trending?since=weekly` 与 `?since=monthly`。
- 只能抓取当前页面，历史无法回溯。
- 历史补录文件夹不生成该文件；未来每周生成。

### 3.3 口径 3：star 增速

- 维护一个仓库快照池：`tools/github-trending/data/star_snapshot.json`。
- 每周对池内仓库调用 `GET /repos/{owner}/{repo}` 记录 `stargazers_count`。
- 增速 = 本周 star 数 - 上周 star 数，取 Top 10-15。
- 候选池 = 上期池内仓库 + 本周口径 1 前 50 名。
- 第一周只建立基线，不输出完整增速榜；历史不补。

## 4. 项目介绍与推荐

每个榜单中的项目包含：

- 仓库名、作者、链接、语言、Star 数、Fork 数、创建时间、License、Topics。
- 完整 GitHub description。
- README 核心内容摘要：抓取 README 前 2000 字符并提炼为 3-5 句中文介绍。
- 「你可能用到」：基于 Topics、语言、领域与用户工具库场景（自动化、AI、文档处理、Python、Obsidian、MCP 等）生成推荐理由，说明为什么值得看、适合用在什么场景。

未来每周自动化运行时，Codex 使用原始数据润色介绍与推荐；历史补录由脚本按规则生成完整结构化版本。

## 5. 脚本设计

目录：`tools/github-trending/`

```
tools/github-trending/
├── collect.py            # CLI 入口
├── github_api.py         # Search API / repo 信息 / README 抓取，含限速与重试
├── trending_parser.py    # Trending 页面抓取与 HTML 解析
├── report.py             # Markdown 生成
├── recommend.py          # 推荐理由规则
├── snapshot.py           # star 快照读写
├── data/                 # raw-data、star 快照、历史缓存
└── tests/
    ├── test_weeks.py
    ├── test_report.py
    └── test_trending_parser.py
```

### 5.1 CLI

```bash
# 历史补录
python collect.py --backfill --start 2026-01-01 --end 2026-08-09

# 生成指定周（周一日期）
python collect.py --week 2026-08-03

# 生成指定月
python collect.py --month 2026-08
```

可选参数：`--top 10`、`--max 15`、`--token <GITHUB_TOKEN>`。

### 5.2 限速与错误处理

- 未认证 Search API：10 次/分钟，脚本按请求间隔 7 秒节流。
- 配置 `GITHUB_TOKEN` 后按 30 次/分钟节流。
- 对网络错误、429、5xx 做指数退避重试，最多 3 次。
- 失败周记录到 `data/failed.log`，不阻塞整批补录。

## 6. 自动化

- 默认：Codex 每周一 09:00 自动任务，运行脚本生成上周报告并润色介绍。
- 若当前环境无法创建自动任务，提供 `tools/github-trending/run-weekly.bat` 一键脚本和手动配置说明。

## 7. 测试与验证

- `unittest`：周/月日期计算、Markdown 结构、Trending HTML 解析（使用 fixture）。
- 集成验证：真实调用少量 Search API，确认返回结构与限速生效。
- 文档验证：补录完成后抽查首尾周文件夹，确认文件齐全、链接可点、Obsidian 可打开。

## 8. 文档更新

- 新增 `docs/github-trending-介绍.md`。
- 更新 `docs/README.md` 索引。
- 更新 `AGENTS.md` 目录结构与场景速查表。

## 9. 不在本次范围

- 不接入第三方 star-history 服务。
- 不做网页版可视化仪表盘。
- 不自动推送 GitHub 周报到外部平台（如公众号、Telegram）。
