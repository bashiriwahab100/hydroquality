import streamlit as st
import json

# Load the database
def load_data():
    with open('database.json', 'r') as f:
        return json.load(f)

data = load_data()
param_map = {p['name']: p for p in data}

st.set_page_config(page_title="Water Quality Pro", layout="wide")

# Custom CSS for a clean, professional aesthetic
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { border-radius: 20px; font-weight: bold; }
    .status-card { padding: 20px; border-radius: 10px; border: 1px solid #d1d5db; background-color: white; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# Initialize Session State
if 'lab_results' not in st.session_state:
    st.session_state.lab_results = {}
if 'analysis_active' not in st.session_state:
    st.session_state.analysis_active = False

st.title("🛡️ Water Quality Assessment Portal")
st.info("Input all parameters from your lab report below. Once the batch is complete, click 'Run Analysis'.")

# --- SECTION 1: DATA INPUT FORM ---
with st.container(border=True):
    st.subheader("📋 Laboratory Data Entry")
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        selected_name = st.selectbox("Select Parameter", options=list(param_map.keys()))
    with col2:
        unit = param_map[selected_name]['unit']
        val = st.number_input(f"Value ({unit})", format="%.4f", key="input_val")
    with col3:
        st.write("##") # Alignment spacer
        if st.button("➕ Add to Batch", use_container_width=True):
            st.session_state.lab_results[selected_name] = val
            st.session_state.analysis_active = False # Reset analysis if new data is added
            st.toast(f"Logged {selected_name}")

# --- SECTION 2: THE DATA BATCH ---
if st.session_state.lab_results:
    st.divider()
    st.subheader("🛒 Parameters Ready for Analysis")
    
    # Display the current list in a clean table format
    batch_display = [{"Parameter": k, "Result": f"{v} {param_map[k]['unit']}"} for k, v in st.session_state.lab_results.items()]
    st.table(batch_display)
    
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("🚀 RUN FULL ANALYSIS", type="primary", use_container_width=True):
            st.session_state.analysis_active = True
    with btn_col2:
        if st.button("🗑️ Clear All Data", use_container_width=True):
            st.session_state.lab_results = {}
            st.session_state.analysis_active = False
            st.rerun()

# --- SECTION 3: ANALYSIS RESULTS ---
if st.session_state.analysis_active and st.session_state.lab_results:
    st.divider()
    st.header("🔍 Comparative Analysis Report")
    
    # Create an image tag for the general water quality assessment process
    # 
    
    for name, user_val in st.session_state.lab_results.items():
        p_data = param_map[name]
        
        with st.container(border=True):
            st.subheader(f"Parameter: {name}")
            c1, c2 = st.columns(2)
            c1.metric("Your Result", f"{user_val} {p_data['unit']}")
            
            # Run comparison against standards from your database
            for std in p_data['standards']:
                auth = std['authority']
                max_lim = std.get('max_limit')
                min_lim = std.get('min_limit')
                
                is_safe = True
                if max_lim is not None and user_val > max_lim: is_safe = False
                if min_lim is not None and user_val < min_lim: is_safe = False
                
                if is_safe:
                    st.success(f"**{auth}**: Compliant ✅")
                else:
                    st.error(f"**{auth}**: Non-Compliant ❌")
                    st.warning(f"**Risk:** {std['consequence']}")
                    st.info(f"**Treatment:** {std['solution']}")

