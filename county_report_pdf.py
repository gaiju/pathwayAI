"""Structured public county brief; patient report rendering stays unchanged."""
from io import BytesIO
from xml.sax.saxutils import escape


def county_report_pdf(report):
    from pdf_report import _fonts
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
    _fonts()
    navy=colors.HexColor('#163149');cyan=colors.HexColor('#eaf5fa')
    body=ParagraphStyle('CountyBody',fontName='PathwayUnicodeV2',fontSize=9,leading=12,textColor=navy,spaceAfter=5)
    small=ParagraphStyle('CountySmall',parent=body,fontSize=7.5,leading=10,spaceAfter=3)
    heading=ParagraphStyle('CountyHeading',parent=body,fontSize=11,leading=15,spaceBefore=9,spaceAfter=6)
    title=ParagraphStyle('CountyTitle',parent=body,fontSize=19,leading=24,spaceAfter=8)
    flow=[]
    def para(text,style=body):
        return Paragraph(escape(str(text)),style)
    def add(text,style=body):flow.append(para(text,style))
    def table(rows,widths):
        items=[[para(v,small) for v in row] for row in rows]
        t=Table(items,colWidths=widths,hAlign='LEFT',repeatRows=1)
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),cyan),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.7,navy),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#d7e1e7')),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
        flow.append(t);flow.append(Spacer(1,6))
    def value(v):return 'Not available' if v is None else f'{v:,.0f}'
    r=report
    add('PathwayAI | Hudson Valley',heading)
    add(r['county']+' County\nLyme Burden & Action Brief',title)
    add('Public evidence for a practical support discussion · Version '+r['report_version'],small)
    add('Prepared: '+r['prepared_date']+' · Surveillance: 2024 · Study costs: 2016 dollars',small)
    add('Starting point for a county discussion. Newer official county releases have not been verified for this brief.',small)
    add('1. OBSERVED PUBLIC EVIDENCE',heading)
    table([['Area','Reported cases · 2024','Reported rate per 100,000']]+[[x['county'],f"{x['reported_cases']:,}",f"{x['reported_rate']:g}"] for x in r['comparison']],[205,140,166])
    add('County of residence, not exposure location. '+r['denominator_status'],small)
    add('2. STUDY-BASED ECONOMIC ILLUSTRATION',heading)
    table([['Calculation · original 2016 dollars','Illustrative amount'],[f"{r['reported_cases']:,} reported cases × USD {r['study_societal_mean_usd']:,}",f"USD {r['illustrative_total_2016_usd']:,.0f}"]],[345,166])
    add('Hook et al. (2022): '+r['study_population']+' '+r['cost_perspective'],small)
    add(r['transfer_assumption']+' '+r['other_assumptions'],small)
    add(r['cost_currency_note'],small)
    if r['inflation']:
        m=r['inflation']
        add(f"Optional purchasing-power comparison: USD {m['restated_total_usd']:,.0f} in 2025 dollars. Factor {float(m['factor']):.9f}. General inflation using 11 available 2025 months; October missing, no imputation. Not a verified official annual-average restatement.",small)
    context=r['local_context'];h=context['healthcare'];language=context['language']
    add('LOCAL RESOURCE AND LANGUAGE CONTEXT',heading)
    table([['General healthcare resources · 2023','Count'],['Primary-care physicians',value(h['pcp'])],['Hospitals',value(h['hosp'])],['Hospital beds',value(h['beds'])]],[345,166])
    add('HRSA AHRF resource counts do not establish Lyme expertise, current staffing or available appointments. '+h['status'],small)
    add(f"Language other than English at home: {language['percent']:g}% of residents age 5+, ACS 2020–2024. This is not a measure of English proficiency or interpreter demand.",small)
    add('3. ADDITIONAL BURDEN TO MEASURE',heading)
    add('Work changes, unpaid care, travel and daily-life limitations matter. The selected study population does not represent every local household. Continuing costs, Lyme-attributable disability and local unmet support needs remain unmeasured here.',small)
    flow.append(PageBreak())
    add('From evidence to a support question',title)
    add('4. SUPPORT DECISION TO EXPLORE',heading)
    plan=r['planning'];add(r['priority'],heading)
    add('Question: '+plan['decision'])
    add('Possible response: '+plan['action'])
    add('Potential partners to approach: '+plan['participants'],small)
    add('Proposed actions for local review—not findings about demand, committed partners or a funded service.',small)
    add('5. CHECK FEASIBILITY BEFORE A PILOT',heading)
    for item in r['feasibility_checks']:add('• '+item,small)
    add('6. AGREE ON FOLLOW-UP',heading)
    add('Candidate measures: '+plan['measure'],small)
    add(r['evaluation'],small)
    add('PUBLISHED AND PATIENT-REPORTED BURDEN',heading)
    for item in r['social_burden']:add('• '+item,small)
    add('SOURCES AND METHODS',heading)
    for i,source in enumerate(r['sources'],1):
        url=source['url']
        flow.append(Paragraph(f'{i}. {escape(source["purpose"])} · {escape(source["period"])} · <link href="{escape(url)}" color="#17648a"><u>Open source</u></link>',small))
    if r['inflation']:
        m=r['inflation'];flow.append(Paragraph('CPI: <link href="'+escape(m['source_url'])+'" color="#17648a"><u>FRED / BLS CPI-U source</u></link>. Available-month means: '+escape(m['base_index'])+' (2016) and '+escape(m['target_index'])+' (2025).',small))
    add('The source ledger and CSV retain source URLs, reporting periods, review status, calculation assumptions and inflation provenance.',small)
    add(r['privacy'],small)
    add('Public-data demonstration. No county or organizational endorsement is implied.',small)
    out=BytesIO()
    def footer(canvas,doc):
        canvas.saveState();canvas.setFont('PathwayUnicodeV2',7)
        canvas.setFillColor(navy)
        canvas.drawString(42,25,'PathwayAI | County public-data planning brief')
        canvas.drawRightString(A4[0]-42,25,str(doc.page));canvas.restoreState()
    SimpleDocTemplate(out,pagesize=A4,leftMargin=42,rightMargin=42,topMargin=32,bottomMargin=42,
                      title=r['county']+' County Lyme Burden & Action Brief',author='PathwayAI').build(flow,onFirstPage=footer,onLaterPages=footer)
    return out.getvalue()
