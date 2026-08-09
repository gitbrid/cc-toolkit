# GitHub 每周热点收集 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立每周自动生成的 GitHub 热点 Obsidian 归档库，并完成 2026-01-01 至今的历史补录。

**Architecture:** Python 3 标准库脚本负责抓取 GitHub Search API、Trending 页面、README 与 star 快照，规则生成中文介绍和推荐，输出到 `github-trending/` 按周命名的 Obsidian 文件夹。

**Tech Stack:** Python 3（标准库 only）、`unittest`、`urllib`、`html.parser`、GitHub REST API。

## Global Constraints

- 只用 Python 3 标准库，不引入第三方包。
- Python 路径：`C:\Users\subrid\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`，下文用 `$PY` 表示。
- 输出根目录固定为 `D:\program\CC 工具库\github-trending\`。
- 周文件夹命名：`YYYY MM.DD-MM.DD`，周定义周一至周日。
- 历史补录起点：2026-01-01，第一个文件夹 `2026 01.01-01.04`。
- 榜单默认 10 个，最多 15 个。
- 历史补录只生成口径 1（新建 star）与月榜；Trending 与 star 增速仅未来周生成。
- 所有用户可见文案使用简体中文。
- 每个 task 结束时运行测试并提交 git。

---

### Task 1: 日期与周划分模块

**Files:**
- Create: `tools/github-trending/dates.py`
- Test: `tools/github-trending/tests/test_dates.py`
- Create: `tools/github-trending/tests/__init__.py`

**Interfaces:**
- Consumes: 无
- Produces:
  - `week_folder(start: datetime.date, end: datetime.date) -> str`
  - `week_ranges(start: datetime.date, end: datetime.date) -> list[tuple[datetime.date, datetime.date]]`
  - `month_label(d: datetime.date) -> str`
  - `next_week_monday(d: datetime.date) -> datetime.date`

- [ ] **Step 1: 写失败测试**

```python
import datetime
import unittest
from dates import week_folder, week_ranges, month_label, next_week_monday

class TestDates(unittest.TestCase):
    def test_week_folder_full_week(self):
        self.assertEqual(week_folder(datetime.date(2026, 1, 5), datetime.date(2026, 1, 11)), "2026 01.05-01.11")

    def test_week_folder_partial_first_week(self):
        self.assertEqual(week_folder(datetime.date(2026, 1, 1), datetime.date(2026, 1, 4)), "2026 01.01-01.04")

    def test_week_ranges_from_jan1(self):
        ranges = week_ranges(datetime.date(2026, 1, 1), datetime.date(2026, 1, 12))
        self.assertEqual(ranges[0], (datetime.date(2026, 1, 1), datetime.date(2026, 1, 4)))
        self.assertEqual(ranges[1], (datetime.date(2026, 1, 5), datetime.date(2026, 1, 11)))

    def test_month_label(self):
        self.assertEqual(month_label(datetime.date(2026, 1, 10)), "2026-01")

    def test_next_week_monday(self):
        self.assertEqual(next_week_monday(datetime.date(2026, 8, 9)), datetime.date(2026, 8, 10))
```

- [ ] **Step 2: 运行测试确认失败**

Run: `$PY -m unittest tests.test_dates -v`（工作目录 `tools/github-trending`）

- [ ] **Step 3: 实现 `dates.py`**

```python
import datetime

def week_folder(start: datetime.date, end: datetime.date) -> str:
    return f"{start.year} {start.month:02d}.{start.day:02d}-{end.month:02d}.{end.day:02d}"

def week_ranges(start: datetime.date, end: datetime.date):
    cursor = start
    ranges = []
    while cursor <= end:
        if cursor.weekday() == 0:
            week_start = cursor
        else:
            week_start = cursor - datetime.timedelta(days=cursor.weekday())
        if week_start < start:
            week_start = start
        week_end = week_start + datetime.timedelta(days=6 - week_start.weekday())
        if week_end > end:
            week_end = end
        ranges.append((week_start, week_end))
        cursor = week_end + datetime.timedelta(days=1)
    return ranges

def month_label(d: datetime.date) -> str:
    return f"{d.year:04d}-{d.month:02d}"

def next_week_monday(d: datetime.date) -> datetime.date:
    return d + datetime.timedelta(days=(7 - d.weekday()) % 7 or 7)
