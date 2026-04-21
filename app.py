import os
import sys
import json
import streamlit as st
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agents"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "mcp_server"))

from supervisor import run_supervisor
from rag_tools import ingest_pdf, list_uploaded_documents
from sql_tools import get_all_customers, get_open_tickets

load_dotenv()

st.set_page_config(
    page_title="Support AI",
    page_icon="◆",
    layout="centered",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500;600&display=swap');

* { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background-color: #EDE8DF !important;
    background-image: radial-gradient(circle, #c6ac8f55 1px, transparent 1px) !important;
    background-size: 28px 28px !important;
}

#MainMenu, footer, header { visibility: hidden; }

/* Hide sidebar entirely */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }

.block-container {
    padding: 2.5rem 2rem 2rem 2rem !important;
    max-width: 820px !important;
}

/* ── Chat input ── */
[data-testid="stBottom"] {
    background: #EDE8DF !important;
    background-image: radial-gradient(circle, #c6ac8f55 1px, transparent 1px) !important;
    background-size: 28px 28px !important;
    border-top: 1px solid #c6ac8f44 !important;
}
[data-testid="stChatInput"] {
    background: #FAF7F2 !important;
    border: 1.5px solid #c6ac8f88 !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 12px #5e503f18 !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #22333b !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #c6ac8f !important;
}
[data-testid="stChatInput"] button {
    background: #22333b !important;
    border-radius: 8px !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #FAF7F2 !important;
    border: 1px solid #c6ac8f44 !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 8px #5e503f10 !important;
    margin-bottom: 1.5rem !important;
}
[data-testid="stExpander"] summary {
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #5e503f !important;
}
[data-testid="stExpander"] [data-testid="stFileUploader"] {
    background: #f0ebe0 !important;
    border: 1.5px dashed #c6ac8f88 !important;
    border-radius: 8px !important;
}

/* ── Stat cards ── */
.stat-card {
    background: #FAF7F2;
    border: 1px solid #c6ac8f44;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 2px 8px #5e503f10;
    margin-bottom: 1.5rem;
}
.stat-number {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    font-weight: 600;
    color: #22333b;
    line-height: 1;
    margin-bottom: 0.3rem;
}
.stat-label {
    font-size: 0.72rem;
    color: #c6ac8f;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 500;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.2rem 0 !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #5e503f !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #EDE8DF; }
::-webkit-scrollbar-thumb { background: #c6ac8f; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# Header 
st.markdown("""
<div style='margin-bottom:1.8rem;padding-bottom:1.2rem;border-bottom:1px solid #c6ac8f33;'>
    <p style='font-family:"Playfair Display",serif;font-size:2.6rem;font-weight:600;
              color:#22333b;line-height:1.1;margin:0 0 0.3rem 0;'>
        Support <span style='color:#c6ac8f;font-style:italic;'>Intelligence</span>
    </p>
    <p style='font-size:0.75rem;color:#c6ac8f;font-weight:400;letter-spacing:0.1em;
              text-transform:uppercase;margin:0;'>
        Multi-agent assistant &nbsp;·&nbsp; Customer data &nbsp;·&nbsp; Policy documents
    </p>
</div>
""", unsafe_allow_html=True)


# Stat cards 
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    try:
        all_customers = json.loads(get_all_customers())
        open_tickets_data = json.loads(get_open_tickets())
        total_customers = len(all_customers)
        total_open = len(open_tickets_data)
        enterprise = sum(1 for c in all_customers if c.get("plan") == "Enterprise")
        premium = sum(1 for c in all_customers if c.get("plan") == "Premium")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{total_customers}</div><div class="stat-label">Customers</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{total_open}</div><div class="stat-label">Open Tickets</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{enterprise}</div><div class="stat-label">Enterprise</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{premium}</div><div class="stat-label">Premium</div></div>', unsafe_allow_html=True)
    except:
        pass


# Knowledge base expander 
with st.expander("Knowledge Base — Upload Policy Documents", expanded=False):
    uploaded_files = st.file_uploader(
        "Drop PDF files here",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        for uf in uploaded_files:
            if uf.name in st.session_state.get("ingested_files", set()):
                st.info(f"Already indexed: {uf.name}")
                continue
            policies_dir = os.path.join(os.path.dirname(__file__), "policies")
            os.makedirs(policies_dir, exist_ok=True)
            save_path = os.path.join(policies_dir, uf.name)
            with open(save_path, "wb") as f:
                f.write(uf.getbuffer())
            with st.spinner(f"Indexing {uf.name}..."):
                ingest_pdf(save_path)
                st.session_state.setdefault("ingested_files", set()).add(uf.name)
            st.success(f"Indexed: {uf.name}")

    docs_info = json.loads(list_uploaded_documents())
    if "documents" in docs_info and docs_info["documents"]:
        st.markdown("<p style='font-size:0.8rem;color:#5e503f;font-weight:600;margin:1rem 0 0.4rem;text-transform:uppercase;letter-spacing:0.08em;'>Indexed Documents</p>", unsafe_allow_html=True)
        for doc in docs_info["documents"]:
            st.markdown(f"<p style='font-size:0.82rem;color:#22333b;margin:3px 0;padding:5px 10px;background:#f0ebe0;border-radius:5px;'>◆ {doc}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:0.72rem;color:#c6ac8f;margin-top:6px;'>{docs_info['total_chunks']} chunks indexed</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='font-size:0.82rem;color:#c6ac8f;font-style:italic;'>No documents uploaded yet. Upload a PDF above to enable policy search.</p>", unsafe_allow_html=True)


# Badge config 
BADGES = {
    "sql":     ("Customer Data", "#22333b", "#eae0d5"),
    "rag":     ("Policy Docs",   "#598392", "#eff6e0"),
    "general": ("General",       "#c6ac8f", "#22333b"),
}

def render_msg(role, content, route=None):
    if role == "user":
        st.markdown(f"""
        <div style='display:flex;justify-content:flex-end;margin:0.5rem 0;'>
            <div style='background:#22333b;color:#eae0d5;
                        border-radius:16px 16px 4px 16px;
                        padding:0.75rem 1.1rem;max-width:75%;
                        font-size:0.9rem;line-height:1.55;
                        box-shadow:0 2px 8px #22333b22;'>
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        label, bg, color = BADGES.get(route or "general", BADGES["general"])
        st.markdown(f"""
        <div style='margin:0.5rem 0;'>
            <span style='display:inline-block;background:{bg};color:{color};
                         padding:2px 10px;border-radius:20px;
                         font-size:0.68rem;font-weight:600;
                         letter-spacing:0.08em;text-transform:uppercase;
                         margin-bottom:7px;'>
                {label}
            </span>
            <div style='background:#FAF7F2;color:#22333b;
                        border-radius:4px 16px 16px 16px;
                        padding:1rem 1.3rem;max-width:90%;
                        font-size:0.9rem;line-height:1.65;
                        border:1px solid #c6ac8f33;
                        box-shadow:0 2px 10px #5e503f10;'>
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)


# Chat history 
for msg in st.session_state.messages:
    render_msg(msg["role"], msg["content"], msg.get("route"))


# Chat input 
if prompt := st.chat_input("Ask about a customer, ticket, or policy..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_msg("user", prompt)

    with st.spinner(""):
        try:
            result = run_supervisor(prompt)
            route = result["route"]
            response = result["response"]
        except Exception as e:
            route = "general"
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err:
                response = "I've hit the API rate limit. Please wait a minute and try again."
            else:
                response = f"Something went wrong. Please try again."

    render_msg("assistant", response, route)
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "route": route,
    })