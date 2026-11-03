import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest
from homepage_outputs import sample_patient_pdf,sample_county_pdf

class HomepageOutputsTests(unittest.TestCase):
    def test_public_samples_and_navigation(self):
        app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'),default_timeout=60).run()
        self.assertFalse(list(app.exception))
        self.assertTrue(any(x.value=='See what you can take away' for x in app.subheader))
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
