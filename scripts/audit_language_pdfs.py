import json
from pathlib import Path
from pdf_report import report_pdf, _fonts, _markup
from reportlab.pdfbase import pdfmetrics
samples={
'English':'I found a tick. My test result was negative. I paid $225.',
'Spanish':'Encontré una garrapata. La prueba fue negativa. Pagué $225.',
'Chinese':'我发现了一只蜱虫。检查结果为阴性。我支付了225美元。',
'French':'J’ai trouvé une tique. Le résultat était négatif. J’ai payé 225 dollars.',
'Haitian_Creole':'Mwen jwenn yon tik. Rezilta tès la te negatif. Mwen peye 225 dola.',
'Arabic':'وجدت قرادة. كانت نتيجة الفحص سلبية. دفعت 225 دولارًا.',
'Vietnamese':'Tôi bị ve cắn. Kết quả xét nghiệm âm tính. Tôi đã trả 225 đô la.',
'Tagalog':'May nakita akong garapata. Negatibo ang resulta ng pagsusuri. Nagbayad ako ng 225 dolyar.',
'Korean':'진드기를 발견했습니다. 검사 결과는 음성이었습니다. 225달러를 지불했습니다.',
'Russian':'Меня укусил клещ. Результат анализа отрицательный. Я заплатил 225 долларов.',
'Portuguese':'Encontrei uma carraça. O resultado do exame foi negativo. Paguei 225 dólares.',
'Hindi':'मुझे एक टिक मिला। जाँच का परिणाम नकारात्मक था। मैंने 225 डॉलर दिए।'
}
_fonts();glyphs=pdfmetrics.getFont('PathwayUnicodeV2').face.charToGlyph
rows=[];out=Path('docs/review/language_pdf_audit')
for name,text in samples.items():
 routed=[c for c in text if '\u2e80'<=c<='\uffef']
 missing=sorted(set(c for c in text if not c.isspace() and c not in routed and ord(c) not in glyphs))
 row={'language':name,'sample':text,'missing_primary_font_characters':missing,'characters_routed_to_chinese_font':len(routed),'pdf':name+'.pdf'}
 if name=='Arabic':row['additional_concern']='Arabic shaping and right-to-left ordering are not configured in the current renderer.'
 if name=='Korean':row['additional_concern']='Hangul is routed to the Chinese CID font rather than a bundled Korean font; requires visual verification.'
 if name=='Chinese':row['additional_concern']='Chinese CID font is referenced, not embedded; cross-viewer appearance requires testing.'
 if name=='Hindi':row['additional_concern']='Devanagari characters absent from bundled font; Indic shaping is not configured.'
 (out/(name+'.pdf')).write_bytes(report_pdf('PathwayAI | Font-display audit\nSynthetic test text — not a patient record\n'+name+'\n'+text+'\n\nOriginal and English side by side in sequence:\n'+text+'\nI found a tick. The test was negative. I paid $225.'))
 rows.append(row)
(out/'results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
for row in rows:print(row['language'],'missing:',len(row['missing_primary_font_characters']),row.get('additional_concern','Primary sample characters covered; visual check pending.'))
