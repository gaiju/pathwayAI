import unittest
from unittest.mock import patch
from report_download import TAGLINE, branded_download_button
from outdoor_plan import outdoor_plan_text


class ReportDownloadTests(unittest.TestCase):
    def test_text_download_is_branded_pdf(self):
        with patch('streamlit.download_button') as download, patch('pdf_report.report_pdf', return_value=b'%PDF-test') as render:
            branded_download_button('Download', '原始笔记'.encode(), mime='text/plain', file_name='Notes.txt')
            self.assertEqual(render.call_args.args[0], TAGLINE + '\n\n原始笔记')
            self.assertEqual(download.call_args.args[1], b'%PDF-test')
            self.assertEqual(download.call_args.kwargs['file_name'], 'Notes.pdf')
            self.assertEqual(download.call_args.kwargs['mime'], 'application/pdf')

    def test_csv_branding_preserves_data_columns(self):
        import csv,io
        with patch('streamlit.download_button') as download:
            branded_download_button('Download', b'county,cost\nExample,10\n', mime='text/csv')
            rows=list(csv.DictReader(io.StringIO(download.call_args.args[1].decode('utf-8-sig'))))
            self.assertEqual(rows[0]['county'],'Example')
            self.assertEqual(rows[0]['cost'],'10')
            self.assertEqual(rows[0]['PathwayAI report'],TAGLINE)

    def test_outdoor_plan_is_educational_and_has_sources(self):
        plan = outdoor_plan_text('Example destination', 'June', 'Gardening or yard work', created='2026-10-20')
        for text in [TAGLINE, 'Example destination', 'June', 'Gardening or yard work', '72 hours', 'not a diagnosis', 'https://www.cdc.gov/', '2026-10-20']:
            self.assertIn(text, plan)
