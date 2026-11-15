import unittest
from datetime import date

from invoicing import apply_discounts, business_days, late_fee, parse_amount, split_amount


class TestInvoicing(unittest.TestCase):
    def test_split_even(self):
        self.assertEqual(split_amount(100, [1, 1]), [50, 50])

    def test_split_three_ways(self):
        self.assertEqual(split_amount(100, [1, 1, 1]), [34, 33, 33])

    def test_business_days_one_week(self):
        # Monday 2026-09-07 to Monday 2026-09-14, end exclusive
        self.assertEqual(business_days(date(2026, 9, 7), date(2026, 9, 14)), 5)

    def test_parse_plain(self):
        self.assertEqual(parse_amount("12.50"), 1250)

    def test_parse_currency(self):
        self.assertEqual(parse_amount("EUR 7.00"), 700)

    def test_percent_discount(self):
        self.assertEqual(apply_discounts(10000, [("percent", 10)]), 9000)

    def test_late_fee_small(self):
        self.assertEqual(late_fee(10, 100000), 2000)


if __name__ == "__main__":
    unittest.main()
