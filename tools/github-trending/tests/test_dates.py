import datetime
import unittest

from dates import week_folder, week_ranges, month_label, next_week_monday


class TestDates(unittest.TestCase):
    def test_week_folder_full_week(self):
        self.assertEqual(week_folder(datetime.date(2026, 1, 5), datetime.date(2026, 1, 11)), "2026 01.05-01.11")

    def test_week_folder_partial_first_week(self):
        self.assertEqual(week_folder(datetime.date(2026, 1, 1), datetime.date(2026, 1, 4)), "2026 01.01-01.04")

    def test_week_ranges_from_jan1(self):
        ranges = week_ranges(datetime.date(2026, 1, 1), datetime.date(2026, 1, 12))
        self.assertEqual(ranges[0], (datetime.date(2026, 1, 1), datetime.date(2026, 1, 4)))
        self.assertEqual(ranges[1], (datetime.date(2026, 1, 5), datetime.date(2026, 1, 11)))

    def test_month_label(self):
        self.assertEqual(month_label(datetime.date(2026, 1, 10)), "2026-01")

    def test_next_week_monday(self):
        self.assertEqual(next_week_monday(datetime.date(2026, 8, 9)), datetime.date(2026, 8, 10))


if __name__ == "__main__":
    unittest.main()
