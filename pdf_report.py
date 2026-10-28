"""Readable, paginated PDFs for user-reviewed reports; no external service."""
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape
from functools import lru_cache

PDF_FONT_REVISION = 2


@lru_cache(maxsize=1)
def _fonts():
    import reportlab
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    # Bundle extended Latin coverage so Vietnamese accents survive cloud exports.
    font_path = Path(__file__).parent / 'fonts' / 'DejaVuSans.ttf'
    if not font_path.exists():
        raise RuntimeError('The bundled multilingual PDF font is missing. Please restore fonts/DejaVuSans.ttf.')
    pdfmetrics.registerFont(TTFont('PathwayUnicodeV2', str(font_path)))
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))


def _markup(line):
    # Keep Chinese alongside English instead of replacing Chinese with boxes.
    chunks=[]
    for char in line:
        safe=escape(char)
        if '\u2e80' <= char <= '\uffef':
            safe='<font name="STSong-Light">'+safe+'</font>'
        chunks.append(safe)
    return ''.join(chunks) or '&#160;'


def report_pdf(text, *, state_code=None):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    _fonts()
    output=BytesIO()
    style=ParagraphStyle('Report',fontName='PathwayUnicodeV2',fontSize=10,leading=15,
                         textColor=colors.HexColor('#163149'),splitLongWords=True,wordWrap='CJK')
    title=ParagraphStyle('ReportTitle',parent=style,fontSize=14,leading=20,spaceAfter=12)
    flow=[]
    for index,line in enumerate(text.splitlines()):
        flow.append(Paragraph(_markup(line),title if index==0 else style))
        flow.append(Spacer(1,4 if line else 7))
        if index == 0 and state_code:
            from state_badge import state_badge
            badge = state_badge(state_code)
            if badge is not None:
                flow.extend([badge, Spacer(1,10)])
    def footer(canvas,doc):
        canvas.saveState()
        canvas.setFont('PathwayUnicodeV2',8)
        canvas.drawString(42,26,'PathwayAI | Reviewed personal record / educational material')
        canvas.drawRightString(A4[0]-42,26,str(doc.page))
        canvas.restoreState()
    SimpleDocTemplate(output,pagesize=A4,leftMargin=42,rightMargin=42,topMargin=42,
                      bottomMargin=45,title='PathwayAI report',author='PathwayAI').build(flow,onFirstPage=footer,onLaterPages=footer)
    return output.getvalue()
