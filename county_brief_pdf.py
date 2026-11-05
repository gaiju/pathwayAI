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
    compact_title = ParagraphStyle('CountyCompactTitle', parent=title, fontSize=16, leading=20)
    metric = ParagraphStyle('CountyMetric', parent=body, fontSize=14, leading=18)
    amount = ParagraphStyle('CountyAmount', parent=body, fontSize=16, leading=20, spaceAfter=4)
    flow=[]
    def paragraph(text, style=body): return Paragraph(escape(str(text)), style)
    def add(text, style=body): flow.append(paragraph(text, style))
    def number(value, suffix=''):
        return 'Not available' if value is None else f'{value:,g}'+suffix
    def table(rows, widths, padding=5, value_style=None):
        t=Table([[paragraph(cell, value_style if index and value_style else small) for cell in row] for index,row in enumerate(rows)], colWidths=widths, repeatRows=1, hAlign='LEFT')
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
    from county_report_context import county_location_map
    location=county_location_map(r['county'])
    if location is not None:
        header=Table([[[paragraph('PathwayAI | '+r['county']+' County',heading), paragraph('Lyme Disease Burden & Community Action',compact_title)],location]],colWidths=[403,108],hAlign='LEFT')
        header.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)]))
        flow.append(header)
    else:
        add('PathwayAI | '+r['county']+' County', heading)
        add('Lyme Disease Burden & Community Action', title)
    add('Prepared '+r['prepared_date']+' · Public-data planning brief · Version '+r['report_version'], small)
    add('Meeting snapshot · Public evidence and proposed actions for local review',small)
    table([['Reported cases · 2024','County rate per 100,000 · 2024','State rate per 100,000 · 2024'],
           [number(r['reported_cases']),number(r['reported_rate_per_100000']),number(r['state_reported_rate_per_100000'])]],[170,170,171],value_style=metric)
    add('Discussion priority: '+r['priority'],heading)
    question=Table([[paragraph('Question for the meeting',heading)],[paragraph(r['planning']['decision'],body)]],colWidths=[511])
    question.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),pale),('BOX',(0,0),(-1,-1),.6,navy),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
    flow.extend([question,Spacer(1,6)])
    if r.get('county_plan_context'):
        plan_context=r['county_plan_context']
        flow.append(Paragraph('Existing county context: the Dutchess 2025–2030 plan describes access disparities and referral approaches. Discuss how support could complement existing work. '+citation(plan_context['source_url']),small))
    add('Mid-Hudson counties and state comparison',heading)
    table([['Area','Reported cases · 2024','Rate per 100,000 · 2024']]+[[x['Area'],number(x['Reported cases']),number(x['Reported cases per 100,000'])] for x in context['comparison']],[205,145,161],padding=3)
    add('Same NYSDOH 2024 reporting year/source. Cases describe residents, not necessarily exposure location; reported rates are not personal risk estimates.',small)
    add('Study-based economic illustration',heading)
    if r['illustrative_total_2016_usd'] is None:
        add('Not available',amount)
        add('A verified county case count is required; no total is inferred from the rate.',small)
    else:
        add(f"USD {r['illustrative_total_2016_usd']/1_000_000:.2f} million · 2016 dollars",amount)
        add('Reported cases × Hook study societal mean. This illustrates scale, not measured county spending or predicted savings.',small)
        if r['inflation']:
            optional=Table([[paragraph(f"Optional 2025 purchasing-power comparison: USD {r['inflation']['restated_total_usd']/1_000_000:.2f} million",small)],
                            [paragraph('General inflation · 11 available months; October missing · not a complete annual average',small)]],colWidths=[511])
            optional.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),pale),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
            flow.extend([optional,Spacer(1,4)])
    add('Sources ['+', '.join(map(str,cost_refs))+']; calculation and methods: page 4.',small)
    add('Suggested meeting flow',heading)
    add('1. Confirm the local evidence.  2. Discuss one support priority.  3. Check existing services and agree a next step.',body)
    add('Public-data planning brief. Resource context and follow-up: page 2; local planning and research: page 3; references and methods: page 4.',small)
    flow.append(PageBreak())
    add('Resources & practical next steps',title)
    add('Healthcare resources and population context',heading)
    rows=[['Indicator','Value','Period']]
    rows += [[label,number(value),'2023'] for label,value in r['healthcare_context']['indicators'].items()]
    rows += [[('Poverty (population with poverty status determined)' if x['field']=='pers_povty_pct_23' else x['measure']),number(x['value'],'%'),str(x['year'])] for x in context['socioeconomic_context']]
    language=context['language_context']
    rows.append(['Language other than English at home · age 5+',number(language['value'],'%'),'ACS 2020–2024'])
    table(rows,[295,80,136],padding=4)
    add('General population/resource context, not Lyme-specific need, appointment availability or interpreter demand. Selected insurance/poverty fields supply no margin of error.',small)
    add('Reported Lyme rates by year · per 100,000 residents',heading)
    if all(row['Reported cases per 100,000'] is None for row in context['rate_trend'][:2]):
        add('2024 rate: '+number(context['rate_trend'][-1]['Reported cases per 100,000'])+' per 100,000; 2022–2023 unavailable in the verified records used here.',small)
    else:
        table([['2022','2023','2024'],[number(row['Reported cases per 100,000']) for row in context['rate_trend']]],[170,170,171])
    add('Pre-2022 rates excluded because surveillance definitions changed. Different sources do not establish causes; see methods on page 4.',small)
    local_resources=[item for item in context['listed_initiatives'] if item['category']!='Community health planning']
    if local_resources:
        add('Existing local resources to check',heading)
        for item in local_resources:
            flow.append(Paragraph(escape(item['name']+' · '+item['category'])+' '+citation(item['url']),small))
        add('Directory snapshot: confirm current activity, eligibility and capacity. Mobile outreach is not verified Lyme treatment; no partnership is implied.',small)
    plan=r['planning']
    add('1. Confirm the need with residents',heading)
    add(plan['need'])
    add(r['local_patient_reports_status'],small)
    add('2. Review an existing-service response',heading)
    add(plan['action'])
    add('Who could help: '+plan['participants'],small)
    add('Actions to discuss · '+r['audience'],small)
    for action in r['audience_actions']:add('• '+action,small)
    add('3. Agree responsibility and follow-up',heading)
    add('Check services, appointment capacity, staff time, funding and who would take responsibility before proposing a pilot. Define consent and privacy arrangements before any collection.',small)
    add('Choose a common period, such as 30 days. Record the starting situation, support received, missing answers and needs still unmet.',small)
    add('For this priority: '+plan['measure'],small)
    add('Proposed actions, not adopted services or demonstrated savings. Professional feedback: source clarity, assumptions, usefulness and missing local factors.',small)
    review_url=escape(r['professional_review_url'], {'"':'&quot;'})
    flow.append(Paragraph('<link href="'+review_url+'" color="#17648a"><u>Email feedback: pathwayai.feedback@gmail.com</u></link>',small))
    flow.append(PageBreak())
    add('Local planning & research context',title)
    add('What this means for local planning',heading)
    for index,note in enumerate(r['local_planning_notes'],1):
        label='A local action to review' if index==3 else note['title']
        flow.append(Paragraph('<b>'+escape(str(index)+'. '+label)+'</b>',body))
        text=escape(note['text'])
        if note['source_url']:
            text+=' '+citation(note['source_url'])
        flow.append(Paragraph(text,body))
    add('Planning questions for local review; population indicators do not establish Lyme-specific need or available services.',small)
    if r.get('county_plan_context'):
        plan_context=r['county_plan_context']
        add(plan_context['title'],heading)
        flow.append(Paragraph('Local priorities and existing pathways '+citation(plan_context['source_url']),small))
        for finding in plan_context['findings']:
            add('• '+finding['text']+' (pp. '+finding['printed_pages']+')',small)
        add(plan_context['question']+' '+plan_context['limits'],small)
        add('Selected CHIP priorities concern nutrition security, chronic-disease prevention and substance-misuse/overdose prevention; these are not an adopted Lyme program.',small)
    add('What published research adds',heading)
    add('External study populations provide context, not county patient findings.',small)
    for study in r['published_research_context']:
        flow.append(Paragraph('<b>'+escape(study['study'])+'</b> '+citation(study['url']),small))
        add(study['sample']+' · '+study['period'],small)
        add(study['contribution'],small)
        add('Population and limits: '+study['limit'],small)
    add('What we still need to know',heading)
    for gap in r['evidence_gaps']:
        add('• '+gap,small)
    add('Missing information is not zero; gaps do not establish an absence of need or services.',small)
    add('Hook is the sole cost basis. Do not add study estimates or infer local disability rates. Local patient findings require a defined collection and review process.',small)
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
    c=r['study_components']
    add('Published cost components · 2016 dollars per participant',heading)
    add('Medical: USD '+number(c['medical_mean'])+'; other expenses and productivity combined: USD '+number(c['other_expenses_and_productivity'])+'; total societal mean: USD '+number(c['total_societal_mean'])+'.',reference)
    add('The combined amount is a derived residual, not a separately reported mean. Caregiving is not separately valued here. Components are already included in the total; do not add them again.',reference)
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
    add('Location map uses the app’s bundled county boundaries for orientation only; underlying boundary vintage is not independently verified. It is not an official county map or a disease-risk map.',reference)
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
