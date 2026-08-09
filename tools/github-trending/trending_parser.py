import re
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser


def _fetch_html(url, token=None, retries=3):
    headers = {"User-Agent": "codex-toolbox"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                time.sleep(8 * (attempt + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"trending page failed after retries: {url}")


class _TrendingParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.current = None
        self.in_h2 = False
        self.in_desc = False
        self.in_lang = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "article" and "Box-row" in attrs.get("class", ""):
            self.current = {"full_name": "", "description": "", "language": "", "stars_today_text": ""}
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
    html = _fetch_html(url, token)
    parser = _TrendingParser()
    parser.feed(html)
    for row in parser.rows:
        m = re.search(r"([\d,]+)\s+stars today", row["stars_today_text"])
        row["stars_today"] = int(m.group(1).replace(",", "")) if m else 0
        row["description"] = row["description"].strip()
        row["full_name"] = row["full_name"].strip()
    return parser.rows
