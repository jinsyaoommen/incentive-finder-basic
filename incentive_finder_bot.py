
import streamlit as st
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import faiss
import json
import numpy as np

st.set_page_config(page_title="RAG Incentive Finder", page_icon="🔍")

st.title("🔍 RAG Utility Incentive Finder Bot (Offline Prototype)")
st.write("Ask me anything about industrial or commercial utility incentives (NY, IL, FL, CT, TN).")

# Load knowledge base
with open("incentive_finder_knowledge_base.json", "r") as f:
    kb = json.load(f)

# Flatten the KB into chunks
chunks = []
chunk_map = []
for state, data in kb.items():
    for prog in data["programs"]:
        text = f"In {state}, {data['utility']} offers incentives for {prog['sector']} customers on projects like {', '.join(prog['project_types'])}. Incentive details: {prog['incentive']}. More at: {prog['link']}"
        chunks.append(text)
        chunk_map.append({
            "state": state,
            "text": text,
            "link": prog["link"]
        })

# Load embedding model
@st.cache_resource
def load_model_and_index():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype("float32"))
    return model, index, embeddings

model, index, embeddings = load_model_and_index()

# Simple keyword-aware context retriever
def retrieve_context(question, top_k=3):
    q_embedding = model.encode([question])
    _, indices = index.search(np.array(q_embedding).astype("float32"), top_k)
    return [chunks[i] for i in indices[0]]

# Fake local LLM generator (replace with real LLM for full RAG pipeline)
def fake_llm_answer(question, contexts):
    response = f"Based on what I found:

"
    for ctx in contexts:
        response += f"- {ctx}

"
    response += "Let me know if you'd like links or help comparing programs."
    return response

# Chat UI
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

prompt = st.chat_input("Ask me a question about incentives...")

if prompt:
    st.chat_message("user").markdown(prompt)
    context = retrieve_context(prompt)
    answer = fake_llm_answer(prompt, context)
    st.chat_message("assistant").markdown(answer)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": answer})
