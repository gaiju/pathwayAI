import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import zipfile

from community_action_summary import (AUDIENCE_ACTIONS, EVIDENCE_TYPES, SURVEY_CONTEXT,
                                      audience_actions, healthcare_context)
from county_burden_report import build_report, report_text, report_csv_rows
from community_action import ACTION_OPTIONS
from pdf_report import report_pdf


class CommunitySummaryTests(unittest.TestCase):
    def test_hrsa_uses_selected_county_and_missing_is_not_zero(self):
        for county, expected in [('Dutchess', [233, 2, 404]), ('Orange', [294, 6, 1111])]:
            data = healthcare_context(county)
            self.assertEqual(list(data['indicators'].values()), expected)
            self.assertEqual(data['year'], 2023)
        with TemporaryDirectory() as folder:
            path = Path(folder) / 'ahrf.zip'
            missing = healthcare_context('Dutchess', str(path))
            self.assertTrue(all(v is None for v in missing['indicators'].values()))
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('AHRF2025.csv', 'fips_st_cnty,phys_nf_prim_care_pc_exc_rsdt_23,hosp_23,hosp_beds_23\n36027,,0,-1\n')
            healthcare_context.cache_clear()
            mixed = healthcare_context('Dutchess', str(path))
            self.assertEqual(list(mixed['indicators'].values()), [None, 0, None])
            with patch('county_burden_report.healthcare_context', return_value=missing):
                self.assertIn('Primary-care physicians: Not available', report_text(build_report('Dutchess', next(iter(ACTION_OPTIONS)))))
        healthcare_context.cache_clear()

    def test_reports_follow_audience_and_keep_evidence_separate(self):
        for audience in AUDIENCE_ACTIONS:
            actions = audience_actions(audience)
            self.assertEqual(len(actions), 3)
            r = build_report('Orange', 'Getting to care', audience=audience)
            self.assertEqual(r['illustrative_total_2016_usd'], 964 * 2032)
            self.assertEqual(r['audience_actions'], actions)
            self.assertNotIn('patient_reported_context', r)
            self.assertIn('No county-specific', r['local_patient_reports_status'])
            text = report_text(r)
            for action in actions:
                self.assertIn(action, text)
            self.assertNotIn('33 respondents', text)
            self.assertNotIn('2026-10-03', text)
            self.assertIn('Resident', text.title())
            self.assertIn('2016 dollars', text)
            self.assertNotIn('patient_reported_context', report_csv_rows(r)[0])
            self.assertIn('small, self-selected', SURVEY_CONTEXT['sampling'].lower())
            self.assertEqual(len(EVIDENCE_TYPES), 4)
            self.assertTrue(report_pdf(text, footer_label='PathwayAI | County public-data planning brief', link_urls=True).startswith(b'%PDF'))
        with self.assertRaises(ValueError):
            audience_actions('unknown')

    def test_ui_audience_changes_preserve_comparisons_downloads_and_private_notes(self):
        from streamlit.testing.v1 import AppTest
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'), default_timeout=60).run()
        at.session_state['saved_story_text'] = 'PRIVATE_SENTINEL'
        at.session_state['daily_life_observations'] = [{'support_needed': 'PRIVATE_OBSERVATION'}]
        at.button(key='route_county').click().run()
        self.assertFalse(list(at.exception))
        self.assertTrue(any('From Lyme Disease Burden to Community Action' in item.value for item in at.subheader))
        at.selectbox(key='community_action_audience').set_value('Patient advocacy organizations').run()
        at.selectbox(key='county_report_county').set_value('Orange').run()
        at.selectbox(key='county_report_priority').set_value('Getting to care').run()
        self.assertFalse(list(at.exception))
        self.assertEqual(at.multiselect(key='county_comparisons_selected').value, ['Reported Lyme rate', 'Language context'])
        self.assertTrue(any('Audience: Patient advocacy organizations' in item.value for item in at.markdown))
        self.assertTrue(any(d.label == 'Download county burden & action report (PDF)' for d in at.get('download_button')))
        r = build_report('Orange', 'Getting to care', audience='Patient advocacy organizations')
        serialized = json.dumps(report_csv_rows(r)) + report_text(r)
        self.assertNotIn('PRIVATE_SENTINEL', serialized)
        self.assertNotIn('PRIVATE_OBSERVATION', serialized)
        self.assertEqual(at.session_state['saved_story_text'], 'PRIVATE_SENTINEL')
