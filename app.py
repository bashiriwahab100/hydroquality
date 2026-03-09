import streamlit as st
import json

# Load the database
def load_data():
    with open('database.json', 'r') as f:
        return json.load(f)

data = load_data()
param_map = {p['name']: p for p in data}

st.set_page_config(page_title="Water Quality Analysis Wizard", layout="wide")

# Custom CSS for the red/grey aesthetic in your screenshot
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
    .batch-container { background-color: #f0f2f6; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("Comprehensive Water Quality Analysis & Project Design Wizard")

# Initialize session state for batch processing
if 'batch' not in st.session_state:
    st.session_state.batch = {}

# Layout: Two main tabs as seen in screenshot
tab1, tab2 = st.tabs(["📊 Multi-Parameter Analysis", "📝 Project Proposal Wizard"])

with tab1:
    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.header("🕹️ Input Lab Data")
        with st.container(border=True):
            # 1. Select Parameter
            selected_param_name = st.selectbox("Select Parameter", options=list(param_map.keys()))
            
            # 2. Enter Value
            unit = param_map[selected_param_name]['unit']
            val = st.number_input(f"Lab Result Value ({unit})", format="%.4f", step=0.01)
            
            # 3. Add to Batch
            if st.button("➕ Add to Batch"):
                st.session_state.batch[selected_param_name] = val
                st.toast(f"Added {selected_param_name} to batch!")

        st.header("📋 Current Batch")
        if not st.session_state.batch:
            st.info("No parameters added yet. Use the form above.")
        else:
            for name, value in st.session_state.batch.items():
                st.write(f"**{name}:** {value} {param_map[name]['unit']}")
            if st.button("🗑️ Clear Batch"):
                st.session_state.batch = {}
                st.rerun()

    with col_right:
        st.header("🔍 Analysis Results")
        
        if not st.session_state.batch:
            st.info("Pending data input. Results will appear here after running analysis.")
        
        if st.button("🚀 RUN FULL ANALYSIS"):
            if not st.session_state.batch:
                st.error("Please add at least one parameter to the batch first.")
            else:
                for name, user_val in st.session_state.batch.items():
                    p_data = param_map[name]
                    st.subheader(f"Results for {name}")
                    
                    # Check against standards
                    for std in p_data['standards']:
                        auth = std['authority']
                        max_lim = std.get('max_limit')
                        min_lim = std.get('min_limit')
                        
                        is_safe = True
                        if max_lim is not None and user_val > max_lim: is_safe = False
                        if min_lim is not None and user_val < min_lim: is_safe = False

                        if is_safe:
                            st.success(f"✅ {auth}: Compliant")
                        else:
                            st.error(f"❌ {auth}: Non-Compliant (Limit: {max_lim if max_lim else min_lim})")
                            st.warning(f"**Consequence:** {std['consequence']}")
                            st.info(f"**Solution:** {std['solution']}")
                    st.divider()
