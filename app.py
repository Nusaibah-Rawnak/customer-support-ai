import os
import sys
import streamlit as st
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agents"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "mcp_server"))

from supervisor import run_supervisor
from rag_tools import ingest_pdf, list_uploaded_documents

load_dotenv()

# Page config 
st.set_page_config(
    page_title="Customer Support AI",
    page_icon="💬",
    layout="wide",
)

# Custom styles 
st.markdown("""
<style>
    .route-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .route-sql { background: #dbeafe; color: #1e40af; }
    .route-rag { background: #dcfce7; color: #166534; }
    .route-general { background: #f3e8ff; color: #6b21a8; }
</style>
""", unsafe_allow_html=True)


# Sidebar: file upload 
with st.sidebar:
    st.title("Policy Documents")
    st.caption("Upload company policy PDFs to build the knowledge base.")

    uploaded_files = st.file_uploader(
        "Upload PDF(s)",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        for uf in uploaded_files:
            # Check if already processed in this session
            if uf.name in st.session_state.get("ingested_files", set()):
                continue

            policies_dir = os.path.join(os.path.dirname(__file__), "policies")
            os.makedirs(policies_dir, exist_ok=True)
            save_path = os.path.join(policies_dir, uf.name)
            with open(save_path, "wb") as f:
                f.write(uf.getbuffer())

            with st.spinner(f"Processing {uf.name}..."):
                result = ingest_pdf(save_path)
                st.session_state.setdefault("ingested_files", set()).add(uf.name)

            st.success(f"{uf.name} added to knowledge base")

    st.divider()
    st.subheader("Knowledge Base")
    import json
    docs_info = json.loads(list_uploaded_documents())
    if "documents" in docs_info and docs_info["documents"]:
        for doc in docs_info["documents"]:
            st.markdown(f"• {doc}")
        st.caption(f"Total chunks: {docs_info['total_chunks']}")
    else:
        st.caption("No policies uploaded yet.")

    st.divider()
    st.subheader("💡 Try asking")
    st.markdown("""
    - *"Give me an overview of Ema's profile and tickets"*
    - *"Show me all open tickets"*
    - *"Who are our Enterprise customers?"*
    - *"What is the refund policy?"* (after upload)
    """)


# Main: chat
st.title("Customer Support AI")
st.caption("A multi-agent assistant for customer profiles, tickets, and policy questions.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and "route" in msg:
            route_class = f"route-{msg['route']}"
            route_labels = {"sql": "Customer Data", "rag": "Policy Docs", "general": "General"}
            label = route_labels.get(msg["route"], msg["route"])
            st.markdown(f'<span class="route-badge {route_class}">{label}</span>', unsafe_allow_html=True)
        st.markdown(msg["content"])

# Input
if prompt := st.chat_input("Ask about customers, tickets, or policies..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = run_supervisor(prompt)
                route = result["route"]
                response = result["response"]
            except Exception as e:
                route = "general"
                response = f"Sorry, something went wrong: `{str(e)}`"

        route_class = f"route-{route}"
        route_labels = {"sql": "Customer Data", "rag": "Policy Docs", "general": "General"}
        label = route_labels.get(route, route)
        st.markdown(f'<span class="route-badge {route_class}">{label}</span>', unsafe_allow_html=True)
        st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "route": route,
    })