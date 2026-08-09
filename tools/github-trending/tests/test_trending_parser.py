import unittest
from unittest import mock

from trending_parser import fetch_trending


class TestTrendingParser(unittest.TestCase):
    def test_parse_fixture(self):
        with open("tests/fixtures/trending.html", encoding="utf-8") as f:
            html = f.read()
        with mock.patch("trending_parser._fetch_html") as m:
            m.return_value = html
            rows = fetch_trending()
        self.assertEqual(rows[0]["full_name"], "owner/repo-a")
        self.assertEqual(rows[0]["stars_today"], 123)
        self.assertEqual(rows[1]["full_name"], "owner/repo-b")
        self.assertEqual(rows[1]["language"], "TypeScript")


if __name__ == "__main__":
    unittest.main()
