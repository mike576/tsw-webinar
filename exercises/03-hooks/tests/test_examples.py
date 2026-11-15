import unittest
from datetime import datetime

from cronnext import next_run


class Examples(unittest.TestCase):
    def test_every_minute(self):
        self.assertEqual(next_run("* * * * *", datetime(2026, 9, 7, 10, 0, 30)), datetime(2026, 9, 7, 10, 1))

    def test_daily_noon(self):
        self.assertEqual(next_run("0 12 * * *", datetime(2026, 9, 7, 8, 0)), datetime(2026, 9, 7, 12, 0))

    def test_bad_minute(self):
        with self.assertRaises(ValueError):
            next_run("60 * * * *", datetime(2026, 9, 7))


if __name__ == "__main__":
    unittest.main()
