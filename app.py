import streamlit as st
import json

# Load the database
def load_data():
    with open('database.json', 'r') as f:
        return json.load(f)

data = load_data()

st.set_page_config(page_title="Water Quality Analyzer", layout="wide")

st.title("💧 Water Chemical Analysis Tool")
st.markdown("Compare your water test results against **NIS 554:2015** and **WHO** standards.")

# Sidebar for inputs
st.sidebar.header("Input Test Results")
user_inputs = {}

for param in data:
    # Use a default value of 0.0 or the min_limit if available
    default_val = param['standards'][0].get('min_limit', 0.0) if 'min_limit' in param['standards'][0] else 0.0
    user_inputs[param['id']] = st.sidebar.number_input(
        f"{param['name']} ({param['unit']})", 
        value=float(default_val),
        step=0.01 if param['unit'] == 'mg/L' else 1.0,
        format="%.3f" if param['unit'] == 'mg/L' else None
    )

# Analysis Logic
st.header("Analysis Report")

cols = st.columns(2)
col_idx = 0

for param in data:
    with cols[col_idx % 2]:
        val = user_inputs[param['id']]
        st.subheader(f"{param['name']}")
        
        # Display current value
        st.metric(label="Detected Level", value=f"{val} {param['unit']}")
        
        # Compare against each authority in the JSON
        for std in param['standards']:
            auth = std['authority']
            max_lim = std.get('max_limit')
            min_lim = std.get('min_limit')
            
            is_safe = True
            issue_msg = ""

            # Check logic
            if max_lim is not None and val > max_lim:
                is_safe = False
                issue_msg = f"Exceeds {auth} limit of {max_lim}."
            if min_lim is not None and val < min_lim:
                is_safe = False
                issue_msg = f"Below {auth} limit of {min_lim}."

            if not is_safe:
                st.error(f"**{auth} Alert:** {issue_msg}")
                st.warning(f"**Consequence:** {std['consequence']}")
                st.info(f"**Recommended Solution:** {std['solution']}")
            else:
                st.success(f"✅ Compliant with {auth}")
        
        st.divider()
    col_idx += 1

# Summary Table
st.header("📋 Data Summary")
summary_data = []
for param in data:
    summary_data.append({
        "Parameter": param['name'],
        "Result": f"{user_inputs[param['id']]} {param['unit']}",
        "NIS Limit": next((f"{s.get('max_limit')}" for s in param['standards'] if s['authority'] == "NIS 554:2015"), "N/A"),
        "WHO Limit": next((f"{s.get('max_limit')}" for s in param['standards'] if s['authority'] == "WHO Guidelines"), "N/A")
    })

st.table(summary_data)