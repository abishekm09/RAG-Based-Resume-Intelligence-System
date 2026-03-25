⚖️ Advanced Comparative Resume AnalyzerAn AI-powered document intelligence tool designed for recruiters and HR professionals. This application allows you to upload multiple PDF resumes into a "Local Vault," where a TinyLlama-1.1B model performs comparative analysis, skill gap detection, and candidate ranking—all 100% offline and private.

🚀 Features
Local RAG Pipeline: Implements Retrieval-Augmented Generation without external APIs or cloud costs.
Smart Chunking: Processes long resumes using a sliding-window strategy (600 characters with 100 overlap) to maintain context.
Heuristic Retrieval: A custom keyword-ranking engine filters irrelevant data, feeding only the most important "snippets" to the LLM.
Privacy-First: Processes all data locally using GGUF-quantized models—no data ever leaves your machine.
Comparative Analysis: Specifically optimized to compare multiple candidates side-by-side based on user queries.

🛠️ Tech Stack
Frontend: Streamlit
LLM Engine: ctransformers (TinyLlama-1.1B-Chat)
PDF Parsing: PyPDF
Format: GGUF (Quantized for CPU efficiency)

📦 Installation
1. Clone the repository:
   Bash
   git clone https://github.com/your-username/resume-analyzer-ai.git
   cd resume-analyzer-ai
2. Install dependencies:
   Bash
   pip install streamlit ctransformers pypdf
3. Download the Model:
   Download tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf from Hugging Face and place it in the project root folder.
4. Run the App:
   Bash
   streamlit run app.py
   
🧠 How It Works
Ingestion: PDFs are parsed and stored as plain text in the resume_vault/ directory.
Chunking: The system breaks the text into overlapping segments to ensure skills and experience aren't "cut in half".
Ranking: When you ask a question, the system scans all chunks for relevant keywords.
Synthesis: The LLM receives the top-ranked chunks as "Context" and generates a comparative answer.
