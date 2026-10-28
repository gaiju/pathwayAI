import csv
import io
import json
from pathlib import Path
import unittest

from burden_framework import evidence_package, evidence_rows, impact_inventory, csv_bytes, methods_text


class BurdenFrameworkTests(unittest.TestCase):
    def test_cost_perspectives_and_time_horizons_stay_distinct_in_export(self):
        package = evidence_package()
        rows = package['measures']
        sources = {s['id'] for s in package['sources']}
        for row in rows:
            self.assertIn(row['source_id'], sources)
            self.assertTrue(row['source_url'].startswith('https://'))
            self.assertTrue(row['period'])
            self.assertTrue(row['interpretation'])
        societal = [r for r in rows if r['perspective'] == 'Societal']
        medical = [r for r in rows if r['source_id'] == 'adrion2015']
        self.assertTrue(all(r['dollar_year'] == 2016 for r in societal))
        self.assertTrue(all(r['dollar_year'] == 'Not established from reviewed text' for r in medical))
        self.assertEqual({r['value'] for r in medical}, {2968, 3798})
        self.assertFalse(package['scope']['current_national_estimate'])
        self.assertIsNone(package['scope']['global_cost_total'])
        self.assertIsNone(package['scope']['county_lyme_disability_estimate'])
        self.assertFalse(package['scope']['patient_entries_included'])

    def test_csv_retains_scope_and_does_not_create_a_combined_total(self):
        parsed = list(csv.DictReader(io.StringIO(csv_bytes(evidence_rows()).decode('utf-8-sig'))))
        self.assertEqual(len(parsed), len(evidence_rows()))
        self.assertTrue(all('interpretation' in row and row['dollar_year'] for row in parsed))
        self.assertNotIn('combined_total', json.dumps(evidence_package()))
        self.assertIn('Do not add', methods_text())
        self.assertEqual(len(impact_inventory()), 6)

    def test_national_tab_renders_with_private_story_kept_out_of_evidence_package(self):
        from streamlit.testing.v1 import AppTest
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'), default_timeout=60).run()
        at.button(key='route_ongoing').click().run()
        secret = 'SYNTHETIC_PRIVATE_STORY_SENTINEL_NOT_FOR_PUBLIC_EXPORT'
        at.text_area(key='quick_story_value').set_value(secret).run()
        at.button(key='patient_to_community').click().run()
        self.assertFalse(list(at.exception))
        self.assertEqual(at.tabs[0].label, 'Region')
        self.assertTrue(any('$345–968 million' == item.value for item in at.metric))
        self.assertNotIn(secret, json.dumps(evidence_package()))
        self.assertNotIn(secret, methods_text())
        labels = {item.label for item in at.get('download_button')}
        self.assertIn('Download U.S. burden evidence and methods', labels)
        self.assertIn('Download reproducible evidence package', labels)
