import json
import os

from dates import week_folder, month_label
from recommend import recommend


def _project_name(p):
    return p.get("name") or p.get("full_name") or "未知"


def _project_url(p):
    if p.get("html_url"):
        return p["html_url"]
    if p.get("full_name"):
        return f"https://github.com/{p['full_name']}"
    return ""


def render_project_block(p):
    topics = ", ".join(p.get("topics", [])) or "无"
    stars = p.get("stargazers_count", p.get("stars", 0))
    if p.get("delta"):
        stars_text = f"{stars}（本周 +{p['delta']}）"
    elif p.get("stars_today"):
        stars_text = f"周期内 +{p['stars_today']}"
    else:
        stars_text = str(stars)
    return (
        f"### {_project_name(p)}\n\n"
        f"- 链接：<{_project_url(p)}>\n"
        f"- 语言：{p.get('language') or '未标注'}\n"
        f"- Stars：{stars_text}\n"
        f"- 创建时间：{p.get('created_at', '未知')}\n"
        f"- Topics：{topics}\n\n"
        f"**项目介绍**\n\n{p.get('description') or '暂无简介'}\n\n"
        f"**你可能用到**\n\n{recommend(p)}\n\n"
        "---\n"
    )


def render_ranking(title, projects):
    lines = [f"# {title}", "", f"共 {len(projects)} 个项目", ""]
    for i, p in enumerate(projects, 1):
        lines.append(f"## Top {i}：{_project_name(p)}")
        lines.append("")
        lines.append(render_project_block(p))
    return "\n".join(lines) + "\n"


def render_index(week_label, files):
    links = "\n".join(f"- [[{f.replace('.md', '')}|{f}]]" for f in files)
    return f"# {week_label} GitHub 热点\n\n## 榜单文件\n\n{links}\n"


def render_root_readme(folders):
    links = "\n".join(f"- [[{folder}|{folder}]]" for folder in folders)
    return (
        "# GitHub 每周热点\n\n"
        "用 Obsidian 打开本文件夹即可浏览。每周目录按 `YYYY MM.DD-MM.DD` 命名。\n\n"
        "## 周归档\n\n"
        f"{links}\n"
    )


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
