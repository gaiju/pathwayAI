"""Visible evidence limits must survive exports and preserve unknown versus zero."""
import json
import unittest
from copy import deepcopy
from county_burden_report import build_report, evidence_gaps, report_text, report_csv_rows

class ReviewReadyGapTests(unittest.TestCase):
    def test_county_specific_missingness_survives_exports(self):
        report = build_report('Putnam', 'Getting to care')
        self.assertTrue(any('language spoken at home' in gap for gap in report['evidence_gaps']))
        self.assertIn('What we still need to know', report_text(report))
        self.assertEqual(json.loads(report_csv_rows(report)[0]['evidence_gaps']), report['evidence_gaps'])
        self.assertNotIn('33 respondents', report_text(report))

    def test_zero_is_not_a_missing_value(self):
        report = deepcopy(build_report('Dutchess', 'Getting to care'))
        report['reported_cases'] = 0
        report['reported_rate_per_100000'] = 0
        report['additional_public_context']['language_context']['value'] = 0
        for row in report['additional_public_context']['socioeconomic_context']:
            row['value'] = 0
        self.assertFalse(any('Not available' in gap for gap in evidence_gaps(report)))
        report['reported_cases'] = None
        self.assertTrue(any('2024 reported case count' in gap for gap in evidence_gaps(report)))