```

- [ ] **Step 4: 运行测试确认通过**

Run: `$PY -m unittest tests.test_dates -v`

- [ ] **Step 5: 提交**

```bash
git add tools/github-trending
git commit -m "feat: add date and week range helpers"
```

---

### Task 2: GitHub API 客户端

**Files:**
- Create: `tools/github-trending/github_api.py`
- Test: `tools/github-trending/tests/test_github_api.py`

**Interfaces:**
- Consumes: `dates.py`
- Produces:
  - `search_new_repos(start: str, end: str, top: int = 10, token: str = None) -> list[dict]`
  - `get_repo(owner: str, repo: str, token: str = None) -> dict`
  - `get_readme_text(owner: str, repo: str, token: str = None) -> str`
  - `GitHubRateLimitError(Exception)`

- [ ] **Step 1: 写失败测试（mock `urllib.request.urlopen`）**

```python
import json
import unittest
from unittest import mock
from github_api import search_new_repos, get_repo, get_readme_text

class TestGitHubApi(unittest.TestCase):
    def test_search_new_repos_parses_items(self):
        payload = {"items": [{"full_name": "a/b", "stargazers_count": 10}]}
        with mock.patch("urllib.request.urlopen") as m:
            m.return_value.__enter__.return_value.read.return_value = json.dumps(payload).encode()
            result = search_new_repos("2026-01-01", "2026-01-04", token="x")
        self.assertEqual(result[0]["full_name"], "a/b")

    def test_get_repo(self):
        with mock.patch("urllib.request.urlopen") as m:
            m.return_value.__enter__.return_value.read.return_value = json.dumps({"full_name": "a/b"}).encode()
            result = get_repo("a", "b")
        self.assertEqual(result["full_name"], "a/b")

    def test_get_readme_text_decodes_base64(self):
        import base64
        payload = {"content": base64.b64encode(b"# Hello\nworld").decode()}
        with mock.patch("urllib.request.urlopen") as m:
            m.return_value.__enter__.return_value.read.return_value = json.dumps(payload).encode()
            result = get_readme_text("a", "b")
        self.assertIn("world", result)
```

- [ ] **Step 2: 运行测试确认失败**

Run: `$PY -m unittest tests.test_github_api -v`

- [ ] **Step 3: 实现 `github_api.py`**

```python
import base64
import json
import os
import time
import urllib.error
import urllib.request

class GitHubRateLimitError(Exception):
    pass

