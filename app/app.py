"""Smart Recycling Coach demo (Streamlit).

Owner: Amaka Okoro · Build plan: 2.8, 4.4 · Spec: docs/PROJECT_SPEC.md §12
Run: streamlit run app/app.py
"""

from pathlib import Path
from PIL import Image
import streamlit as st

from recycle_coach import config
from recycle_coach.predict import FakePredictor, Predictor, load_predictor

st.set_page_config(
    page_title="Smart Recycling Coach",
    page_icon="♻️",
    layout="centered",
)

# Header & Disclaimer
st.title("♻️ Smart Recycling Coach")
st.caption(
    "AI-powered single-item waste classifier for students and campus staff."
)

st.warning(
    "⚠️ **Disclaimer:** General guidance only. Recycling rules vary by municipal and campus "
    "location. This coach does not replace campus facilities policy or make hazardous waste decisions.",
    icon="ℹ️",
)

# Sidebar controls & info
with st.sidebar:
    st.header("⚙️ Settings & Info")
    use_mock = st.checkbox("Use Mock Predictor", value=not config.CHECKPOINT_PATH.exists())
    conf_threshold = st.slider(
        "Confidence Threshold",
        min_value=0.40,
        max_value=0.90,
        value=float(config.LOW_CONFIDENCE),
        step=0.05,
        help="Predictions below this score show an uncertain warning.",
    )

    st.markdown("---")
    st.subheader("👥 Project Team")
    st.markdown(
        """
        - **John Sampson**: Team Lead & Data Ingest
        - **Dakarai Lanes**: Model & Training Lead
        - **Rickey Johnson**: Data Pipeline & Validation
        - **Amaka Okoro**: Demo App & Evaluation Lead
        - **Premajyoti Gammon**: Documentation & Review
        """
    )
    st.markdown("---")
    st.caption("COMP 365: AI & Machine Learning")

# Load model
@st.cache_resource
def get_cached_predictor(mock: bool):
    if mock:
        return load_predictor(fake=True)
    return load_predictor(checkpoint_path=config.CHECKPOINT_PATH)

predictor = get_cached_predictor(use_mock)

if isinstance(predictor, FakePredictor):
    st.info("ℹ️ Running in **Mock/Demo mode** (MobileNetV3 checkpoint not loaded).", icon="💡")

# Input selection: Upload vs Camera
input_mode = st.radio("Choose input method:", ("Upload Photo", "Camera Capture"), horizontal=True)

image_input = None
if input_mode == "Upload Photo":
    uploaded_file = st.file_uploader(
        "Upload a photo of a single waste item (clean, centered):",
        type=["jpg", "jpeg", "png", "webp"],
    )
    if uploaded_file is not None:
        image_input = Image.open(uploaded_file)
else:
    camera_file = st.camera_input("Take a photo of the item:")
    if camera_file is not None:
        image_input = Image.open(camera_file)

# Prediction & Results Display
if image_input is not None:
    st.image(image_input, caption="Input Photo", use_container_width=True)

    with st.spinner("Analyzing item..."):
        result = predictor.predict(image_input, threshold=conf_threshold)

    pred_label = result["label"]
    confidence = result["confidence"]
    probs = result["probs"]
    guidance = result["guidance"]
    is_low_conf = result.get("low_confidence", False)

    st.markdown("---")
    st.subheader("Disposal Suggestion")

    # Status card with color
    color_map = {
        "recycling": ("#2e7d32", "🟢", "Recycling"),
        "special_handling": ("#ed6c02", "🟡", "Special Handling"),
        "trash": ("#424242", "⚪", "Trash"),
    }
    hex_color, icon, display_title = color_map.get(pred_label, ("#1976d2", "ℹ️", pred_label))

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(
            f"<div style='padding: 16px; border-radius: 8px; border-left: 6px solid {hex_color}; "
            f"background-color: #f7f9fa;'>"
            f"<h3 style='margin:0; color: {hex_color};'>{icon} {display_title}</h3>"
            f"<p style='margin: 8px 0 0 0; font-size: 1.05rem;'>{guidance}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

    with col2:
        st.metric("Top Confidence", f"{confidence:.1%}")

    if is_low_conf:
        st.error(
            "⚠️ **Low Confidence Prediction:** The AI is unsure about this item. "
            "Please check the posted campus bin signage, consult the Label Guide, "
            "or contact Facilities Services before disposing."
        )

    # Class probability breakdown
    with st.expander("📊 View Probability Breakdown", expanded=True):
        for cls_name in config.CLASSES:
            display_name = config.DISPLAY_NAMES.get(cls_name, cls_name)
            prob_val = probs.get(cls_name, 0.0)
            col_l, col_r = st.columns([3, 1])
            with col_l:
                st.write(f"**{display_name}**")
                st.progress(prob_val)
            with col_r:
                st.write(f"{prob_val:.1%}")
else:
    st.markdown("---")
    st.info("👆 Upload or snap a photo of an item above to get disposal recommendations.")

    st.subheader("Accepted Item Categories Quick Reference")
    q1, q2, q3 = st.columns(3)
    with q1:
        st.markdown(
            "**🟢 Recycling**\n\n"
            "- Clean plastic bottles & jugs\n"
            "- Aluminum soda cans\n"
            "- Steel food cans\n"
            "- Glass bottles & jars\n"
            "- Flattened cardboard & paper"
        )
    with q2:
        st.markdown(
            "**🟡 Special Handling**\n\n"
            "- Batteries (AA, AAA, lithium)\n"
            "- Electronics & charging cables\n"
            "- Light bulbs (CFLs, LEDs)\n"
            "- Plastic grocery bags (store drop-off)\n"
            "- Broken glass (wrapped)"
        )
    with q3:
        st.markdown(
            "**⚪ Trash**\n\n"
            "- Chip bags & snack wrappers\n"
            "- Food-soiled paper & napkins\n"
            "- Styrofoam cups & containers\n"
            "- Plastic straws & utensils\n"
            "- Mixed-material packaging"
        )
