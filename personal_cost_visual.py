"""A local visual of entered payments and time; no external AI or uploads."""
from html import escape
import math


def personal_cost_svg(medical=None, other=None, workdays=None, caregiver=None,
                      modeled=None, period="Not reported"):
    def valid(value):
        return (isinstance(value, (int, float)) and not isinstance(value, bool)
                and math.isfinite(value) and value >= 0)

    def label(value, unit):
        if not valid(value):
            return "Add when known"
        return f"${value:,.2f}" if unit == "$" else f"{value:g} {unit}"

    cards = [("Care payments", medical, "$"), ("Other payments", other, "$"),
             ("Work missed", workdays, "days"), ("Unpaid help", caregiver, "hours")]
    complete = valid(medical) and valid(other)
    total = f"Recorded payments: ${medical + other:,.2f}" if complete else "Record both payment amounts to calculate your total."
    estimated = (f"Chosen work-loss estimate: ${modeled:,.2f} (shown separately)"
                 if valid(modeled) else "Workdays and unpaid help are shown in their own units.")
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 340" role="img" aria-labelledby="title desc">',
             '<title id="title">Your money and time record</title>',
             '<desc id="desc">' + escape("; ".join(f"{name}: {label(value, unit)}" for name, value, unit in cards) + "; " + total + "; " + estimated) + '</desc>',
             '<rect width="1000" height="340" rx="16" fill="#f5fafb"/>',
             '<g font-family="Arial,sans-serif" fill="#123149">',
             '<text x="28" y="42" font-size="26" font-weight="bold">Your money and time record</text>',
             f'<text x="28" y="72" font-size="17">Period: {escape(str(period))}</text>']
    for index, (name, value, unit) in enumerate(cards):
        x = 28 + index * 240
        parts.extend([f'<rect x="{x}" y="94" width="224" height="110" rx="12" fill="#ffffff" stroke="#a7cbd1"/>',
                      f'<text x="{x+14}" y="130" font-size="18">{name}</text>',
                      f'<text x="{x+14}" y="172" font-size="23" font-weight="bold">{label(value, unit)}</text>'])
    parts.extend([f'<text x="28" y="240" font-size="21" font-weight="bold">{escape(total)}</text>',
                  f'<text x="28" y="273" font-size="17">{escape(estimated)}</text>',
                  '<text x="28" y="310" font-size="15">PathwayAI · Your entries for this period · Review alongside your visit summary</text>', '</g></svg>'])
    return "".join(parts)
