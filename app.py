import streamlit as st
import pandas as pd

# Page configuration for that "Portal" feel
st.set_page_config(page_title="AquaCheck", page_icon="💧", layout="centered")

# Custom CSS to mimic your glassmorphism design
st.markdown("""
    <style>
    .main {
        background: linear-gradient(145deg, #eef5fa 0%, #f2f8fe 100%);
    }
    div.stButton > button {
        background: linear-gradient(115deg, #197bbd, #2c8fc9);
        color: white;
        border-radius: 25px;
        padding: 0.6rem 2rem;
        border: none;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(0, 80, 120, 0.3);
    }
    .parameter-tag {
        background-color: #d9edf9;
        color: #07405a;
        padding: 5px 15px;
        border-radius: 20px;
        border: 1px solid #7bc0df;
        display: inline-block;
        margin: 5px;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

# App Header
st.title("💧 Water Quality Assessment Portal")
st.info("Input all parameters from your lab report below. Once the batch is complete, run the analysis.")

# Initialize Session State for the "Batch"
if 'batch' not in st.session_state:
    st.session_state.batch = []

# --- Laboratory Data Entry ---
with st.container():
    st.subheader("📋 Laboratory Data Entry")
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        param = st.selectbox("Select Parameter", 
                             ["pH Level", "Turbidity (NTU)", "Dissolved Oxygen (mg/L)", 
                              "Conductivity (µS/cm)", "Temperature (°C)"])
    with col2:
        # Dynamic hint logic
        ranges = {"pH Level": "0-14", "Turbidity (NTU)": "0-5", "Dissolved Oxygen (mg/L)": "7-11"}
        val = st.number_input(f"Value ({ranges.get(param, 'Scale')})", format="%.4f", step=0.0001)
        
    with col3:
        st.write("##") # Alignment spacer
        if st.button("+ Add to Batch"):
            st.session_state.batch.append({"Parameter": param, "Value": val})

# --- Current Batch Display ---
st.divider()
st.subheader(f"📦 Current Batch ({len(st.session_state.batch)} parameters)")

if not st.session_state.batch:
    st.write("_No parameters added yet_")
else:
    # Displaying as a list of tags or a table
    for i, item in enumerate(st.session_state.batch):
        st.markdown(f'<span class="parameter-tag"><b>{item["Parameter"]}</b>: {item["Value"]:.4f}</span>', unsafe_allow_html=True)

    if st.button("Clear Batch"):
        st.session_state.batch = []
        st.rerun()

# --- Run Analysis ---
st.write("##")
if st.button("🌀 Run Analysis →", use_container_width=True):
    if not st.session_state.batch:
        st.warning("Batch is empty. Please add parameters first.")
    else:
        st.success("Analysis Complete!")
        df = pd.DataFrame(st.session_state.batch)
        st.table(df) # Shows the summary
