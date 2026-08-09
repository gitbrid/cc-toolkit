import argparse
import datetime
import os
import sys
import time

from dates import week_ranges, month_label
from github_api import search_new_repos, get_repo, get_readme_text
from report import write_week_folder
from snapshot import load_snapshot, save_snapshot, update_snapshot
from trending_parser import fetch_trending


def _log_failure(data_dir, message):
    os.makedirs(data_dir, exist_ok=True)
    with open(os.path.join(data_dir, "failed.log"), "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now().isoformat()} {message}\n")


def _enrich(project, token, with_readme):
    if with_readme and "full_name" in project:
        owner, repo = project["full_name"].split("/", 1)
        try:
            project["readme_excerpt"] = get_readme_text(owner, repo, token)[:2000]
        except Exception:
            project["readme_excerpt"] = ""
    else:
        project["readme_excerpt"] = ""
    return project


def _collect_new(start, end, top, max_count, token, with_readme):
    projects = search_new_repos(start.isoformat(), end.isoformat(), top=max_count, token=token)
    enriched = []
    for p in projects[:max_count]:
        enriched.append(_enrich(p, token, with_readme))
    return enriched


def _month_bounds(d):
    ms = d.replace(day=1)
    me = (ms + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
    return ms, me


def run_backfill(start, end, top, max_count, token, output_root, data_dir, with_readme=False):
    total = 0
    month_cache = {}
    for ws, we in week_ranges(start, end):
        try:
            weekly = {"new_star": _collect_new(ws, we, top, max_count, token, with_readme)}
            ms, me = _month_bounds(ws)
            month_key = month_label(ws)
            if month_key not in month_cache:
                month_cache[month_key] = _collect_new(ms, me, top, max_count, token, with_readme)
            write_week_folder(output_root, ws, we, weekly, month_cache[month_key])
            total += 1
            time.sleep(7)
        except Exception as e:
            _log_failure(data_dir, f"backfill week {ws}..{we}: {e}")
    return total


def run_week(week_start, top, max_count, token, output_root, data_dir, with_readme=True):
    ws = week_start
    we = ws + datetime.timedelta(days=6)
    weekly = {"new_star": _collect_new(ws, we, top, max_count, token, with_readme)}
    try:
        weekly["trending"] = fetch_trending("weekly", token)[:max_count]
    except Exception as e:
        _log_failure(data_dir, f"trending weekly: {e}")
    try:
        prev = load_snapshot(os.path.join(data_dir, "star_snapshot.json"))
        current = {p["full_name"]: p.get("stargazers_count", 0) for p in weekly["new_star"][:50]}
        for repo in prev:
            if repo not in current:
                try:
                    owner, name = repo.split("/", 1)
                    current[repo] = get_repo(owner, name, token).get("stargazers_count", 0)
                except Exception:
                    continue
        deltas = update_snapshot(prev, current)
        save_snapshot(os.path.join(data_dir, "star_snapshot.json"), current)
        growth = [
            {"name": k, "stargazers_count": v["stars"], "delta": v["delta"]}
            for k, v in sorted(deltas.items(), key=lambda x: -x[1]["delta"])
        ]
        if any(v["delta"] > 0 for v in deltas.values()):
            weekly["star_delta"] = growth[:max_count]
    except Exception as e:
        _log_failure(data_dir, f"star snapshot: {e}")
    ms, me = _month_bounds(ws)
    monthly = _collect_new(ms, me, top, max_count, token, with_readme)
    write_week_folder(output_root, ws, we, weekly, monthly)
    return 1


def run_month(month, top, max_count, token, output_root, data_dir, with_readme=False):
    y, m = map(int, month.split("-"))
    ms = datetime.date(y, m, 1)
    me = (ms + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
    projects = _collect_new(ms, me, top, max_count, token, with_readme)
    for ws, we in week_ranges(ms, me):
        if ws.month != m:
            continue
        write_week_folder(output_root, ws, we, {"new_star": []}, projects)
    return len(projects)


def main(argv=None):
    ap = argparse.ArgumentParser(description="GitHub 每周热点收集")
    ap.add_argument("--backfill", action="store_true", help="历史补录")
    ap.add_argument("--start", help="补录开始日期 YYYY-MM-DD")
    ap.add_argument("--end", help="补录结束日期 YYYY-MM-DD")
    ap.add_argument("--week", help="生成指定周，传该周周一日期 YYYY-MM-DD")
    ap.add_argument("--month", help="生成指定月 YYYY-MM")
    ap.add_argument("--top", type=int, default=10, help="榜单默认数量")
    ap.add_argument("--max", dest="max_count", type=int, default=15, help="榜单最大数量")
    ap.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"), help="GitHub token")
    ap.add_argument("--with-readme", action="store_true", help="抓取 README 摘要（增加 API 请求）")
    ap.add_argument(
        "--output-root",
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "github-trending")),
        help="Obsidian 库根目录",
    )
    ap.add_argument("--data-dir", default=os.path.join(os.path.dirname(__file__), "data"))
    args = ap.parse_args(argv)
    output_root = os.path.abspath(args.output_root)
    if args.backfill:
        if not args.start or not args.end:
            ap.error("--backfill 需要 --start 和 --end")
        count = run_backfill(
            datetime.date.fromisoformat(args.start),
            datetime.date.fromisoformat(args.end),
            args.top,
            args.max_count,
            args.token,
            output_root,
            args.data_dir,
            args.with_readme,
        )
        print(f"backfill completed: {count} weeks")
    elif args.week:
        run_week(
            datetime.date.fromisoformat(args.week),
            args.top,
            args.max_count,
            args.token,
            output_root,
            args.data_dir,
            args.with_readme,
        )
        print("week report generated")
    elif args.month:
        n = run_month(args.month, args.top, args.max_count, args.token, output_root, args.data_dir, args.with_readme)
        print(f"month report generated: {n} projects")
    else:
        ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
