import datetime
import os
import tempfile
import unittest
from unittest import mock

import collect


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


if __name__ == "__main__":
    unittest.main()
