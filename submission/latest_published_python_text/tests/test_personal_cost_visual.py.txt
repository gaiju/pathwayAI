import unittest
from personal_cost_visual import personal_cost_svg


class PersonalCostVisualTests(unittest.TestCase):
    def test_missing_is_not_zero_and_units_are_separate(self):
        svg = personal_cost_svg(100, None, 3, 8, 600)
        self.assertNotIn("Recorded payments: $100", svg)
        self.assertIn("Add when known", svg)
        self.assertIn("3 days", svg)
        self.assertIn("8 hours", svg)
        self.assertIn("$600.00 (shown separately)", svg)

    def test_totals_include_only_payments_and_escape_period(self):
        svg = personal_cost_svg(100, 25, 3, 8, 600, '<script>')
        self.assertIn("Recorded payments: $125.00", svg)
        self.assertNotIn("$725.00", svg)
        self.assertIn("&lt;script&gt;", svg)
        self.assertNotIn("<script>", svg)
