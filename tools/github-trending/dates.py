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
