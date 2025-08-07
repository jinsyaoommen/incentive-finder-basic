
import streamlit as st
import json

st.set_page_config(page_title="Utility Incentive Finder", page_icon="💡")

st.title("Utility Incentive Finder Bot 💡")
st.write("Select your NAICS industry and one or more U.S. states (non–West Coast only for now), and I’ll show matching utility incentives.")

# Load data
@st.cache_data
def load_data():
    with open("incentive_finder_knowledge_base.json", "r") as f:
        kb = json.load(f)
    with open("naics_to_projects.json", "r") as f:
        naics_map = json.load(f)
    return kb, naics_map

kb, naics_map = load_data()

# Build dropdown options
naics_options = {f"{code} – {data['industry']}": code for code, data in naics_map.items()}
naics_selection = st.selectbox("Select your industry (NAICS)", list(naics_options.keys()))
selected_naics = naics_options[naics_selection]

# Multi-select for states
state_input = st.multiselect(
    "Select one or more states (2-letter codes)",
    options=["FL", "TN", "NY", "IL", "CT"]
)

def find_incentives(states, naics_code):
    output = []

    industry = naics_map[naics_code]["industry"]
    relevant_projects = set([p.lower() for p in naics_map[naics_code]["project_types"]])
    output.append(f"**NAICS {naics_code} – {industry}**")
    output.append(f"Relevant project types: {', '.join(relevant_projects)}\n")

    for state in states:
        state_key = state.strip().upper()
        if state_key not in kb:
            output.append(f"❌ No data for state '{state_key}'")
            continue

        entry = kb[state_key]
        matches = []
        for program in entry["programs"]:
            if any(pt.lower() in relevant_projects for pt in program["project_types"]):
                matches.append(f"""**Utility:** {entry['utility']}
Eligible Projects: {", ".join(program['project_types'])}
Incentive: {program['incentive']}
🔗 [Program Link]({program['link']})""")

        if matches:
            output.append(f"### {state_key}")
            output.extend(matches)
        else:
            output.append(f"⚠️ No matching programs found in {state_key} for NAICS {naics_code}")

    return "\n\n".join(output)

# Show results
if selected_naics and state_input:
    response = find_incentives(state_input, selected_naics)
    st.markdown(response)
else:
    st.info("Please select both a NAICS industry and at least one state.")
