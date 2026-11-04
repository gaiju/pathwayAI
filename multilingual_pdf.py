"""Embedded-font PDF path for scripts requiring shaping or portable CJK fonts.

All input is escaped as text. Resource fetching is restricted to bundled fonts
and internally generated data images: patient text cannot initiate network reads.
"""
from pathlib import Path
from html import escape
import unicodedata
from urllib.parse import urlsplit, unquote

FONT_DIR = Path(__file__).resolve().parent / 'fonts'
FONTS = {
    'PathwayLatin': 'DejaVuSans.ttf',
    'PathwayArabic': 'NotoSansArabic-Regular.ttf',
    'PathwayIndic': 'NotoSansDevanagari-Regular.ttf',
    'PathwayChinese': 'NotoSansCJKSC-Regular.otf',
    'PathwayKorean': 'NotoSansCJKKR-Regular.otf',
}


def needs_multiscript_pdf(text):
    return any('\u0600' <= c <= '\u08ff' or '\u0900' <= c <= '\u097f'
               or '\u1100' <= c <= '\u11ff' or '\u2e80' <= c <= '\uffef'
               for c in text)


def font_for(char):
    n=ord(char)
    if 0x0600<=n<=0x08ff: return 'PathwayArabic'
    if 0x0900<=n<=0x097f: return 'PathwayIndic'
    if 0x1100<=n<=0x11ff or 0x3130<=n<=0x318f or 0xac00<=n<=0xd7af: return 'PathwayKorean'
    if 0x2e80<=n<=0xffef: return 'PathwayChinese'
    return 'PathwayLatin'


def line_html(line):
    # Group runs, not individual characters: shaping must see connected letters.
    runs=[];family=None;value=''
    for char in line:
        selected=font_for(char)
        # Keep whitespace/numbers/punctuation with adjacent script when possible.
        if (char.isspace() or unicodedata.category(char)[0] in 'NP') and family:
            selected=family
        if selected!=family:
            if value:runs.append('<span style="font-family:'+family+'">'+escape(value)+'</span>')
            family=selected;value=''
        value+=char
    if value:runs.append('<span style="font-family:'+family+'">'+escape(value)+'</span>')
    return ''.join(runs) or '&#160;'


def paragraph_direction(line):
    for char in line:
        direction=unicodedata.bidirectional(char)
        if direction in ('R','AL'):return 'rtl'
        if direction=='L':return 'ltr'
    return 'ltr'


def bundled_resource_fetcher(url):
    from weasyprint import default_url_fetcher
    parsed=urlsplit(url)
    if parsed.scheme=='file':
        path=Path(unquote(parsed.path)).resolve()
        if path.parent==FONT_DIR.resolve() and path.name in FONTS.values():
            return default_url_fetcher(url)
    # Only generated state-badge images may use data URLs; input is escaped.
    if url.startswith('data:image/svg+xml;base64,'):
        return default_url_fetcher(url)
    raise ValueError('PDF resource is not a bundled font or generated badge')


def multiscript_pdf(text, *, state_code=None, footer_label='', link_urls=False):
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    declarations='\n'.join('@font-face{font-family:'+family+';src:url("'+(FONT_DIR/name).as_uri()+'");}' for family,name in FONTS.items())
    css=declarations+'''
    @page {size:A4; margin:42pt 42pt 48pt;
      @bottom-left {content: string(footer);font-family:PathwayLatin;font-size:8pt;color:#163149;}
      @bottom-right {content:counter(page);font-family:PathwayLatin;font-size:8pt;color:#163149;}}
    body {font-family:PathwayLatin;font-size:10pt;line-height:1.5;color:#163149;}
    p {margin:0 0 4pt;white-space:pre-wrap;overflow-wrap:anywhere;}
    p.title {font-size:14pt;line-height:1.4;margin-bottom:12pt;}
    p[dir=rtl] {text-align:right;}
    a {color:#17648a;} .footer {string-set:footer content();height:0;overflow:hidden;}
    img.badge {display:block;max-width:160pt;max-height:80pt;margin-bottom:10pt;}
    '''
    paragraphs=['<div class="footer">'+escape(footer_label)+'</div>']
    for index,line in enumerate(text.splitlines()):
        markup=line_html(line)
        if link_urls and line.startswith('https://') and not any(c.isspace() for c in line):
            markup='<a href="'+escape(line,quote=True)+'">'+markup+'</a>'
        paragraphs.append('<p class="'+('title' if index==0 else 'line')+'" dir="'+paragraph_direction(line)+'">'+markup+'</p>')
        if index==0 and state_code:
            from state_badge import state_badge
            badge=state_badge(state_code)
            if badge is not None:
                import base64
                from reportlab.graphics import renderSVG
                svg=renderSVG.drawToString(badge)
                if isinstance(svg,str):svg=svg.encode()
                paragraphs.append('<img class="badge" src="data:image/svg+xml;base64,'+base64.b64encode(svg).decode()+'">')
    doc='<!doctype html><html><head><meta charset="utf-8"><title>PathwayAI report</title></head><body>'+''.join(paragraphs)+'</body></html>'
    config=FontConfiguration()
    return HTML(string=doc,url_fetcher=bundled_resource_fetcher).write_pdf(stylesheets=[CSS(string=css,font_config=config)],font_config=config)
