import unittest
from pathlib import Path
from unittest.mock import patch
from report_download import compact_personal_text, branded_download_button

class PdfFeedbackTests(unittest.TestCase):
    def test_russian_and_vietnamese_use_embedded_font_with_required_glyphs(self):
        from pdf_report import report_pdf, _fonts
        from reportlab.pdfbase import pdfmetrics
        _fonts()
        text='Меня укусил клещ. Анализ отрицательный. Tôi bị ve cắn.'
        glyphs=pdfmetrics.getFont('PathwayUnicodeV2').face.charToGlyph
        self.assertTrue(all(ord(c) in glyphs for c in text if not c.isspace()))
        data=report_pdf('PathwayAI\n'+text)
        self.assertTrue(data.startswith(b'%PDF'))
        self.assertIn(b'/FontFile2',data)

    def test_compact_keeps_originals_negative_findings_zero_and_periods(self):
        text='PathwayAI\n\nSTORY\nMY OWN WORDS\nExample: Not reported\n\nSTRUCTURED JOURNEY\nExposure: Not reported\nTests: Negative\n\nBURDEN\nPeriod: Not reported\nMedical: $0.00\n\nQUESTION FOR MY CLINICIAN\nNot reported\n\nORIGINAL NOTES (UNCHANGED)\nТест отрицательный.\nExample: Not reported'
        result=compact_personal_text(text)
        for expected in ['Example: Not reported','Tests: Negative','Medical: $0.00','Period: Not reported','Тест отрицательный.']:
            self.assertIn(expected,result)
        self.assertNotIn('Exposure: Not reported',result)
        self.assertNotIn('QUESTION FOR MY CLINICIAN',result)
        self.assertIn('Missing information does not mean No',result)
        self.assertEqual(result.count('Example: Not reported'),2)
        with patch('streamlit.download_button'),patch('pdf_report.report_pdf',return_value=b'%PDF') as render:
            branded_download_button('Download',text.encode(),mime='text/plain',file_name='Personal.txt',compact_personal_pdf=True)
            self.assertNotIn('Exposure: Not reported',render.call_args.args[0])

    def test_period_is_explicit_and_seven_day_option_does_not_autofill(self):
        from streamlit.testing.v1 import AppTest
        at=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'),default_timeout=60).run()
        at.button(key='route_ongoing').click().run()
        at.number_input(key='medical88').set_value(180.0).run()
        at.number_input(key='other88').set_value(45.0).run()
        self.assertEqual(at.selectbox(key='period88').value,'Not reported')
        self.assertTrue(any('dated observation’s period is separate' in x.value for x in at.warning))
        at.selectbox(key='period88').set_value('Past 7 days').run()
        self.assertIn('COST-AND-TIME PERIOD: Past 7 days',at.text_area(key='summary88_text').value)
        at.radio(key='cost_pdf_layout').set_value('Compact · hide unused fields').run()
        self.assertFalse(list(at.exception))
        self.assertEqual(at.number_input(key='medical88').value,180.0)
        self.assertEqual(at.number_input(key='other88').value,45.0)
