import unittest
from unittest.mock import patch
from pathlib import Path
from streamlit.testing.v1 import AppTest
from homepage_outputs import sample_patient_pdf,sample_county_pdf

class HomepageOutputsTests(unittest.TestCase):
    def test_public_samples_and_navigation(self):
        app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'),default_timeout=60).run()
        self.assertFalse(list(app.exception))
        self.assertTrue(any(x.value=='See how PathwayAI can help' for x in app.subheader))
        labels=[x.label for x in app.get('download_button')]
        self.assertIn('View sample patient summary (PDF)',labels)
        self.assertIn('View sample county brief (PDF)',labels)
        self.assertTrue(any(x.label=='Improved through feedback' for x in app.expander))
        self.assertNotIn('burden_session_record',app.session_state)
        app.button(key='route_county').click().run()
        self.assertFalse(list(app.exception))
        self.assertEqual(len(app.selectbox(key='county_report_county').options),7)
        self.assertTrue(sample_patient_pdf().startswith(b'%PDF'))
        self.assertTrue(sample_county_pdf().startswith(b'%PDF'))

    def test_county_sample_cache_refreshes_with_report_version(self):
        from homepage_outputs import sample_county_pdf, _sample_county_pdf
        _sample_county_pdf.cache_clear()
        try:
            with patch('community_runtime.ensure_current_community_modules'), patch('county_brief_pdf.county_brief_pdf',side_effect=[b'%PDF-old',b'%PDF-new']) as render:
                with patch('county_burden_report.REPORT_VERSION','old'):
                    self.assertEqual(sample_county_pdf(),b'%PDF-old')
                    self.assertEqual(sample_county_pdf(),b'%PDF-old')
                with patch('county_burden_report.REPORT_VERSION','new'):
                    self.assertEqual(sample_county_pdf(),b'%PDF-new')
                self.assertEqual(render.call_count,2)
        finally:
            _sample_county_pdf.cache_clear()
