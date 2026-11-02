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
    reference = ParagraphStyle('CountyReference', parent=small, fontSize=7.5, leading=10, spaceAfter=5)
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
    sources += [dict(purpose=x['study']+' · '+x['sample'],period=x['period'],url=x['url']) for x in r['published_research_context']]
    research_titles={
        r['published_research_context'][0]['url']:'Hook et al. Economic Burden of Reported Lyme Disease in High-Incidence Areas, United States, 2014–2016. Emerging Infectious Diseases. 2022.',
        r['published_research_context'][1]['url']:'Adrion et al. Health Care Costs, Utilization and Patterns of Care following Lyme Disease. PLOS ONE. 2015;10:e0116767.',
        r['published_research_context'][2]['url']:'Johnson et al. Severity of chronic Lyme disease compared to other chronic conditions: a quality of life survey. PeerJ. 2014;2:e322.'
    }
    source_numbers={}
    for source in sources:
        if source['url'] not in source_numbers: source_numbers[source['url']]=len(source_numbers)+1
    def citation(url):
        target=escape(url, {'"':'&quot;'})
        return '<link href="'+target+'" color="#17648a">['+str(source_numbers[url])+']</link>'
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
    add('Study-based illustration, not measured county spending or predicted savings. Sources ['+', '.join(map(str,cost_refs))+']; calculation and methods: page 4.', small)
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
    add('County of residence, not exposure location. Pre-2022 rates excluded because surveillance definitions changed. Different sources do not establish causes. References and limitations: page 4.',small)
    flow.append(PageBreak())
    add('From evidence to community action',title)
    c=r['study_components']
    add('Published components · per participant · 2016 dollars',heading)
    add('Medical: USD '+number(c['medical_mean'])+'; other expenses and productivity combined: USD '+number(c['other_expenses_and_productivity'])+'; total: USD '+number(c['total_societal_mean'])+'.',small)
    add('The combined component is a derived residual, not a separately reported mean. A separate caregiving amount is not established here; do not add components to the total again.',small)
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
    add('Professional review',heading)
    add('Public-health, health-economics and Lyme-care reviewers: please comment on source clarity, cost assumptions, practical usefulness and missing local factors.',small)
    review_url=escape(r['professional_review_url'], {'"':'&quot;'})
    flow.append(Paragraph('<link href="'+review_url+'" color="#17648a"><u>Email feedback: pathwayai.feedback@gmail.com</u></link>',small))
    flow.append(PageBreak())
    add('Local planning & research context',title)
    add('What This Means for Local Planning',heading)
    for index,note in enumerate(r['local_planning_notes'],1):
        label='A local action to review' if index==3 else note['title']
        flow.append(Paragraph('<b>'+escape(str(index)+'. '+label)+'</b>',body))
        text=escape(note['text'])
        if note['source_url']:
            text+=' '+citation(note['source_url'])
        flow.append(Paragraph(text,body))
    add('Planning questions for local review; population indicators do not establish Lyme-specific need or available services.',small)
    add('What published research adds',heading)
    add('External study populations provide context, not county patient findings.',small)
    for study in r['published_research_context']:
        flow.append(Paragraph(escape(study['study'])+' '+citation(study['url']),heading))
        add(study['sample']+' · '+study['period'],small)
        add(study['contribution'])
        add('Population and limits: '+study['limit'],small)
    add('How to use this evidence',heading)
    add('Use these studies to discuss spending, work disruption and daily-life impacts with local residents. Hook remains the sole study-cost basis for the county illustration. Study estimates are not added together or applied as local disability rates.',small)
    add('County-specific patient findings would require a defined local collection and review process. References and detailed methods follow on page 4.',small)
    flow.append(PageBreak())
    add('References & methods',title)
    add('Original study basis',heading)
    add(r['formula'],reference)
    if r['reported_cases'] is None:
        add(f"Published study reference: USD {r['study_societal_mean_usd']:,} per participant in 2016 dollars; no county total calculated without a verified case count.",reference)
    add('Hook et al. (published 2022): '+r['study_population']+' '+r['cost_perspective'],reference)
    add(r['transfer_assumption']+' '+r['other_assumptions'],reference)
    add('Hook excluded non-English speakers and nonacute disease. The study does not represent every local household or continuing lifetime costs.',reference)
    if r['inflation']:
        m=r['inflation']
        add('Optional inflation comparison',heading)
        add(f"General CPI factor approximately {float(m['factor']):.2f}; calculations use the full-precision factor retained in the methods CSV. Adjusted study mean approximately USD {m['restated_unit_usd']:,.0f} per participant (rounded for display).",reference)
        add('2016 uses 12 monthly observations; 2025 uses 11 available months. October is missing; no imputation. This is not a verified official full-year annual average or medical-care inflation adjustment. It changes purchasing power, not case mix, treatment patterns or local prices.',reference)
    add('Source register',heading)
    seen=set()
    for source in sources:
        if source['url'] in seen: continue
        seen.add(source['url'])
        label=escape(str(source_numbers[source['url']])+'. '+research_titles.get(source['url'],source['purpose'])+' · '+source['period'])
        url=escape(source['url'], {'"':'&quot;'})
        flow.append(Paragraph('<link href="'+url+'" color="#17648a">'+label+'</link>',reference))
    add('Verification and interpretation',heading)
    add('Existing source snapshots; newer official releases have not been verified for this brief. Official rates are reproduced; exact rate-denominator vintage is not independently verified. Pre-2022 rates are excluded because surveillance definitions changed.',reference)
    add(('Census language context is an existing QuickFacts snapshot, not a fresh pull or a measure of English proficiency. ' if context['language_context']['value'] is not None else 'County language context has not been verified and remains unavailable. ')+'HRSA field years are not substituted with newer Census periods. Initiative links require current local verification; no listing does not mean no services exist.',reference)
    add(r['privacy'],reference)
    add(r['scope']+' No county or organizational endorsement is implied.',reference)
    out=BytesIO()
    def footer(canvas,doc):
        canvas.saveState();canvas.setFont('PathwayUnicodeV2',7);canvas.setFillColor(navy)
        canvas.drawString(42,25,'PathwayAI | Making the Hidden Patient Journey Visible—and Actionable')
        canvas.drawRightString(A4[0]-42,25,str(doc.page));canvas.restoreState()
    SimpleDocTemplate(out,pagesize=A4,leftMargin=42,rightMargin=42,topMargin=30,bottomMargin=42,
                      title=r['county']+' County Lyme Burden & Action Report',author='PathwayAI').build(flow,onFirstPage=footer,onLaterPages=footer)
    return out.getvalue()
