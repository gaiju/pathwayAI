"""Share the public app address without patient data or tracking parameters."""
from report_download import branded_download_button
from pathlib import Path

PUBLIC_APP_URL = "https://pathwayai.streamlit.app/"
SHARE_MESSAGE = (
    "Help shape PathwayAI for patients, caregivers and healthier communities. "
    "Explore the app and share one suggestion: what is useful, and what would make it easier to use? "
    + PUBLIC_APP_URL
)


def show_share_pathway(key, feedback_callback=None, title="Share PathwayAI · help patient voices be heard"):
    import streamlit as st
    with st.expander(title):
        st.write("Know someone who could use PathwayAI or help improve it? Share the app with patients, caregivers and community teams.")
        st.image(str(Path(__file__).resolve().parent / "images" / "pathwayai_share_qr.png"),
                 width=200, caption="Scan to open PathwayAI")
        st.markdown(f"[Open PathwayAI]({PUBLIC_APP_URL})")
        st.code(SHARE_MESSAGE, language=None, wrap_lines=True)
        branded_download_button("Download QR code", (Path(__file__).resolve().parent / "images" / "pathwayai_share_qr.png").read_bytes(),
                           file_name="PathwayAI_QR.png", mime="image/png", key=key + "_qr")
        st.write("Your feedback can help us understand needs and improve support. What one change would help you most?")
        if feedback_callback:
            st.button("Share feedback →", key=key + "_feedback", on_click=feedback_callback)
        st.caption("The QR code shares the public website only. Personal stories and cards stay separate. Share feedback without names, medical reports or other identifying details.")
