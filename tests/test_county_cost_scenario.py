import unittest

from county_cost_scenario import county_scenario, burden_paths


class CountyScenarioTests(unittest.TestCase):
    def test_societal_reference_keeps_perspective_and_price_year(self):
        rows = county_scenario(perspective="societal")
        self.assertEqual(rows[0]["Illustrative societal amount · 2016 USD"], 2153920)
        self.assertEqual(rows[1]["Illustrative societal amount · 2016 USD"], 1958848)
        self.assertEqual(rows[1]["Illustrative amount per 100,000 · 2016 USD"], 481584)
        self.assertEqual(rows[0]["dollar_year"], 2016)
        self.assertNotIn("Illustrative medical amount · 2022 USD", rows[0])
        self.assertIn("still requires verification", rows[0]["case_count_verification"])
        with self.assertRaises(ValueError):
            county_scenario(.5, perspective="societal")

    def test_paths_share_baseline_and_do_not_claim_observed_history(self):
        paths = burden_paths("Dutchess", 2227)
        self.assertEqual(len(paths), 18)
        baseline = [row for row in paths if row["Scenario year"] == 0]
        self.assertEqual({row["Assumed reported cases"] for row in baseline}, {1060})
        unchanged = next(row for row in paths if row["Scenario year"] == 5 and row["Annual change assumption"] == 0)
        higher = next(row for row in paths if row["Scenario year"] == 5 and row["Annual change assumption"] > 0)
        lower = next(row for row in paths if row["Scenario year"] == 5 and row["Annual change assumption"] < 0)
        self.assertLess(lower["Assumed reported cases"], unchanged["Assumed reported cases"])
        self.assertGreater(higher["Assumed reported cases"], unchanged["Assumed reported cases"])
        self.assertTrue(all(row["evidence_type"] == "hypothetical_projection_not_forecast" for row in paths))

    def test_overall_mean_and_population_rate_scaling(self):
        rows = county_scenario()
        self.assertEqual(rows[0]["Illustrative medical amount · 2022 USD"], 1060 * 2227)
        self.assertEqual(rows[1]["Illustrative amount per 100,000 · 2022 USD"], 237 * 2227)
        self.assertIsNone(rows[0]["assumed_disseminated_share"])

    def test_zero_full_and_mixed_shares(self):
        self.assertEqual(county_scenario(0)[0]["Medical reference per episode · 2022 USD"], 695)
        self.assertEqual(county_scenario(1)[0]["Medical reference per episode · 2022 USD"], 6833)
        self.assertEqual(county_scenario(.5)[0]["Medical reference per episode · 2022 USD"], (695 + 6833) / 2)

    def test_invalid_assumptions_fail_and_exports_keep_limits(self):
        for share in (-.1, 1.1, float("nan"), True):
            with self.assertRaises(ValueError):
                county_scenario(share)
        row = county_scenario()[0]
        self.assertIn("illustrative", row["scenario_type"])
        self.assertIn("OOP not added", row["limits"])
        self.assertTrue(row["case_source"].startswith("https://www.health.ny.gov/"))


if __name__ == "__main__":
    unittest.main()
