#!/usr/bin/env python3
"""Generate a spaced repetition review schedule.

Outputs:
- A markdown schedule with dated review prompts
- An .ics calendar file the user can import into Google Calendar / Apple Calendar

Default review intervals follow the SM-2-inspired curve:
    Day 1, Day 3, Day 7, Day 14, Day 30, Day 60, Day 120

Each review session has:
- A date
- A review prompt
- An estimated duration

Usage:
    python generate_schedule.py --topic "Postgres indexing" --output-dir ./out
    python generate_schedule.py --topic "Polish vocabulary" --start 2026-05-08 --intervals "1,3,7,14,30,60,120"
"""

import argparse
import datetime as dt
import sys
import uuid
from pathlib import Path


DEFAULT_INTERVALS = [1, 3, 7, 14, 30, 60, 120]


def to_ics_dt(dtv: dt.datetime) -> str:
    """ICS uses UTC formatted as YYYYMMDDTHHMMSSZ."""
    return dtv.strftime("%Y%m%dT%H%M%SZ")


def make_markdown(topic: str, start: dt.date, intervals: list[int], duration_min: int) -> str:
    lines = [f"# {topic} — Spaced Repetition Schedule",
             "",
             f"**Topic:** {topic}",
             f"**First learned:** {start.isoformat()}",
             f"**Per-session duration:** ~{duration_min} minutes",
             "",
             "## Why follow this",
             "",
             "Each review is timed to hit you just before you'd forget. Skipping reviews makes the next one harder; doing them on schedule means each one strengthens the memory and you can space them out further. If you fail a review badly, restart the schedule from Day 1 for that material.",
             "",
             "## Schedule",
             "",
             "| # | Date | Day | Activity |",
             "|---|------|-----|----------|"]
    today = dt.date.today()
    for i, days in enumerate(intervals, start=1):
        d = start + dt.timedelta(days=days)
        weekday = d.strftime("%a")
        date_cell = d.isoformat()
        if d == today:
            date_cell = f"**{date_cell} (today)**"
        elif d < today:
            date_cell = f"~~{date_cell}~~"
        activity = activity_for_review(i, len(intervals))
        lines.append(f"| {i} | {date_cell} | {weekday} D+{days:>3} | {activity} |")
    lines += ["", "## Notes",
              "",
              "- **Pass with confidence:** advance to the next review on schedule.",
              "- **Pass with hesitation:** keep the next review on schedule but add 1 extra interval.",
              "- **Fail:** restart from Day 1 (don't skip ahead). The forgetting curve resets.",
              "- **Missed a day:** do that review as soon as you remember; don't double up by doing two reviews back-to-back unless they're for different material.",
              "",
              "## What to do in each session",
              "",
              "Each session is a *retrieval session*, not a re-reading. Try to:",
              "1. Cover your notes.",
              "2. Recall as much as you can about the topic from memory — say it out loud or write it down.",
              "3. Compare against your notes; identify the gap.",
              "4. Re-state the gap correctly, then move on.",
              "",
              "If you have flashcards (an Anki deck or HTML flashcards) for this topic, do them as part of this session.",
              ""]
    return "\n".join(lines)


def activity_for_review(idx: int, total: int) -> str:
    """Vary review activity to keep it interesting and effective."""
    activities = [
        "**Brain dump:** write down everything you remember on the topic without notes. Compare to source.",
        "**Flashcards:** quiz yourself on the key facts from this topic.",
        "**Teach-back:** explain the topic out loud as if to a beginner. Find the gaps.",
        "**Application:** solve one new problem / example using the topic.",
        "**Summary:** write a fresh one-page summary of the topic from memory.",
        "**Edge cases:** name 3 places this topic could go wrong or have surprising behavior.",
        "**Connections:** link this topic to two other things you know. How are they related?",
    ]
    return activities[(idx - 1) % len(activities)]


def make_ics(topic: str, start: dt.date, intervals: list[int], duration_min: int, time: str) -> str:
    """Build an .ics file with one VEVENT per review."""
    cal = ["BEGIN:VCALENDAR",
           "VERSION:2.0",
           "PRODID:-//the-learning-skill//Spaced Repetition//EN",
           "CALSCALE:GREGORIAN",
           "METHOD:PUBLISH"]
    hour, minute = (int(x) for x in time.split(":"))
    for i, days in enumerate(intervals, start=1):
        d = start + dt.timedelta(days=days)
        start_local = dt.datetime(d.year, d.month, d.day, hour, minute)
        # Treat as UTC for simplicity; users can adjust on import.
        end_local = start_local + dt.timedelta(minutes=duration_min)
        uid = uuid.uuid4().hex
        activity = activity_for_review(i, len(intervals))
        cal += [
            "BEGIN:VEVENT",
            f"UID:{uid}@the-learning-skill",
            f"DTSTAMP:{to_ics_dt(dt.datetime.now(dt.timezone.utc).replace(tzinfo=None))}",
            f"DTSTART:{to_ics_dt(start_local)}",
            f"DTEND:{to_ics_dt(end_local)}",
            f"SUMMARY:Review {i}/{len(intervals)} — {topic}",
            f"DESCRIPTION:{activity.replace(chr(10), ' ').replace('**', '')}",
            "BEGIN:VALARM",
            "TRIGGER:-PT15M",
            "ACTION:DISPLAY",
            f"DESCRIPTION:Review {topic} in 15 minutes",
            "END:VALARM",
            "END:VEVENT",
        ]
    cal.append("END:VCALENDAR")
    return "\n".join(cal) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--topic", required=True, help="Name of the topic")
    p.add_argument("--output-dir", type=Path, default=Path("."), help="Where to write outputs")
    p.add_argument("--start", default=None, help="First-learned date (YYYY-MM-DD); defaults to today")
    p.add_argument("--intervals", default=",".join(str(i) for i in DEFAULT_INTERVALS),
                   help="Comma-separated days, e.g. 1,3,7,14,30,60,120")
    p.add_argument("--duration", type=int, default=20, help="Per-session duration in minutes")
    p.add_argument("--time", default="18:00", help="Time of day for calendar events (HH:MM 24h)")
    p.add_argument("--no-ics", action="store_true", help="Skip .ics generation")
    args = p.parse_args()

    if args.start:
        start = dt.date.fromisoformat(args.start)
    else:
        start = dt.date.today()

    intervals = [int(x.strip()) for x in args.intervals.split(",") if x.strip()]
    if not intervals:
        print("Error: at least one interval required", file=sys.stderr)
        return 1

    args.output_dir.mkdir(parents=True, exist_ok=True)
    safe_topic = "".join(c if c.isalnum() or c in "-_" else "_" for c in args.topic.lower())[:60]

    md = make_markdown(args.topic, start, intervals, args.duration)
    md_path = args.output_dir / f"{safe_topic}-schedule.md"
    md_path.write_text(md, encoding="utf-8")
    print(f"Wrote schedule: {md_path}")

    if not args.no_ics:
        ics = make_ics(args.topic, start, intervals, args.duration, args.time)
        ics_path = args.output_dir / f"{safe_topic}-schedule.ics"
        ics_path.write_text(ics, encoding="utf-8")
        print(f"Wrote calendar: {ics_path}")
        print(f"  Import via Google Calendar Settings → Import & export → Import")
        print(f"  Or open the .ics file to add to Apple Calendar")

    return 0


if __name__ == "__main__":
    sys.exit(main())
