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

# ==========================
# Authentication System
# ==========================
AUTH_TOKEN = "shiksha@12"  # Same token as new_calc.py

# Session state init
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Login form if not authenticated
if not st.session_state.authenticated:
    st.title("🔐 Secure Gauge Calculator Login")
    token_input = st.text_input("Enter Access Token", type="password")
    
    if st.button("Login"):
        if token_input == AUTH_TOKEN:
            st.session_state.authenticated = True
            st.success("✅ Login Successful!")
            st.rerun()
        else:
            st.error("❌ Invalid Token. Access Denied.")

    st.stop()

# Logout button
with st.sidebar:
    st.success("✅ Logged In")
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# ==========================
# Main App UI
# ==========================
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
    inputs["lower"] = st.number_input("Min Limit (Lower) (mm):", step=0.001, format="%.3f")
    inputs["upper"] = st.number_input("Max Limit (Upper) (mm):", step=0.001, format="%.3f")

# Action buttons
col1, col2 = st.columns([1, 0.4])
with col1:
    calculate = st.button("🔍 Calculate")
with col2:
    reset = st.button("🔄 Reset")

if reset:
    st.experimental_rerun()

if calculate:
    # ✅ Add token to pass into new_calc.py
    result = calculate_go_no_go_extended(
        auth_token=AUTH_TOKEN,
        tol_type=tol_type,
        **inputs
    )

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

        st.write(f"**Nominal Range:** `{result['range'][0]} – {result['range'][1]} mm`")
        st.write(f"**ISO Column:** `S{result['column']}`")
        st.write(f"**EI / ES:** `{result['EI']:.3f} / {result['ES']:.3f} mm`")

st.markdown("---")
st.caption("Developed with ❤️ using Streamlit — Secured Access Enabled ✅")
