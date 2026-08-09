import datetime
import os
import tempfile
import unittest
from unittest import mock

import collect
from snapshot import save_snapshot


class TestCollect(unittest.TestCase):
    def test_run_week_creates_files(self):
        project = {"name": "demo", "full_name": "a/demo", "stargazers_count": 1, "description": "demo"}
        with tempfile.TemporaryDirectory() as d:
            with mock.patch("collect.search_new_repos", return_value=[project]), \
                 mock.patch("collect.get_repo", return_value={"stargazers_count": 1}), \
                 mock.patch("collect.get_readme_text", return_value="# demo"), \
                 mock.patch("collect.fetch_trending", return_value=[]):
                count = collect.run_week(datetime.date(2026, 8, 3), 10, 15, None, d, os.path.join(d, "data"))
            self.assertGreaterEqual(count, 1)
            self.assertTrue(os.path.exists(os.path.join(d, "2026 08.03-08.09", "index.md")))
            self.assertTrue(os.path.exists(os.path.join(d, "2026 08.03-08.09", "周榜-新建-star.md")))

    def test_run_week_star_delta_keeps_project_info(self):
        project = {
            "name": "demo",
            "full_name": "a/demo",
            "stargazers_count": 10,
            "description": "demo description",
            "html_url": "https://github.com/a/demo",
        }
        with tempfile.TemporaryDirectory() as d:
            data_dir = os.path.join(d, "data")
            os.makedirs(data_dir)
            save_snapshot(os.path.join(data_dir, "star_snapshot.json"), {"a/demo": 5})
            with mock.patch("collect.search_new_repos", return_value=[project]), \
                 mock.patch("collect.get_repo", return_value={"stargazers_count": 10}), \
                 mock.patch("collect.get_readme_text", return_value="# demo"), \
                 mock.patch("collect.fetch_trending", return_value=[]):
                collect.run_week(datetime.date(2026, 8, 3), 10, 15, None, d, data_dir)
            growth_file = os.path.join(d, "2026 08.03-08.09", "周榜-star增速.md")
            self.assertTrue(os.path.exists(growth_file))
            with open(growth_file, encoding="utf-8") as f:
                content = f.read()
            self.assertIn("https://github.com/a/demo", content)
            self.assertIn("demo description", content)


if __name__ == "__main__":
    unittest.main()
