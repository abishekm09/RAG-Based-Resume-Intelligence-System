import os
import ssl
import re
import streamlit as st
from pypdf import PdfReader
from ctransformers import AutoModelForCausalLM

# --- 1. Environment & Setup ---
ssl._create_default_https_context = ssl._create_unverified_context
os.environ['PYTHONHTTPSVERIFY'] = '0'

VAULT_DIR = "resume_vault"
if not os.path.exists(VAULT_DIR):
    os.makedirs(VAULT_DIR)

# --- 2. Page Configuration ---
st.set_page_config(page_title="AI Resume Vault", page_icon="⚖️", layout="wide")
st.title("⚖️ Advanced Comparative Resume Analyzer")
st.markdown("---")

# --- 3. Optimized Model Loader ---
@st.cache_resource
def load_llm():
    # Increased context_length to 2048 to handle multiple resume chunks
    return AutoModelForCausalLM.from_pretrained(
        "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf", 
        model_type="llama",
        temperature=0.1,    # Low temperature for factual consistency
        context_length=2048, 
        gpu_layers=0 
    )

llm = load_llm()

# --- 4. Logic Functions (Chunking & Ranking) ---
def get_text_chunks(text, chunk_size=600, overlap=100):
    """Breaks long resumes into overlapping pieces to preserve context."""
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i : i + chunk_size])
    return chunks

def rank_relevant_chunks(query, chunks, top_n=2):
    """Simple keyword-based search to find the most relevant parts of a resume."""
    query_words = set(re.findall(r'\w+', query.lower()))
    if not query_words: return []
    
    scored_chunks = []
    for chunk in chunks:
        # Score based on keyword frequency
        score = sum(1 for word in query_words if word in chunk.lower())
        if score > 0:
            scored_chunks.append((score, chunk))
    
    # Sort by score (highest first)
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [c[1] for c in scored_chunks[:top_n]]

# --- 5. Sidebar: Management ---
with st.sidebar:
    st.header("📂 Data Management")
    uploaded_file = st.file_uploader("Upload New PDF", type="pdf")
    
    if uploaded_file:
        reader = PdfReader(uploaded_file)
        text = "".join([page.extract_text() for page in reader.pages])
        
        file_path = os.path.join(VAULT_DIR, f"{uploaded_file.name}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
        st.success(f"Added {uploaded_file.name} to Vault!")

    if st.button("🗑️ Clear All Resumes"):
        for f in os.listdir(VAULT_DIR):
            os.remove(os.path.join(VAULT_DIR, f))
        st.rerun()

    st.header("🗄️ Loaded Candidates")
    files = os.listdir(VAULT_DIR)
    for f in files:
        st.write(f"👤 {f.replace('.txt', '')}")

# --- 6. The "Brain": Retrieval and Analysis ---
st.header("💬 Ask the Expert")
user_query = st.text_input("Example: Which candidate has the strongest Python and SQL background?")

if user_query:
    combined_context = ""
    files = os.listdir(VAULT_DIR)
    
    if not files:
        st.warning("Please upload resumes to the vault first.")
    else:
        with st.spinner("🔍 Searching vault and ranking relevance..."):
            for filename in files:
                with open(os.path.join(VAULT_DIR, filename), "r", encoding="utf-8") as f:
                    full_text = f.read()
                    all_chunks = get_text_chunks(full_text)
                    
                    # Find only the parts of THIS resume that match the query
                    matches = rank_relevant_chunks(user_query, all_chunks)
                    
                    if matches:
                        candidate_name = filename.replace('.txt', '')
                        combined_context += f"\n[START DATA FOR {candidate_name}]\n"
                        combined_context += "\n".join(matches)
                        combined_context += f"\n[END DATA FOR {candidate_name}]\n"

            if not combined_context:
                # Fallback: If no keywords match, just take a snippet of everyone
                combined_context = "No direct keyword matches found. Analyzing general profiles..."

            # 7. Final Prompt Execution
            full_prompt = f"""<|system|>
You are a technical recruiter. Use the following resume snippets to answer the user's question accurately. 
If the information isn't in the context, say you don't know. 
Context: {combined_context}
</s>
<|user|>
{user_query}</s>
<|assistant|>"""

            response = llm(full_prompt)
            st.subheader("AI Analysis")
            st.info(response)

# --- Visual UI Touch ---
if not user_query and not files:
    st.write("👈 Start by uploading candidate resumes in the sidebar.")
