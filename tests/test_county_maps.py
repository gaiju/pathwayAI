import unittest

from county_maps import county_key, rate_color, rate_data


class RateMapTests(unittest.TestCase):
    def test_county_rates_match_checked_table_and_exclude_nyc_aggregation(self):
        data = rate_data()
        rates = data["county_rates"]
        self.assertEqual(len(rates), 57)
        self.assertEqual(rates["DUTCHESS"], 355.5)
        self.assertEqual(rates["ORANGE"], 237.0)
        self.assertEqual(max(rates, key=rates.get), "ESSEX")
        self.assertNotIn("NYC", rates)
        self.assertEqual(county_key("St. Lawrence"), county_key("ST LAWRENCE"))

    def test_higher_rate_is_darker_and_unknown_stays_distinct(self):
        low = rate_color(50, 535.5)
        high = rate_color(400, 535.5)
        luminance = lambda color: sum(int(color[i:i + 2], 16) for i in (1, 3, 5))
        self.assertLess(luminance(high), luminance(low))
        self.assertNotEqual(rate_color(None, 535.5), rate_color(0, 535.5))
