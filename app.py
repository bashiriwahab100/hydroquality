import streamlit as st
import json
import os
import pandas as pd

# 1. Robust File Loading
# This ensures the script finds database.json regardless of where it's hosted
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, 'database.json')

# 1. Page Config
st.set_page_config(page_title="AquaCheck Portal", page_icon="💧", layout="centered")

# --- CSS to hide ONLY the GitHub icon and the footer ---
hide_github_only = """
            <style>
            /* Hides the GitHub 'View Source' button in the header */
            header .stAppToolbar > div:first-child {
                display: none;
            }
            
            /* Hides the 'Made with Streamlit' footer */
            footer {
                visibility: hidden;
            }
            </style>
            """
st.markdown(hide_github_only, unsafe_allow_html=True)

# 2. Your existing logic follows
st.title("Water Quality Assessment Portal")# 1. Page Config
st.set_page_config(page_title="AquaCheck Portal", page_icon="💧", layout="centered")

# --- CSS to hide ONLY the GitHub icon and the footer ---
hide_github_only = """
            <style>
            /* Hides the GitHub 'View Source' button in the header */
            header .stAppToolbar > div:first-child {
                display: none;
            }
            
            /* Hides the 'Made with Streamlit' footer */
            footer {
                visibility: hidden;
            }
            </style>
            """
st.markdown(hide_github_only, unsafe_allow_html=True)

# 2. Your existing logic follows
st.title("Water Quality Assessment Portal")

def load_database():
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Error: 'database.json' not found in the root directory.")
        return []

water_db = load_database()

# 2. Initialize Session State (Prevents Blank Screen on Refresh)
if 'batch' not in st.session_state:
    st.session_state.batch = []

def run_analysis(lab_results):
    report = []
    for entry in lab_results:
        # Match parameter name from your JSON
        db_item = next((item for item in water_db if item["name"] == entry["name"]), None)
        if not db_item: continue

        status = {
            "Parameter": entry["name"],
            "Value": entry["value"],
            "Unit": db_item["unit"],
            "NIS (NAFDAC)": "✅ PASS",
            "WHO": "✅ PASS",
            "Notes": "",
            "Action": ""
        }

        # Check against NIS and WHO standards
        for std in db_item["standards"]:
            limit_fail = False
            if std.get("max_limit") and entry["value"] > std["max_limit"]:
                limit_fail = True
            if std.get("min_limit") and entry["value"] < std["min_limit"]:
                limit_fail = True

            if limit_fail:
                auth_key = "NIS (NAFDAC)" if "NIS" in std["authority"] else "WHO"
                status[auth_key] = "❌ FAIL"
                status["Notes"] = std["consequence"]
                status["Action"] = std["solution"]
        
        report.append(status)
    return pd.DataFrame(report)

# --- UI LAYOUT ---
st.title("💧 AquaCheck Assessment Portal")

# Sidebar for Input
with st.sidebar:
    st.header("Input Data")
    # Get names directly from your JSON database
    param_names = [item["name"] for item in water_db]
    selected_name = st.selectbox("Select Parameter", param_names)
    val = st.number_input("Laboratory Value", format="%.4f")
    
    if st.button("Add to Batch"):
        st.session_state.batch.append({"name": selected_name, "value": val})
        st.toast(f"Added {selected_name}")

# Main Display Area
if st.session_state.batch:
    st.subheader("Current Batch Results")
    results_df = run_analysis(st.session_state.batch)
    
    # Highlight failures visually
    st.dataframe(results_df.style.apply(lambda x: ['background-color: #ffcccc' if v == "❌ FAIL" else '' for v in x], axis=1))

    # Detailed Solutions for Failures
    for _, row in results_df.iterrows():
        if "❌ FAIL" in [row["NIS (NAFDAC)"], row["WHO"]]:
            with st.expander(f"⚠️ Remediation for {row['Parameter']}"):
                st.warning(f"**Consequence:** {row['Notes']}")
                st.success(f"**Required Solution:** {row['Action']}")
else:
    st.info("The batch is currently empty. Use the sidebar to add laboratory results.")



