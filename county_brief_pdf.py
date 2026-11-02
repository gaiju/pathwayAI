"""Numbers-first county brief; existing patient PDF rendering is untouched."""
from io import BytesIO
from xml.sax.saxutils import escape
from pdf_report import _fonts


def county_brief_pdf(r):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    _fonts()
    navy = colors.HexColor('#163b50')
    pale = colors.HexColor('#edf4f7')
    body = ParagraphStyle('CountyBody', fontName='PathwayUnicodeV2', fontSize=9, leading=12, textColor=navy, spaceAfter=5)
    small = ParagraphStyle('CountyNotes', parent=body, fontSize=8, leading=10.5, spaceAfter=4)
    heading = ParagraphStyle('CountyHeading', parent=body, fontSize=11, leading=14, spaceBefore=9, spaceAfter=6, keepWithNext=True)
    title = ParagraphStyle('CountyTitle', parent=body, fontSize=19, leading=24, spaceAfter=7)
    amount = ParagraphStyle('CountyAmount', parent=body, fontSize=23, leading=28, spaceAfter=4)
    flow=[]
    def paragraph(text, style=body): return Paragraph(escape(str(text)), style)
    def add(text, style=body): flow.append(paragraph(text, style))
    def number(value, suffix=''):
        return 'Not available' if value is None else f'{value:,g}'+suffix
    def table(rows, widths, padding=5):
        t=Table([[paragraph(cell, small) for cell in row] for row in rows], colWidths=widths, repeatRows=1, hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),pale),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.6,navy),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#d8e1e5')),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),padding),('BOTTOMPADDING',(0,0),(-1,-1),padding)]))
        flow.extend([t, Spacer(1,4)])
    context=r['additional_public_context']
    sources=list(r['sources'])
    sources += [dict(purpose=x['name'],period='Existing directory; current status requires verification',url=x['url']) for x in context['listed_initiatives']]
    if r['inflation']: sources.append(dict(purpose='BLS CPI-U via supplied FRED file',period='2016 and 2025 available-month comparison',url=r['inflation']['source_url']))
    source_numbers={}
    for source in sources:
        if source['url'] not in source_numbers: source_numbers[source['url']]=len(source_numbers)+1
    cost_refs=[source_numbers[r['sources'][0]['url']], source_numbers[next(x['url'] for x in r['sources'] if 'Societal study mean' == x['purpose'])]]
    if r['inflation']: cost_refs.append(source_numbers[r['inflation']['source_url']])
    add('PathwayAI | '+r['county']+' County', heading)
    add('Lyme Disease Burden & Community Action', title)
    add('Prepared '+r['prepared_date']+' · Public-data planning brief · Version '+r['report_version'], small)
    add('For local planning discussions · Proposed actions for review',small)
    table([['Reported cases · 2024','County rate per 100,000 · 2024','State rate per 100,000 · 2024'],
           [number(r['reported_cases']),number(r['reported_rate_per_100000']),number(r['state_reported_rate_per_100000'])]],[170,170,171])
    add('Illustrative economic burden estimate', heading)
    if r['reported_cases'] is None:
        add('Not available', amount)
        add('Economic total requires a verified case count. No count is reconstructed from the published rate.',small)
    elif r['inflation']:
        add(f"USD {r['inflation']['restated_total_usd']/1_000_000:.2f} million", amount)
        add('Optional 2025 purchasing-power comparison · 11 available CPI months · general inflation', small)
        table([['Original study basis · 2016 dollars','Optional 2025 comparison · approximately 1.34×'],
               [f"USD {r['illustrative_total_2016_usd']/1_000_000:.2f} million",f"USD {r['inflation']['restated_total_usd']/1_000_000:.2f} million"]],[255,256])
    else:
        add(f"USD {r['illustrative_total_2016_usd']/1_000_000:.2f} million", amount)
        add('Original study-dollar basis · 2016 dollars', small)
    add('Study-based illustration, not measured county spending or predicted savings. Sources ['+', '.join(map(str,cost_refs))+']; calculation and methods: page 3.', small)
    add('Mid-Hudson counties and state comparison', heading)
    table([['Area','Reported cases · 2024','Rate per 100,000 · 2024']]+[[x['Area'],number(x['Reported cases']),number(x['Reported cases per 100,000'])] for x in context['comparison']], [205,145,161], padding=2)
    add('All comparison rates use the same NYSDOH 2024 published source and reporting year; reported rates are not personal risk estimates.',small)
    add('Healthcare resources and population context', heading)
    rows=[['Indicator','Value','Period']]
    rows += [[label,number(value),'2023'] for label,value in r['healthcare_context']['indicators'].items()]
    rows += [[('Poverty (population with poverty status determined)' if x['field']=='pers_povty_pct_23' else x['measure']),number(x['value'],'%'),str(x['year'])] for x in context['socioeconomic_context']]
    language=context['language_context']
    rows.append(['Language other than English at home · age 5+',number(language['value'],'%'),'ACS 2020–2024'])
    table(rows,[295,80,136])
    add('General resource/population context, not Lyme-attributable need, appointment availability or interpreter demand. Selected insurance/poverty fields supply no margin of error.',small)
    add('Reported Lyme rates by year · per 100,000 residents',heading)
    if all(row['Reported cases per 100,000'] is None for row in context['rate_trend'][:2]):
        add('2024 rate: '+number(context['rate_trend'][-1]['Reported cases per 100,000'])+' per 100,000. The 2022–2023 rates are not available in the verified source records used for this brief.',small)
    else:
        table([['2022','2023','2024'],[number(row['Reported cases per 100,000']) for row in context['rate_trend']]],[170,170,171])
    add('County of residence, not exposure location. Pre-2022 rates excluded because surveillance definitions changed. Different sources do not establish causes. References and limitations: page 3.',small)
    flow.append(PageBreak())
    add('From evidence to community action',title)
    plan=r['planning']
    add('Support priority: '+r['priority'],heading)
    add('Question: '+plan['decision'])
    add('Possible response: '+plan['action'])
    add('Who could help: '+plan['participants'],small)
    add('Actions to discuss · '+r['audience'],heading)
    for action in r['audience_actions']:add('• '+action)
    add('Four areas for community action',heading)
    for item in r['community_action_areas']:add(item['title']+': '+item['description'],small)
    add('Resident priorities to discuss',heading)
    add('Confirm priorities with residents and caregivers before choosing a response. '+r['local_patient_reports_status'],small)
    add('Before starting a pilot',heading)
    for check in r['feasibility_checks']:add('• '+check,small)
    add('Check whether people received support',heading)
    add('Choose a common follow-up period, such as 30 days. Record the starting situation, help received and needs still unmet. Keep unanswered questions unknown.',small)
    add('For this priority: '+plan['measure'],small)
    add('Further evaluation is needed to establish health benefits or savings. Actions are proposals for local review, not adopted programs or commitments.',small)
    flow.append(PageBreak())
    add('References & methods',title)
    add('Original study basis',heading)
    add(r['formula'],small)
    if r['reported_cases'] is None:
        add(f"Published study reference: USD {r['study_societal_mean_usd']:,} per participant in 2016 dollars; no county total calculated without a verified case count.",small)
    add('Hook et al. (published 2022): '+r['study_population']+' '+r['cost_perspective'],small)
    add(r['transfer_assumption']+' '+r['other_assumptions'],small)
    add('Hook excluded non-English speakers and nonacute disease. The study does not represent every local household or continuing lifetime costs.',small)
    if r['inflation']:
        m=r['inflation']
        add('Optional inflation comparison',heading)
        add(f"General CPI factor approximately {float(m['factor']):.2f}; calculations use the full-precision factor retained in the methods CSV. Adjusted study mean approximately USD {m['restated_unit_usd']:,.0f} per participant (rounded for display).",small)
        add('2016 uses 12 monthly observations; 2025 uses 11 available months. October is missing; no imputation. This is not a verified official full-year annual average or medical-care inflation adjustment. It changes purchasing power, not case mix, treatment patterns or local prices.',small)
    add('Source register',heading)
    seen=set()
    for source in sources:
        if source['url'] in seen: continue
        seen.add(source['url'])
        add(str(len(seen))+'. '+source['purpose']+' · '+source['period'],small)
        url=escape(source['url'], {'"':'&quot;'})
        flow.append(Paragraph('<link href="'+url+'" color="#17648a"><u>'+escape(source['url'])+'</u></link>',small))
    add('Verification and interpretation',heading)
    add('Existing source snapshots; newer official releases have not been verified for this brief. Official rates are reproduced; exact rate-denominator vintage is not independently verified. Pre-2022 rates are excluded because surveillance definitions changed.',small)
    add(('Census language context is an existing QuickFacts snapshot, not a fresh pull or a measure of English proficiency. ' if context['language_context']['value'] is not None else 'County language context has not been verified and remains unavailable. ')+'HRSA field years are not substituted with newer Census periods. Initiative links require current local verification; no listing does not mean no services exist.',small)
    add(r['privacy'],small)
    add(r['scope']+' No county or organizational endorsement is implied.',small)
    out=BytesIO()
    def footer(canvas,doc):
        canvas.saveState();canvas.setFont('PathwayUnicodeV2',7);canvas.setFillColor(navy)
        canvas.drawString(42,25,'PathwayAI | Making the Hidden Patient Journey Visible—and Actionable')
        canvas.drawRightString(A4[0]-42,25,str(doc.page));canvas.restoreState()
    SimpleDocTemplate(out,pagesize=A4,leftMargin=42,rightMargin=42,topMargin=30,bottomMargin=42,
                      title=r['county']+' County Lyme Burden & Action Report',author='PathwayAI').build(flow,onFirstPage=footer,onLaterPages=footer)
    return out.getvalue()