def _request(url, token=None, retries=3):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "codex-toolbox"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                time.sleep(8 * (attempt + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            time.sleep(5 * (attempt + 1))
    raise GitHubRateLimitError(f"request failed after retries: {url}")

def search_new_repos(start, end, top=10, token=None):
    url = ("https://api.github.com/search/repositories?q="
           f"created:{start}..{end}&sort=stars&order=desc&per_page={top}")
    data = _request(url, token)
    return data.get("items", [])

def get_repo(owner, repo, token=None):
    return _request(f"https://api.github.com/repos/{owner}/{repo}", token)

def get_readme_text(owner, repo, token=None):
    data = _request(f"https://api.github.com/repos/{owner}/{repo}/readme", token)
    return base64.b64decode(data.get("content", "")).decode("utf-8", errors="replace")
```

- [ ] **Step 4: 运行测试确认通过**

Run: `$PY -m unittest tests.test_github_api -v`

- [ ] **Step 5: 提交**

```bash
git add tools/github-trending
git commit -m "feat: add GitHub API client with rate-limit retry"
```

---

### Task 3: Trending 页面解析器

**Files:**
- Create: `tools/github-trending/trending_parser.py`
- Test: `tools/github-trending/tests/test_trending_parser.py`
- Fixture: `tools/github-trending/tests/fixtures/trending.html`

**Interfaces:**
- Consumes: `github_api._request`（复用其重试与 User-Agent）
- Produces: `fetch_trending(since: str = "weekly", token: str = None) -> list[dict]`
  - 返回字段：`full_name`、`description`、`language`、`stars_today`

- [ ] **Step 1: 写失败测试**

```python
import unittest
from unittest import mock
from trending_parser import fetch_trending

class TestTrendingParser(unittest.TestCase):
    def test_parse_fixture(self):
        html = open("tests/fixtures/trending.html", encoding="utf-8").read()
        with mock.patch("trending_parser._request") as m:
            m.return_value = html
            rows = fetch_trending()
        self.assertEqual(rows[0]["full_name"], "owner/repo-a")
        self.assertEqual(rows[0]["stars_today"], 123)
```

- [ ] **Step 2: 运行测试确认失败**

Run: `$PY -m unittest tests.test_trending_parser -v`

- [ ] **Step 3: 创建 fixture**

```html
<article class="Box-row">
  <h2><a href="/owner/repo-a">owner/repo-a</a></h2>
  <p>Description A</p>
  <span itemprop="programmingLanguage">Python</span>
  <span>123 stars today</span>
</article>
<article class="Box-row">
  <h2><a href="/owner/repo-b">owner/repo-b</a></h2>
  <p>Description B</p>
  <span itemprop="programmingLanguage">TypeScript</span>
  <span>45 stars today</span>
</article>
```

- [ ] **Step 4: 实现 `trending_parser.py`**

```python
import re
from html.parser import HTMLParser
from github_api import _request

class _TrendingParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.current = None
        self.in_h2 = False
        self.in_desc = False
        self.in_lang = False
        self.text_buf = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "article" and "Box-row" in attrs.get("class", ""):
            self.current = {"full_name": "", "description": "", "language": "", "stars_today": 0}
        elif tag == "h2" and self.current is not None:
            self.in_h2 = True
        elif tag == "p" and self.current is not None:
            self.in_desc = True
        elif tag == "span" and attrs.get("itemprop") == "programmingLanguage":
            self.in_lang = True

    def handle_endtag(self, tag):
        if tag == "article" and self.current is not None:
            self.rows.append(self.current)
            self.current = None
        elif tag == "h2":
            self.in_h2 = False
        elif tag == "p":
            self.in_desc = False
        elif tag == "span":
            self.in_lang = False

    def handle_data(self, data):
        if self.current is None:
            return
        text = data.strip()
        if not text:
            return
        if self.in_h2:
            self.current["full_name"] += text
        elif self.in_desc:
            self.current["description"] += text
        elif self.in_lang:
            self.current["language"] += text
        elif "stars today" in text:
            self.current["stars_today_text"] = text

def fetch_trending(since="weekly", token=None):
    url = f"https://github.com/trending?since={since}"
    html = _request(url, token)
    parser = _TrendingParser()
    parser.feed(html)
    for row in parser.rows:
        m = re.search(r"(\d[\d,]*)\s+stars today", row.get("stars_today_text", ""))
        row["stars_today"] = int(m.group(1).replace(",", "")) if m else 0
        row["stars_today_text"] = ""
    return parser.rows
```

- [ ] **Step 5: 运行测试确认通过**

Run: `$PY -m unittest tests.test_trending_parser -v`

- [ ] **Step 6: 提交**

```bash
git add tools/github-trending
git commit -m "feat: add GitHub trending page parser"
```

---

### Task 4: star 快照模块

**Files:**
- Create: `tools/github-trending/snapshot.py`
- Test: `tools/github-trending/tests/test_snapshot.py`

**Interfaces:**
- Produces:
  - `load_snapshot(path: str) -> dict`
  - `save_snapshot(path: str, data: dict) -> None`
  - `update_snapshot(prev: dict, current: dict) -> dict`
    - `prev/current` 形如 `{"owner/repo": 123}`
    - 返回 `{"owner/repo": {"stars": 123, "delta": 10}}`

- [ ] **Step 1: 写失败测试**

```python
import unittest
import tempfile
import os
from snapshot import load_snapshot, save_snapshot, update_snapshot

class TestSnapshot(unittest.TestCase):
    def test_save_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "snap.json")
            save_snapshot(path, {"a/b": 5})
            self.assertEqual(load_snapshot(path), {"a/b": 5})

    def test_update_snapshot_computes_delta(self):
        result = update_snapshot({"a/b": 5}, {"a/b": 15, "c/d": 3})
        self.assertEqual(result["a/b"]["delta"], 10)
        self.assertEqual(result["c/d"]["delta"], 0)
```

- [ ] **Step 2: 运行测试确认失败**

Run: `$PY -m unittest tests.test_snapshot -v`

- [ ] **Step 3: 实现 `snapshot.py`**

```python
import json
import os

def load_snapshot(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_snapshot(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def update_snapshot(prev, current):
    result = {}
    for repo, stars in current.items():
        result[repo] = {"stars": stars, "delta": stars - prev.get(repo, stars)}
    for repo, stars in prev.items():
        if repo not in result:
            result[repo] = {"stars": stars, "delta": 0}
    return result
```

- [ ] **Step 4: 运行测试确认通过**

Run: `$PY -m unittest tests.test_snapshot -v`

- [ ] **Step 5: 提交**

```bash
git add tools/github-trending
git commit -m "feat: add star snapshot persistence and delta calc"
```

---

### Task 5: 推荐理由模块

**Files:**
- Create: `tools/github-trending/recommend.py`
- Test: `tools/github-trending/tests/test_recommend.py`

**Interfaces:**
- Produces: `recommend(project: dict) -> str`
  - 输入项目字段：`name`、`description`、`language`、`topics: list[str]`

- [ ] **Step 1: 写失败测试**

```python
import unittest
from recommend import recommend

class TestRecommend(unittest.TestCase):
    def test_ai_topic(self):
        p = {"name": "llm-tool", "description": "local LLM runner", "language": "Python", "topics": ["llm", "ai"]}
        self.assertIn("AI", recommend(p))

    def test_python_tooling(self):
        p = {"name": "pytest-helper", "description": "test helpers", "language": "Python", "topics": ["testing"]}
        self.assertIn("Python 工具", recommend(p))
```

- [ ] **Step 2: 运行测试确认失败**

Run: `$PY -m unittest tests.test_recommend -v`

- [ ] **Step 3: 实现 `recommend.py`**

```python
def recommend(project):
    text = f"{project.get('name', '')} {project.get('description', '')} {' '.join(project.get('topics', []))}".lower()
    reasons = []
    if any(k in text for k in ("llm", "ai", "agent", "chatgpt", "deepseek", "rag")):
        reasons.append("AI/LLM 方向，可能对你的 Agent 工具链有直接参考价值")
    if project.get("language") == "Python" or "python" in text:
        reasons.append("Python 技术栈，适合做脚本、自动化或工具扩展")
    if any(k in text for k in ("obsidian", "note", "knowledge", "markdown")):
        reasons.append("与 Obsidian/笔记/知识管理相关，可直接借鉴或集成")
    if any(k in text for k in ("mcp", "model context protocol")):
        reasons.append("MCP 生态项目，可对照你的 MCP 收藏库评估")
    if any(k in text for k in ("automation", "workflow", "cli", "crawler", "scrape")):
        reasons.append("偏自动化和工程效率，适合补进工具库场景")
    if not reasons:
        reasons.append("值得关注的新项目，建议按文档判断是否适合你的工作流")
    return "；".join(reasons) + "。"
```

- [ ] **Step 4: 运行测试确认通过**

Run: `$PY -m unittest tests.test_recommend -v`

- [ ] **Step 5: 提交**

```bash
git add tools/github-trending
git commit -m "feat: add rule-based recommendation generator"
```

---

### Task 6: Markdown 报告生成

**Files:**
- Create: `tools/github-trending/report.py`
- Test: `tools/github-trending/tests/test_report.py`

**Interfaces:**
- Consumes: `dates.week_folder`、`recommend.recommend`
- Produces:
  - `render_project_block(project: dict) -> str`
  - `render_ranking(title: str, projects: list[dict]) -> str`
  - `render_index(week_label: str, files: list[str]) -> str`
  - `write_week_folder(output_root: str, start, end, weekly: dict, monthly: dict) -> str`
    - `weekly`：`{"new_star": [...], "trending": [...], "star_delta": [...]}`，缺失口径传空 list 则不生成该文件
    - 返回周文件夹绝对路径

- [ ] **Step 1: 写失败测试**

```python
import datetime
import tempfile
import os
import unittest
from report import write_week_folder

class TestReport(unittest.TestCase):
    def test_write_week_folder(self):
        p = {"name": "demo", "description": "demo project", "language": "Python", "topics": [], "stars": 10}
        with tempfile.TemporaryDirectory() as d:
            path = write_week_folder(d, datetime.date(2026, 1, 5), datetime.date(2026, 1, 11),
                                     {"new_star": [p], "trending": [], "star_delta": []}, [])
            self.assertTrue(os.path.isdir(path))
            self.assertTrue(os.path.exists(os.path.join(path, "index.md")))
            self.assertTrue(os.path.exists(os.path.join(path, "周榜-新建-star.md")))
            self.assertFalse(os.path.exists(os.path.join(path, "周榜-trending.md")))
```

- [ ] **Step 2: 运行测试确认失败**

Run: `$PY -m unittest tests.test_report -v`

- [ ] **Step 3: 实现 `report.py`**

```python
import json
import os
from dates import week_folder, month_label
from recommend import recommend

def render_project_block(p):
    topics = ", ".join(p.get("topics", [])) or "无"
    return (
        f"### {p.get('name')}\n\n"
        f"- 链接：<{p.get('html_url', '')}>\n"
        f"- 语言：{p.get('language') or '未标注'}\n"
        f"- Stars：{p.get('stargazers_count', p.get('stars', 0))}\n"
        f"- 创建时间：{p.get('created_at', '未知')}\n"
        f"- Topics：{topics}\n\n"
        f"**项目介绍**\n\n{p.get('description') or '暂无简介'}\n\n"
        f"**你可能用到**\n\n{recommend(p)}\n\n"
        "---\n"
    )

def render_ranking(title, projects):
    lines = [f"# {title}", "", f"共 {len(projects)} 个项目", ""]
    for i, p in enumerate(projects, 1):
        lines.append(f"## Top {i}：{p.get('name')}")
        lines.append("")
        lines.extend(render_project_block(p).splitlines())
    return "\n".join(lines) + "\n"

def render_index(week_label, files):
    links = "\n".join(f"- [[{f.replace('.md', '')}|{f}]]" for f in files)
    return f"# {week_label} GitHub 热点\n\n## 榜单文件\n\n{links}\n"

def write_week_folder(output_root, start, end, weekly, monthly):
    folder = os.path.join(output_root, week_folder(start, end))
    os.makedirs(folder, exist_ok=True)
    mapping = {
        "new_star": ("周榜-新建-star.md", "本周新建仓库 Star Top"),
        "trending": ("周榜-trending.md", "GitHub 官方 Trending 周榜"),
        "star_delta": ("周榜-star增速.md", "本周 Star 增速榜"),
    }
    files = ["index.md"]
    for key, (filename, title) in mapping.items():
        projects = weekly.get(key, [])
        if projects:
            with open(os.path.join(folder, filename), "w", encoding="utf-8") as f:
                f.write(render_ranking(f"{week_folder(start, end)} {title}", projects))
            files.append(filename)
    month_projects = monthly or []
    if month_projects:
        month_name = month_label(start)
        month_file = f"月榜-{month_name}.md"
        with open(os.path.join(folder, month_file), "w", encoding="utf-8") as f:
            f.write(render_ranking(f"{month_name} 月榜（新建仓库 Star Top）", month_projects))
        files.append(month_file)
    with open(os.path.join(folder, "index.md"), "w", encoding="utf-8") as f:
        f.write(render_index(week_folder(start, end), files))
    raw = {"start": start.isoformat(), "end": end.isoformat(), "weekly": weekly, "monthly": monthly}
    with open(os.path.join(folder, "raw-data.json"), "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)
    return folder
```

- [ ] **Step 4: 运行测试确认通过**

Run: `$PY -m unittest tests.test_report -v`

- [ ] **Step 5: 提交**

```bash
git add tools/github-trending
git commit -m "feat: add markdown report generator"
```

---

### Task 7: CLI 串联

**Files:**
- Create: `tools/github-trending/collect.py`
- Test: `tools/github-trending/tests/test_collect.py`

**Interfaces:**
- Consumes: `dates`、`github_api`、`trending_parser`、`snapshot`、`report`
- Produces:
  - `run_backfill(start: date, end: date, top: int, max_count: int, token: str, output_root: str, data_dir: str) -> int`
  - `run_week(week_start: date, top: int, max_count: int, token: str, output_root: str, data_dir: str) -> int`
  - `run_month(month: str, top: int, max_count: int, token: str, output_root: str, data_dir: str) -> int`
  - CLI 参数：`--backfill`、`--start`、`--end`、`--week`、`--month`、`--top`、`--max`、`--token`、`--output-root`、`--data-dir`

- [ ] **Step 1: 写失败测试**

```python
import datetime
import os
import tempfile
import unittest
from unittest import mock
import collect

class TestCollect(unittest.TestCase):
    def test_run_week_creates_files(self):
        with tempfile.TemporaryDirectory() as d:
            with mock.patch("github_api.search_new_repos", return_value=[{"name": "demo", "stargazers_count": 1}]), \
                 mock.patch("github_api.get_repo", return_value={"stargazers_count": 1}), \
                 mock.patch("github_api.get_readme_text", return_value="# demo"):
                count = collect.run_week(datetime.date(2026, 8, 3), 10, 15, None, d, os.path.join(d, "data"))
            self.assertGreaterEqual(count, 3)
            self.assertTrue(os.path.exists(os.path.join(d, "2026 08.03-08.09", "index.md")))
```

- [ ] **Step 2: 运行测试确认失败**

Run: `$PY -m unittest tests.test_collect -v`

- [ ] **Step 3: 实现 `collect.py`**

```python
import argparse
import datetime
import json
import os
import sys

from dates import week_ranges, month_label, next_week_monday
from github_api import search_new_repos, get_repo, get_readme_text
from trending_parser import fetch_trending
from snapshot import load_snapshot, save_snapshot, update_snapshot
from report import write_week_folder

def _enrich(project, token):
    owner, repo = project["full_name"].split("/", 1)
    try:
        readme = get_readme_text(owner, repo, token)
        project["readme_excerpt"] = readme[:2000]
    except Exception:
        project["readme_excerpt"] = ""
    return project

def _collect_new(start, end, top, max_count, token):
    projects = search_new_repos(start.isoformat(), end.isoformat(), top=max_count, token=token)
    enriched = []
    for p in projects[:max_count]:
        enriched.append(_enrich(p, token))
    return enriched

def run_backfill(start, end, top, max_count, token, output_root, data_dir):
    total = 0
    for ws, we in week_ranges(start, end):
        weekly = {"new_star": _collect_new(ws, we, top, max_count, token)}
        month_start = ws.replace(day=1)
        month_end = (month_start + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
        monthly = _collect_new(month_start, month_end, top, max_count, token)
        write_week_folder(output_root, ws, we, weekly, monthly)
        total += 1
    return total

def run_week(week_start, top, max_count, token, output_root, data_dir):
    ws = week_start
    we = ws + datetime.timedelta(days=6)
    weekly = {
        "new_star": _collect_new(ws, we, top, max_count, token),
        "trending": fetch_trending("weekly", token)[:max_count],
    }
    prev = load_snapshot(os.path.join(data_dir, "star_snapshot.json"))
    current = {}
    for p in weekly["new_star"][:50]:
        current[p["full_name"]] = p.get("stargazers_count", 0)
    for repo in prev:
        if repo not in current:
            try:
                owner, name = repo.split("/", 1)
                current[repo] = get_repo(owner, name, token).get("stargazers_count", 0)
            except Exception:
                continue
    deltas = update_snapshot(prev, current)
    save_snapshot(os.path.join(data_dir, "star_snapshot.json"), current)
    growth = [{"name": k, "stargazers_count": v["stars"], "delta": v["delta"]} for k, v in sorted(deltas.items(), key=lambda x: -x[1]["delta"])]
    if any(v["delta"] > 0 for v in deltas.values()):
        weekly["star_delta"] = growth[:max_count]
    month_start = ws.replace(day=1)
    month_end = (month_start + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
    monthly = _collect_new(month_start, month_end, top, max_count, token)
    write_week_folder(output_root, ws, we, weekly, monthly)
    return 1

def run_month(month, top, max_count, token, output_root, data_dir):
    y, m = map(int, month.split("-"))
    ms = datetime.date(y, m, 1)
    me = (ms + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
    projects = _collect_new(ms, me, top, max_count, token)
    for ws, we in week_ranges(ms, me):
        if ws.month != m:
            continue
        write_week_folder(output_root, ws, we, {"new_star": []}, projects)
    return len(projects)

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--backfill", action="store_true")
    ap.add_argument("--start")
    ap.add_argument("--end")
    ap.add_argument("--week")
    ap.add_argument("--month")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--max", dest="max_count", type=int, default=15)
    ap.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"))
    ap.add_argument("--output-root", default=os.path.join(os.path.dirname(__file__), "..", "..", "github-trending"))
    ap.add_argument("--data-dir", default=os.path.join(os.path.dirname(__file__), "data"))
    args = ap.parse_args(argv)
    output_root = os.path.abspath(args.output_root)
    if args.backfill:
        count = run_backfill(datetime.date.fromisoformat(args.start), datetime.date.fromisoformat(args.end),
                             args.top, args.max_count, args.token, output_root, args.data_dir)
        print(f"backfill completed: {count} weeks")
    elif args.week:
        run_week(datetime.date.fromisoformat(args.week), args.top, args.max_count, args.token, output_root, args.data_dir)
        print("week report generated")
    elif args.month:
        n = run_month(args.month, args.top, args.max_count, args.token, output_root, args.data_dir)
        print(f"month report generated: {n} projects")
    else:
        ap.print_help()

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 运行测试确认通过**

Run: `$PY -m unittest tests.test_collect -v`

- [ ] **Step 5: 提交**

```bash
git add tools/github-trending
git commit -m "feat: add collect CLI for backfill and weekly runs"
```

---

### Task 8: 历史补录

**Files:**
- Output: `github-trending/2026 01.01-01.04/` 至 `github-trending/2026 08.03-08.09/`

- [ ] **Step 1: 运行历史补录**

Run: `$PY collect.py --backfill --start 2026-01-01 --end 2026-08-09 --max 15`
Expected: 输出 `backfill completed: 32 weeks`（实际周数按脚本计算）

- [ ] **Step 2: 检查首尾周文件**

Run: `Get-ChildItem "github-trending" | Select-Object Name`；抽查 `2026 01.01-01.04\index.md` 与 `2026 08.03-08.09\index.md`。

- [ ] **Step 3: 提交归档**

```bash
git add github-trending tools/github-trending/data
git commit -m "chore: backfill github trending archives from 2026-01-01"
```

---

### Task 9: 一键运行脚本与自动化

**Files:**
- Create: `tools/github-trending/run-weekly.ps1`
- Create: `tools/github-trending/run-weekly.bat`

- [ ] **Step 1: 创建 PowerShell 脚本**

```powershell
$PY = "C:\Users\subrid\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$MONDAY = (Get-Date).Date
while ($MONDAY.DayOfWeek -ne "Monday") { $MONDAY = $MONDAY.AddDays(-1) }
$LAST_MONDAY = $MONDAY.AddDays(-7)
& $PY "D:\program\CC 工具库\tools\github-trending\collect.py" --week $LAST_MONDAY.ToString("yyyy-MM-dd")
```

- [ ] **Step 2: 创建 bat 包装**

```bat
@echo off
powershell -ExecutionPolicy Bypass -File "D:\program\CC 工具库\tools\github-trending\run-weekly.ps1"
```

- [ ] **Step 3: 尝试创建 Codex 每周自动任务；若当前环境不支持，把配置说明写入 `docs/github-trending-介绍.md`**

- [ ] **Step 4: 提交**

```bash
git add tools/github-trending
git commit -m "feat: add weekly runner scripts and automation notes"
```

---

### Task 10: 文档更新

**Files:**
- Create: `docs/github-trending-介绍.md`
- Modify: `docs/README.md`
- Modify: `AGENTS.md`

- [ ] **Step 1: 写介绍文档**：目录、三种口径、命令、Obsidian 打开方式、自动任务说明。
- [ ] **Step 2: 更新 `docs/README.md`**：在索引中加 GitHub 热点收集条目。
- [ ] **Step 3: 更新 `AGENTS.md`**：目录结构加 `github-trending/` 与 `tools/github-trending/`；场景速查表加「每周 GitHub 热点」。
- [ ] **Step 4: 提交**

```bash
git add docs AGENTS.md
git commit -m "docs: document github trending collector"
```

---

### Task 11: 收尾验证

- [ ] **Step 1: 运行全部测试**

Run: `$PY -m unittest discover -s tests -v`（工作目录 `tools/github-trending`）

- [ ] **Step 2: 检查 Obsidian 结构**：确认每个周文件夹含 `index.md`、榜单文件、`raw-data.json`。
- [ ] **Step 3: 检查 git 状态**：确认无未提交变更（除用户既有未跟踪文件）。
- [ ] **Step 4: 向用户汇报**：文件位置、历史周数、自动任务状态、后续使用方式。
