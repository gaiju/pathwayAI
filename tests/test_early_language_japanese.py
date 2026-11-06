import io
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from pypdf import PdfReader
from fontTools.ttLib import TTFont
from streamlit.testing.v1 import AppTest
from language_preferences import save_language_choice
from language_organizer import LANGUAGES, FIELDS, AIDS, CONTROLS, translate_notes, bilingual_text
from pdf_report import report_pdf

JP = '日本語 / Japanese'
STORY = '架空の例：Baltimoreで虫に刺されました。検査は陰性でした。225ドルを支払いました。'
RESULT = {'english_translation': 'Fictional example: I was bitten by an insect in Baltimore. The test was negative. I paid 225 dollars.',
          'timeline': {key: {'exposure': 'Baltimore', 'tests': 'Negative; date not reported.', 'support': 'Paid 225 dollars.'}.get(key) for key in FIELDS},
          'uncertainties': ['What was the date of the test?']}

class EarlyLanguageTests(unittest.TestCase):
    def test_preference_does_not_delete_records_or_send_requests(self):
        state = {'preferred_language_widget': JP, 'saved_story_text': STORY,
                 'daily_life_observations': [{'work': 'missed work'}], 'medical88': 225,
                 'translation_result': RESULT, 'translation_source': ('old',)}
        save_language_choice(state, 'preferred_language_widget')
        self.assertEqual(state['saved_notes_language'], JP)
        self.assertEqual(state['notes_language'], JP)
        self.assertEqual(state['saved_story_text'], STORY)
        self.assertEqual(state['medical88'], 225)
        self.assertTrue(state['daily_life_observations'])
        self.assertNotIn('translation_result', state)
        self.assertEqual(len(LANGUAGES), 14)
        self.assertIn(JP, AIDS)
        self.assertIn(JP, CONTROLS)

    def test_early_selection_survives_routes_and_no_automatic_translation(self):
        app = Path(__file__).resolve().parents[1] / 'app.py'
        with patch('language_organizer.translate_notes', return_value=(RESULT, '')) as translate:
            at = AppTest.from_file(str(app), default_timeout=60).run()
            at.selectbox(key='preferred_language_widget').set_value(JP).run()
            at.button(key='route_ongoing').click().run()
            self.assertEqual(at.selectbox(key='notes_language').value, JP)
            at.text_area(key='quick_story_value').set_value(STORY).run()
            self.assertEqual(translate.call_count, 0)
            at.checkbox(key='translation_consent').check().run()
            at.button(key='translate_visit_notes').click().run()
            self.assertEqual(translate.call_count, 1)
            at.sidebar.radio(key='pathway_view').set_value('📊 Community Burden & Action').run()
            at.sidebar.radio(key='pathway_view').set_value('🩹 Tick Bite: What Next?').run()
            self.assertEqual(at.text_area(key='quick_story_value').value, STORY)
            self.assertEqual(at.selectbox(key='notes_language').value, JP)
            self.assertTrue(any(d.key == 'bilingual_download' for d in at.get('download_button')))
            at.selectbox(key='notes_language').set_value('Русский / Russian').run()
            self.assertEqual(at.selectbox(key='notes_language').value, 'Русский / Russian')
            self.assertEqual(at.text_area(key='quick_story_value').value, STORY)
            self.assertFalse(any(d.key == 'bilingual_download' for d in at.get('download_button')))
            self.assertEqual(translate.call_count, 1)
            self.assertFalse(list(at.exception))

    def test_japanese_payload_preserves_original_with_mocked_translation(self):
        def opener(request, **kwargs):
            source = json.loads(json.loads(request.data)['input'][1]['content'])
            self.assertEqual(source['notes'], STORY)
            self.assertEqual(source['language'], JP)
            return io.BytesIO(json.dumps({'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': json.dumps(RESULT)}]}]}).encode())
        result, error = translate_notes(STORY, JP, 'Myself', consent=True, api_key='fake', model='fake', opener=opener)
        self.assertFalse(error)
        self.assertIn('negative', result['english_translation'])
        self.assertIn(STORY, bilingual_text(STORY, JP, 'Myself', result))

    def test_japanese_font_embedded_and_text_extractable(self):
        from multilingual_pdf import FONT_DIR, FONTS
        font = TTFont(FONT_DIR / FONTS['PathwayJapanese'])
        self.assertTrue(all(ord(c) in font.getBestCmap() for c in STORY if not c.isspace()))
        pdf = report_pdf('PathwayAI\n'+STORY, source_language=JP)
        reader = PdfReader(io.BytesIO(pdf))
        text = ''.join(page.extract_text() for page in reader.pages)
        self.assertIn('検査は陰性', text)
        fonts = reader.pages[0]['/Resources']['/Font'].get_object()
        jp = [f.get_object() for f in fonts.values() if 'PathwayJapanese' in f.get_object().get('/BaseFont', '')]
        self.assertTrue(jp)
        descriptor = jp[0]['/DescendantFonts'][0].get_object()['/FontDescriptor'].get_object()
        self.assertTrue('/FontFile2' in descriptor or '/FontFile3' in descriptor)
