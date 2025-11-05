# app.py
import streamlit as st
from new_calc import calculate_go_no_go_extended

st.set_page_config(
    page_title="Snape Gauge / Ring Gauge GO / NO-GO Calculator (ISO Standard)",
    page_icon="🧩",
    layout="centered"
)

AUTH_TOKEN = "shiksha@12"

# Authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Secure Gauge Calculator Login")
    token_input = st.text_input("Enter Access Token", type="password")

    if st.button("Login"):
        if token_input == AUTH_TOKEN:
            st.session_state.authenticated = True
            st.success("✅ Login Successful!")
            st.rerun()
        else:
            st.error("❌ Invalid Token")

    st.stop()

with st.sidebar:
    st.success("✅ Logged In")
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

st.title("🧩 Snape Gauge / Ring Gauge GO / NO-GO Calculator (ISO Standard)")
st.write("Enter tolerance parameters")

tol_type = st.selectbox(
    "Select Tolerance Type:",
    options=["±", "+", "-", "++", "--", "/"],
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

if st.button("🔍 Calculate"):
    result = calculate_go_no_go_extended(auth_token=AUTH_TOKEN, tol_type=tol_type, **inputs)

    if "error" in result:
        st.error(result["error"])
    else:
        st.success("✅ Calculation Successful")
        st.metric("GO Gauge", f"{result['go']:.3f} ± {result['gauge_tol']:.4f} mm")
        st.metric("NO-GO Gauge", f"{result['no_go']:.3f} ± {result['gauge_tol']:.4f} mm")

        st.write(f"**Nominal Range:** `{result['range'][0]} – {result['range'][1]} mm`")
        st.write(f"**ISO Column:** `S{result['column']}`")
        st.write(f"**EI / ES:** `{result['EI']:.3f} / {result['ES']:.3f} mm`")

st.caption("Developed with ❤️ — Secured Access ✅")
