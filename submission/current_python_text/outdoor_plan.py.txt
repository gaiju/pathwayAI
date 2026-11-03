"""Offline outdoor preparation download; no AI or individual risk scoring."""
from datetime import datetime, timezone

from report_download import TAGLINE
CDC_BOT = "https://www.cdc.gov/ticks/communication-resources/tick-bite-bot-1.html"


def outdoor_plan_text(destination, month, activity, *, created=None, state_name=None):
    created = created or datetime.now(timezone.utc).strftime("%Y-%m-%d (UTC)")
    return "\n".join([
        TAGLINE, "My Outdoor Preparation Plan", "Created: " + created,
        "", "YOUR PLANS", "Destination: " + (destination or "Not provided"),
        "Destination state: " + (state_name or "State not identified"),
        "Month: " + month, "Planned activity: " + activity,
        "", "BEFORE AND DURING OUTDOOR ACTIVITIES",
        "- Pack an EPA-registered insect repellent and follow its label instructions.",
        "- Consider protective clothing and gear treated with 0.5% permethrin; follow product instructions. Do not apply permethrin to skin.",
        "- Avoid brush and tall grass where possible; walk in the center of trails.",
        "- Pack clean, fine-tipped tweezers.",
        "", "AFTER OUTDOOR ACTIVITIES",
        "- Check your body, clothing, gear and pets for ticks. Check children too.",
        "- Shower within two hours of coming indoors.",
        "", "IF YOU FIND AN ATTACHED TICK",
        "- Remove it promptly with clean, fine-tipped tweezers. Grasp close to the skin and pull upward with steady, even pressure.",
        "- Clean the bite area and your hands. Do not burn the tick or cover it with oil or petroleum jelly.",
        "- Record when and where you found it and when you removed it.",
        "- Different tick-borne infections spread at different speeds. Do not assume a short attachment time rules out every infection.",
        "", "WHEN TO CONTACT A HEALTHCARE PROFESSIONAL",
        "- Contact a clinician promptly for a new rash, fever or other symptoms after possible tick exposure. A Lyme rash does not always look like a bull's-eye.",
        "- After some bites, preventive antibiotics may be appropriate within 72 hours of tick removal. Ask a clinician promptly; do not wait for symptoms to ask. Not every bite needs antibiotics.",
        "- Do not wait for tick-test results before seeking medical advice. Tick testing cannot establish whether you were infected and should not determine treatment.",
        "- For sudden facial drooping, chest pain, severe trouble breathing or fainting, call 911. These may be emergencies unrelated to a tick bite.",
        "- If you lack insurance, ask a community health center about care and income-based discounts. Care is not automatically free.",
        "", "SOURCES AND NEXT STEPS",
        "CDC tick prevention: https://www.cdc.gov/ticks/prevention/index.html",
        "CDC after a tick bite: https://www.cdc.gov/ticks/after-a-tick-bite/index.html",
        "CDC Tick Bite Bot: " + CDC_BOT,
        "Find a health center: https://findahealthcenter.hrsa.gov/",
        "PathwayAI: https://pathwayai.streamlit.app/",
        "", "Educational preparation, not a diagnosis, treatment decision or personal infection-risk estimate.",
        "County surveillance provides general context and is not a prediction of your individual risk. No individual risk score is calculated.",
        "This download contains your selected destination, month and activity, plus a general checklist. It does not include maps, health-condition selections or a complete copy of the on-screen surveillance details.",
    ]) + "\n"
