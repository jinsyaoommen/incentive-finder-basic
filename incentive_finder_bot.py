
import streamlit as st
import json
from difflib import get_close_matches

st.set_page_config(page_title="Utility Incentive Finder", page_icon="💡")

st.title("Utility Incentive Finder Bot 💡")
st.write("I'm here to help you find utility programs and incentives based on your industry and location (non–West Coast only for now).")

# Load the knowledge base
@st.cache_data
def load_kb():
    with open("incentive_finder_knowledge_base.json", "r") as f:
        return json.load(f)

kb = load_kb()

# Helper function
def find_incentives(state_input, sector_input=None):
    state_key = state_input.strip().upper()
    if state_key not in kb:
        return f"Sorry, I don't have any data for '{state_input}' yet. Try FL, TN, NY, IL, or CT."

    entry = kb[state_key]
    results = []
    for program in entry["programs"]:
        if sector_input:
            match = get_close_matches(sector_input.lower(), [program["sector"].lower()], n=1, cutoff=0.4)
            if not match:
                continue
        details = f"""
**Utility:** {entry['utility']}  
**Eligible Projects:** {", ".join(program['project_types'])}  
**Incentive:** {program['incentive']}  
🔗 [Program Link]({program['link']})
"""
        results.append(details)
    return "\n\n".join(results) if results else f"No matching programs found for sector '{sector_input}'."

# Chat session state
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

# Input
prompt = st.chat_input("Ask me about utility incentives...")

if prompt:
    st.chat_message("user").markdown(prompt)
    # Simple parsing for state and sector
    state = None
    sector = None
    for word in prompt.upper().split():
        if word in kb:
            state = word
    if "industrial" in prompt.lower():
        sector = "industrial"
    elif "commercial" in prompt.lower():
        sector = "commercial"

    if state:
        response = find_incentives(state, sector)
    else:
        response = "Please tell me the state you're in (e.g., FL, NY, IL) and your sector (industrial or commercial)."

    st.chat_message("assistant").markdown(response)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": response})
