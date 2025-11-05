# app.py
import streamlit as st
from new_calc import calculate_go_no_go_extended

# ==========================
# Streamlit Page Config
# ==========================
st.set_page_config(
    page_title="Snape Gauge / Ring Gauge GO / NO-GO Calculator (ISO Standard)",
    page_icon="🧩",
    layout="centered"
)

st.title("🧩 Snape Gauge / Ring Gauge GO / NO-GO Calculator (ISO Standard)")
st.markdown("""
This tool calculates **GO** and **NO-GO** gauge values as per ISO standards.  
Select your **tolerance type** and enter the corresponding values.
""")

# ==========================
# Input Selection
# ==========================
tol_type = st.selectbox(
    "Select Tolerance Type:",
    options=["±", "+", "-", "++", "--", "/"],
    format_func=lambda x: {
        "±": "± (Symmetric tolerance)",
        "+": "+ (Positive only)",
        "-": "− (Negative only)",
        "++": "++ (Double positive)",
        "--": "-- (Double negative)",
        "/": "/ (Lower/Upper range)"
    }[x]
)

# Input fields based on type
inputs = {}
if tol_type == "±":
    inputs["nominal"] = st.number_input("Nominal Size (mm):", step=0.001, format="%.3f")
    inputs["val1"] = st.number_input("Tolerance (± mm):", step=0.001, format="%.3f")

elif tol_type in ["++", "--"]:
    inputs["nominal"] = st.number_input("Nominal Size (mm):", step=0.001, format="%.3f")
    inputs["val1"] = st.number_input("Tolerance 1 (mm):", step=0.001, format="%.3f")
    inputs["val2"] = st.number_input("Tolerance 2 (mm):", step=0.001, format="%.3f")

elif tol_type in ["+", "-"]:
    inputs["nominal"] = st.number_input("Nominal Size (mm):", step=0.001, format="%.3f")
    inputs["val1"] = st.number_input("Tolerance (mm):", step=0.001, format="%.3f")

elif tol_type == "/":
    inputs["lower"] = st.number_input("Max Limit (A - Upper) [Snape] (mm):", step=0.001, format="%.3f")
    inputs["upper"] = st.number_input("Min Limit (B - Lower) [Snape] (mm):", step=0.001, format="%.3f")

# Action buttons
col1, col2 = st.columns([1, 0.4])
with col1:
    calculate = st.button("🔍 Calculate")
with col2:
    reset = st.button("🔄 Reset")

if reset:
    st.experimental_rerun()

if calculate:
    result = calculate_go_no_go_extended(tol_type, **inputs)
    if "error" in result:
        st.error(result["error"])
    else:
        st.success("✅ Calculation Successful!")

        go = result["go"]
        no_go = result["no_go"]
        gauge_tol = result["gauge_tol"]

        st.markdown("---")
        st.subheader("📊 Results")

        left, right = st.columns(2)
        with left:
            st.metric("GO Gauge", f"{go:.3f} ± {gauge_tol:.4f} mm")
        with right:
            st.metric("NO-GO Gauge", f"{no_go:.3f} ± {gauge_tol:.4f} mm")

        st.write(f"**Nominal Range Applied:** `{result['range'][0]} - {result['range'][1]} mm`")
        st.write(f"**Selected ISO Column:** `S{result['column']}`")
        st.write(f"**Lower / Upper Used:** `{result['EI']:.3f} / {result['ES']:.3f} mm`")
        st.caption("Computed using ISO T, Z, and H/2 values (micron → mm conversion).")

st.markdown("---")
st.caption("Developed with ❤️ using Streamlit")
