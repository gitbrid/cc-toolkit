import os
import tempfile
import unittest

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


if __name__ == "__main__":
    unittest.main()
