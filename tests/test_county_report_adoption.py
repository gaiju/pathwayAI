import json
import unittest
from pathlib import Path
from unittest.mock import patch
from county_burden_report import build_report, report_text, report_csv_rows, load_county_registry
from county_executive_pdf import executive_pdf


class CountyAdoptionTests(unittest.TestCase):
    def test_source_metadata_and_local_notes_are_separate_and_not_persistent(self):
        r = build_report('Dutchess', 'Getting to care', local_context={
            'notes': '<unverified local planning>', 'unexpected': 'IGNORE'})
        text = report_text(r)
        self.assertIn('LOCALLY COMPLETED PLANNING — UNVERIFIED', text)
        self.assertIn('<unverified local planning>', text)
        self.assertNotIn('IGNORE', text)
        self.assertEqual(build_report('Dutchess', 'Getting to care')['local_context']['notes'], '')
        self.assertEqual(r['sources'][1]['checked_on'], '2026-10-14')
        self.assertIn('Rate per 100,000', r['sources'][1]['title'])
        self.assertEqual(len(r['sources'][0]['supplied_file_sha256']), 64)
        self.assertEqual(json.loads(report_csv_rows(r)[0]['local_context'])['notes'],
                         '<unverified local planning>')

    def test_an_added_county_uses_registry_sources_not_pilot_numbers(self):
        import county_burden_report as module
        config = dict(module.COUNTY_REGISTRY['Dutchess'], name='Example',
                      state='Example State', fips='99001', county_key='Example',
                      state_rate_key='EXAMPLE TOTAL', year=2023)
        original = module._load
        def load(name):
            result = original(name)
            if 'verified_lyme_case_counts' in result:
                result['verified_lyme_case_counts']['Example'] = 0
            if 'verified_rates' in result:
                result['verified_rates'].update({'Example': 0, 'EXAMPLE TOTAL': 10})
            return result
        with patch.dict(module.COUNTY_REGISTRY, {'Example': config}), \
             patch.dict(module.COUNTIES, {'Example': '99001'}), patch.object(module, '_load', load):
            r = build_report('Example', 'Getting to care')
        self.assertEqual((r['state'], r['case_year'], r['reported_cases']),
                         ('Example State', 2023, 0))
        self.assertEqual(r['illustrative_total_2016_usd'], 0)
        with self.assertRaises(ValueError):
            build_report('Unavailable', 'Getting to care')

    def test_executive_is_one_page_for_all_priorities_and_local_notes(self):
        import re
        from unittest.mock import patch
        from reportlab.pdfgen import canvas
        from community_action import ACTION_OPTIONS
        for county in load_county_registry():
            for priority in ACTION_OPTIONS:
                r = build_report(county, priority, True, {'notes': 'X' * 800})
                pdf = executive_pdf(r)
                self.assertTrue(pdf.startswith(b"%PDF-"))
                self.assertEqual(len(re.findall(rb"/Type\s*/Page\b", pdf)), 1)
