import unittest
from county_cost_scenario import county_scenario, county_cost_categories
from county_explanation import explanation_text, LABELS
from burden_framework import evidence_package, methods_text

class CountyExplanationTests(unittest.TestCase):
    def test_exported_county_values_retain_four_explanations_without_new_arithmetic(self):
        for row in county_scenario(perspective='societal'):
            for field,label in LABELS:
                self.assertTrue(row[field])
            self.assertIn('2024',row['reported_cases_context'])
            self.assertIn('n=613',row['published_cost_context'])
            self.assertIn('2016',row['published_cost_context'])
            self.assertIn('No underreporting or inflation adjustment',row['calculation_assumptions'])
            self.assertIn('data/ny_lyme_cases_2024_verification.json',row['provenance'])
            self.assertEqual(row['Illustrative societal amount · 2016 USD'],row['Reported cases · 2024']*2032)
        self.assertEqual(county_cost_categories()[0]['Estimated societal total · 2016 USD'],2153920)
        self.assertIn('original study table',county_scenario()[0]['published_cost_context'])
        mixed=county_scenario(.5)[0]
        self.assertIn('User-selected disseminated share 50%',mixed['calculation_assumptions'])
        self.assertNotIn('No local case-mix adjustment',mixed['calculation_assumptions'])

    def test_methods_export_contains_same_explanations_and_no_patient_records(self):
        package=evidence_package()
        self.assertEqual(len(package['county_illustrations']),2)
        text=methods_text()
        for row in package['county_illustrations']:
            for field,label in LABELS:
                self.assertIn(row[field],text)
        self.assertNotIn('daily_life_observations',package)
        self.assertFalse(package['scope']['patient_entries_included'])
        self.assertEqual(set(package['source_applications']),{s['id'] for s in package['sources']})
