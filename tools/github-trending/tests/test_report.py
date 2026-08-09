import datetime
import os
import tempfile
import unittest

from report import write_week_folder, render_root_readme


class TestReport(unittest.TestCase):
    def test_render_root_readme(self):
        text = render_root_readme(["2026 01.01-01.04", "2026 01.05-01.11"])
        self.assertIn("[[2026 01.01-01.04|2026 01.01-01.04]]", text)
        self.assertIn("2026 01.05-01.11", text)

    def test_write_week_folder(self):
        p = {
            "name": "demo",
            "description": "demo project",
            "language": "Python",
            "topics": [],
            "stargazers_count": 10,
            "html_url": "https://github.com/a/demo",
            "created_at": "2026-01-05T00:00:00Z",
        }
        with tempfile.TemporaryDirectory() as d:
            path = write_week_folder(
                d,
                datetime.date(2026, 1, 5),
                datetime.date(2026, 1, 11),
                {"new_star": [p], "trending": [], "star_delta": []},
                [],
            )
            self.assertTrue(os.path.isdir(path))
            self.assertTrue(os.path.exists(os.path.join(path, "index.md")))
            self.assertTrue(os.path.exists(os.path.join(path, "周榜-新建-star.md")))
            self.assertFalse(os.path.exists(os.path.join(path, "周榜-trending.md")))


if __name__ == "__main__":
    unittest.main()
