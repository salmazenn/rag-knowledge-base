"""
RAG Knowledge Base — Interface Streamlit
Support client avec base de connaissances pré-indexée
"""

import streamlit as st
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))
from rag import load_vectorstore, build_qa_chain, ask

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Support Client",
    page_icon="💬",
    layout="centered"
)

st.title("💬 Support Client")
st.caption("Posez vos questions — je consulte notre base de connaissances pour vous répondre.")

# ── Session state ─────────────────────────────────────────────────────────────

if "chain" not in st.session_state:
    with st.spinner("Chargement de la base de connaissances..."):
        try:
            vectorstore = load_vectorstore()
            st.session_state.chain = build_qa_chain(vectorstore)
            st.session_state.ready = True
        except Exception as e:
            st.session_state.ready = False
            st.session_state.error = str(e)

if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Status ────────────────────────────────────────────────────────────────────

if not st.session_state.get("ready", False):
    st.error("⚠️ Base de connaissances non disponible. Veuillez contacter l'administrateur.")
    st.info("💡 Admin : lancez `python src/ingest.py` pour indexer les documents.")
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("ℹ️ À propos")
    st.markdown("""
    Cet assistant répond à vos questions en consultant 
    notre base de connaissances.
    
    **Ce que je peux faire :**
    - Répondre aux questions fréquentes
    - Expliquer nos produits et services
    - Vous guider dans vos démarches
    
    **Besoin d'aide humaine ?**
    
    📧 support@entreprise.com
    📞 1-800-XXX-XXXX
    """)
    st.divider()
    if st.button("🗑️ Effacer la conversation"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.markdown("**Propulsé par :** Groq ⚡ + ChromaDB")

# ── Chat ──────────────────────────────────────────────────────────────────────

# Message de bienvenue
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("Bonjour ! 👋 Je suis votre assistant de support. Comment puis-je vous aider aujourd'hui ?")

# Historique
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sources" in msg and msg["sources"]:
            with st.expander("📎 Sources consultées"):
                for s in msg["sources"]:
                    st.markdown(f"- `{s}`")

# Input
if prompt := st.chat_input("Posez votre question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultation de la base de connaissances..."):
            result = ask(st.session_state.chain, prompt)
        st.markdown(result["answer"])
        if result["sources"]:
            with st.expander("📎 Sources consultées"):
                for s in result["sources"]:
                    st.markdown(f"- `{s}`")

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result["sources"]
    })