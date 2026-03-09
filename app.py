import streamlit as st
import json

# Load the database
def load_data():
    with open('database.json', 'r') as f:
        return json.load(f)

data = load_data()
param_map = {p['name']: p for p in data}

# UI Configuration
st.set_page_config(page_title="AquaMetric Pro", layout="wide", initial_sidebar_state="expanded")

# Advanced CSS for a modern "Dashboard" look
st.markdown("""
    <style>
    /* Main background */
    .stApp { background-color: #f8f9fa; }
    
    /* Custom Sidebar styling */
    section[data-testid="stSidebar"] { background-color: #1e293b !important; color: white; }
    
    /* Card-style containers */
    div[data-testid="stVerticalBlock"] > div:has(div.stMetric) {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
    }
    
    /* Primary Button Styling */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize Session States
if 'batch' not in st.session_state:
    st.session_state.batch = {}

# --- SIDEBAR: CONTROLS & BATCH LIST ---
with st.sidebar:
    st.title("🧪 AquaMetric Pro")
    st.markdown("---")
    
    st.header("1. Input Data")
    selected_name = st.selectbox("Parameter Name", options=list(param_map.keys()))
    current_p = param_map[selected_name]
    
    val = st.number_input(f"Result ({current_p['unit']})", format="%.4f")
    
    if st.button("➕ Add to Analysis"):
        st.session_state.batch[selected_name] = val
        st.success(f"Linked: {selected_name}")

    st.markdown("---")
    st.header("2. Current Queue")
    if not st.session_state.batch:
        st.caption("No data added yet.")
    else:
        for name, value in st.session_state.batch.items():
            st.info(f"**{name}**: {value} {param_map[name]['unit']}")
        
        if st.button("🗑️ Reset All"):
            st.session_state.batch = {}
            st.rerun()

# --- MAIN AREA: RESULTS DASHBOARD ---
st.title("Water Quality Analysis Dashboard")
st.caption("Cross-referencing laboratory results with NIS 554:2015 and WHO standards.")

if not st.session_state.batch:
    st.warning("Please use the sidebar to input your laboratory results for analysis.")
else:
    # Top-level Metrics
    total_params = len(st.session_state.batch)
    st.write(f"### Analysis Overview ({total_params} Parameters)")
    
    # Display Results in a Grid
    cols = st.columns(2)
    for i, (name, user_val) in enumerate(st.session_state.batch.items()):
        p_data = param_map[name]
        with cols[i % 2]:
            st.markdown(f"### {name}")
            st.metric(label="Measured Value", value=f"{user_val} {p_data['unit']}")
            
            # Compare with standards
            for std in p_data['standards']:
                auth = std['authority']
                max_lim = std.get('max_limit')
                min_lim = std.get('min_limit')
                
                # Logical Evaluation
                fail_max = max_lim is not None and user_val > max_lim
                fail_min = min_lim is not None and user_val < min_lim
                
                if fail_max or fail_min:
                    st.error(f"**{auth} Status: NON-COMPLIANT**")
                    with st.expander("⚠️ View Risk & Remediation"):
                        st.write(f"**Hazard:** {std['consequence']}")
                        st.write(f"**Treatment:** {std['solution']}")
                else:
                    st.success(f"**{auth} Status: COMPLIANT**")
            st.markdown("---")

    # Final Action
    if st.button("📥 Export Comprehensive Report"):
        st.balloons()
        st.write("Generating CSV/PDF summary...")
