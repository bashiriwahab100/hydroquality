import json
import pandas as pd

# 1. Load your provided database.json
with open('database.json', 'r') as f:
    water_db = json.load(f)

def run_water_analysis(lab_results):
    """
    lab_results: list of dicts, e.g., [{"name": "pH Level", "value": 9.0}]
    """
    analysis_report = []

    for result in lab_results:
        # Find the parameter in our database
        param_info = next((item for item in water_db if item["name"] == result["name"]), None)
        
        if not param_info:
            continue
        
        param_status = {
            "Parameter": result["name"],
            "Measured Value": result["value"],
            "Unit": param_info["unit"],
            "NIS Status": "✅ PASS",
            "WHO Status": "✅ PASS",
            "Consequences": [],
            "Solutions": []
        }

        # Check against each standard (NIS and WHO)
        for std in param_info["standards"]:
            authority = "NIS" if "NIS" in std["authority"] else "WHO"
            
            # Check Max Limit
            is_above_max = std.get("max_limit") is not None and result["value"] > std["max_limit"]
            # Check Min Limit (mostly for pH)
            is_below_min = std.get("min_limit") is not None and result["value"] < std["min_limit"]

            if is_above_max or is_below_min:
                param_status[f"{authority} Status"] = "❌ FAIL"
                param_status["Consequences"].append(f"({authority}): {std['consequence']}")
                param_status["Solutions"].append(f"({authority}): {std['solution']}")

        analysis_report.append(param_status)
    
    return pd.DataFrame(analysis_report)

# --- EXAMPLE USAGE ---
# Let's say these are the values entered in your portal
my_lab_batch = [
    {"name": "pH Level", "value": 9.2},       # Should fail (Limit 8.5)
    {"name": "Turbidity", "value": 2.5},     # Fails WHO (Limit 1.0), Passes NIS (Limit 5.0)
    {"name": "Lead (Pb)", "value": 0.005}    # Should pass both (Limit 0.01)
]

df_results = run_water_analysis(my_lab_batch)
print(df_results[['Parameter', 'Measured Value', 'NIS Status', 'WHO Status']])
