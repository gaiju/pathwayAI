"""Single-page public county brief; full details stay in the companion report."""
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from pdf_report import _fonts, _markup


def executive_pdf(report):
    _fonts()
    output = BytesIO()
    width, height = A4
    c = canvas.Canvas(output, pagesize=A4)
    c.setTitle(f"PathwayAI {report['county']} County executive brief")
    style = ParagraphStyle('Executive', fontName='PathwayUnicodeV2',
                           fontSize=9, leading=12, textColor=HexColor('#163149'))
    y = height - 40

    def paragraph(text, size=9):
        nonlocal y
        p = Paragraph(_markup(text), ParagraphStyle('Line', parent=style, fontSize=size))
        _, h = p.wrap(width - 80, height)
        if y - h < 35:
            raise ValueError('Executive brief exceeds one page; use the full report.')
        p.drawOn(c, 40, y - h)
        y -= h + 7

    paragraph(f"{report['county']} County | Lyme burden & action", 15)
    paragraph(f"PUBLIC-EVIDENCE DISCUSSION DRAFT · {report['state']} · v{report['report_version']}")
    paragraph('No patient data required. Complements surveillance and personal-care tools.')
    paragraph(f"OBSERVED: {report['reported_cases']:,} reported cases in {report['case_year']}; "
              f"{report['reported_rate_per_100000']:g} per 100,000 residents. "
              f"State rate: {report['state_reported_rate_per_100000']:g}.")
    paragraph('Reported cases are not all infections, exposure locations or measured service demand.')
    paragraph('REPORTED-RATE CONTEXT — cases per 100,000, zero baseline')
    # This series is verified only for the existing NY pilot counties.
    if report['state'] == 'New York' and report['county'] in ('Dutchess', 'Orange'):
        from county_trends import county_rate_trend
        rows = [r for r in county_rate_trend() if r['Area'] in
                (report['county'], 'New York State')]
        years = sorted({r['Year'] for r in rows})
        maximum = max(r['Reported cases per 100,000'] for r in rows)
        for year in years:
            for area, color in ((report['county'], '#2474A6'), ('New York State', '#6B7280')):
                value = next(r['Reported cases per 100,000'] for r in rows
                             if r['Year'] == year and r['Area'] == area)
                c.setFont('PathwayUnicodeV2', 8)
                c.setFillColor(HexColor('#163149'))
                c.drawString(40, y - 8, f'{year} {area}')
                c.setFillColor(HexColor(color))
                c.rect(185, y - 10, value / maximum * 230, 7, fill=1, stroke=0)
                c.setFillColor(HexColor('#163149'))
                c.drawString(425, y - 8, f'{value:g}')
                y -= 14
        y -= 6
        paragraph('2022–2023: Mid-Hudson CHA 2025, Fig. 147 p.219; 2024: NYSDOH rates p.5. '
                  'Post-2022 series only; surveillance changes affect interpretation.')
    else:
        paragraph('Historical series not verified for this county. No trend inferred.')
    paragraph('STUDY-BASED ILLUSTRATION — NOT MEASURED LOCAL SPENDING')
    paragraph(report['formula'] + ' Hook et al. 2022; societal analysis n=613. '
              'Applying the study mean locally is an assumption, not a county budget or savings estimate.')
    paragraph('Medical resources | household payments and hardship | work and unpaid care | daily life: '
              'keep these distinct. Societal costs already include medical, nonmedical and productivity costs; '
              'do not add them again. No supported component shares are plotted.')
    paragraph('UNCERTAINTY: reporting and study-sampling limits; different local case mix; excluded populations '
              'and long-term burden. No county confidence interval. Missing local burden is not zero.')
    paragraph('DECISION: ' + report['planning']['decision'])
    paragraph('NEXT: verify demand, service eligibility/capacity, accessibility, responsible partners, staffing '
              'and funding with residents. Agree a baseline and track support received and unresolved needs.')
    if any(report.get('local_context', {}).values()):
        paragraph('LOCAL STAFF NOTES: included in the full companion report as unverified local context; '
                  'not public-source findings or partner commitments.')
    paragraph('SOURCES: NYSDOH county cases/rates (2024); Hook et al. (2022), 2016 dollars. '
              'Full URLs, prior verification dates, hashes, uncertainty and review worksheet: companion full report/CSV.')
    paragraph('Not an adopted county plan, benefits decision, funded service or causal evaluation. '
              'Optional inflation restatement, if selected, appears only in the full report.')
    c.setFont('PathwayUnicodeV2', 7)
    c.drawString(40, 22, 'PathwayAI | Public county planning brief | ' + report['generated_on'])
    c.showPage()
    c.save()
    return output.getvalue()
