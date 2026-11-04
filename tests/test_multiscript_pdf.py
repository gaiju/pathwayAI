import unittest
from io import BytesIO
from pypdf import PdfReader
from pathlib import Path
from urllib.parse import quote
from fontTools.ttLib import TTFont
from multilingual_pdf import (FONT_DIR,FONTS,font_for,line_html,paragraph_direction,
                              needs_multiscript_pdf,bundled_resource_fetcher)
from pdf_report import report_pdf

class MultiscriptPdfTests(unittest.TestCase):
    samples={
        'Chinese':'我发现了一只蜱虫。检查结果为阴性。',
        'Korean':'진드기를 발견했습니다. 검사 결과는 음성이었습니다.',
        'Arabic':'وجدت قرادة. كانت نتيجة الفحص سلبية. دفعت 225 دولارًا.',
        'Indic':'मुझे एक टिक मिला। जाँच का परिणाम नकारात्मक था।',
    }

    def test_selected_font_covers_each_sample_and_is_embedded(self):
        for script,text in self.samples.items():
            with self.subTest(script=script):
                font=TTFont(FONT_DIR/FONTS['Pathway'+script])
                cmap=font.getBestCmap()
                self.assertTrue(all(ord(c) in cmap for c in text if not c.isspace()))
                pdf=report_pdf('PathwayAI\n'+text)
                self.assertTrue(pdf.startswith(b'%PDF'))
                reader=PdfReader(BytesIO(pdf))
                fonts=reader.pages[0]['/Resources']['/Font'].get_object()
                selected=[f.get_object() for f in fonts.values() if 'Pathway'+script in f.get_object().get('/BaseFont','')]
                self.assertTrue(selected)
                descendant=selected[0]['/DescendantFonts'][0].get_object()
                descriptor=descendant['/FontDescriptor'].get_object()
                self.assertTrue('/FontFile2' in descriptor or '/FontFile3' in descriptor)

    def test_runs_and_bidirectional_paragraphs(self):
        self.assertEqual(paragraph_direction('وجدت قرادة 225'),'rtl')
        self.assertEqual(paragraph_direction('English العربية'),'ltr')
        self.assertEqual(font_for('한'),'PathwayKorean')
        self.assertIn('وجدت قرادة',line_html('وجدت قرادة'))
        self.assertEqual(line_html('وجدت قرادة').count('<span'),1)
        for text in self.samples.values():self.assertTrue(needs_multiscript_pdf(text))
        self.assertFalse(needs_multiscript_pdf('Тест отрицательный. Très bien. Tiếng Việt.'))

    def test_text_is_escaped_and_fetch_is_allowlisted(self):
        html=line_html('<img src="https://invalid.example/leak"> العربية')
        self.assertNotIn('<img',html)
        self.assertIn('&lt;',html)
        for url in ['https://invalid.example/leak','http://localhost:8000','file:///etc/passwd','file:///tmp/other.ttf']:
            with self.assertRaises(ValueError):bundled_resource_fetcher(url)
        response=bundled_resource_fetcher((FONT_DIR/FONTS['PathwayArabic']).as_uri())
        self.assertIsNotNone(response)

    def test_mixed_wrapping_badge_and_link(self):
        text='PathwayAI\n'+('\n'.join(self.samples.values())+'\n')*40+'https://www.cdc.gov/lyme/'
        pdf=report_pdf(text,state_code='NY',link_urls=True)
        self.assertTrue(pdf.startswith(b'%PDF'))
        reader=PdfReader(BytesIO(pdf))
        links=[a.get_object().get('/A',{}).get('/URI') for page in reader.pages for a in page.get('/Annots',[])]
        self.assertIn('https://www.cdc.gov/lyme/',links)
        self.assertGreater(len(reader.pages),1)
