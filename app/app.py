"""Smart Recycling Coach demo (Streamlit).

Owner: Amaka · Build plan: 2.8, 4.4 · Spec: docs/PROJECT_SPEC.md §12
Run: streamlit run app/app.py
"""

import streamlit as st

st.set_page_config(page_title="Smart Recycling Coach")
st.title("Smart Recycling Coach")
st.caption(
    "General guidance only. Recycling rules vary by location, "
    "and this doesn't replace campus policy."
)
st.info("Coming soon: upload a photo of one item to get a disposal suggestion.")

# TODO(Amaka): photo upload / camera, a fake predictor until recycle_coach.predict exists (§8.9),
# guidance cards from docs/LABEL_GUIDE.md §5, and the low-confidence message (config.LOW_CONFIDENCE).
