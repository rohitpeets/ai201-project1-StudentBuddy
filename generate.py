"""
generate.py
-----------
Milestone 5 — Generation and Interface
McNeese State University Professor Reviews RAG System
"""

import os
from dotenv import load_dotenv
from groq import Groq
import gradio as gr

from embed_and_retrieve import retrieve, embed_and_store
from ingest_and_chunk import ingest_all

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file.")

groq_client = Groq(api_key=GROQ_API_KEY)

print("[INFO] Loading and embedding chunks...")
chunks = ingest_all()
embed_and_store(chunks)
print("[INFO] Ready.\n")

SYSTEM_PROMPT = """You are a helpful assistant for McNeese State University students.
You help students make informed decisions about which professors to take based on real student reviews.

STRICT GROUNDING RULES:
- Answer ONLY using the information provided in the retrieved reviews below.
- Do NOT use your general training knowledge about professors, universities, or teaching.
- If the retrieved reviews do not contain enough information to answer the question, say exactly:
  "I don't have enough information in the current reviews to answer that question."
- Do NOT make up or infer anything not explicitly stated in the reviews.
- Do NOT give advice beyond what the reviews actually say.

SOURCE ATTRIBUTION RULES:
- After your answer, always include a "Sources:" section.
- List each review you drew from, formatted as:
  - [Professor Name] | [Course] | [Date] | Rating: [X/5]
- Only list sources you actually used in your answer.

Keep your answer clear, helpful, and concise."""


def ask(query: str) -> dict:
    results = retrieve(query)
    if not results:
        return {
            "answer": "I don't have reviews for that professor in the current dataset.",
            "sources": []
        }
    context_blocks = []
    for i, r in enumerate(results, 1):
        block = (
            f"Review {i}:\n"
            f"Professor: {r['professor']}\n"
            f"Course: {r['course']}\n"
            f"Date: {r['date']}\n"
            f"Rating: {r['rating']}/5\n"
            f"Text: {r['text']}"
        )
        context_blocks.append(block)
    context = "\n\n".join(context_blocks)
    user_message = f"""Retrieved reviews:\n\n{context}\n\n---\n\nStudent question: {query}\n\nAnswer the question using ONLY the reviews above. Cite your sources at the end."""
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
        temperature=0.2,
        max_tokens=1024,
    )
    answer = response.choices[0].message.content
    sources = [
        f"{r['professor']} | {r['course']} | {r['date']} | Rating: {r['rating']}/5"
        for r in results
    ]
    return {"answer": answer, "sources": sources}


def handle_query(question: str):
    if not question.strip():
        return "Please enter a question.", ""
    result  = ask(question)
    answer  = result["answer"]
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return answer, sources


custom_css = """
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Reset Gradio chrome ── */
footer, .gradio-footer { display: none !important; }
.contain { padding: 0 !important; }
#component-0 { gap: 0 !important; }

body, .gradio-container, .main, .wrap {
    background: #f7f6f2 !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #1c1c1c !important;
}

.gradio-container {
    max-width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* ── Header ── */
#header {
    background: #1a3a2a;
    padding: 48px 60px 40px;
    border-bottom: 4px solid #2d6a4f;
}

#header .tag {
    display: inline-block;
    background: rgba(255,255,255,0.1);
    color: #74c69d;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 20px;
    margin-bottom: 16px;
}

#header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 42px;
    font-weight: 400;
    color: #ffffff;
    line-height: 1.15;
    margin: 0 0 12px 0;
}

#header h1 em {
    color: #74c69d;
    font-style: normal;
}

#header p {
    font-size: 15px;
    color: #a8c5b5;
    font-weight: 300;
    margin: 0;
}

/* ── Main layout ── */
#main-content {
    display: grid;
    grid-template-columns: 380px 1fr;
    min-height: calc(100vh - 220px);
}

#left-panel {
    background: #ffffff;
    border-right: 1px solid #e5e2db;
    padding: 36px 32px;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

#right-panel {
    background: #f7f6f2;
    padding: 36px 40px;
    display: flex;
    flex-direction: column;
    gap: 24px;
}

/* ── Input section ── */
#left-panel .section-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #2d6a4f;
    margin-bottom: 8px;
}

#left-panel textarea,
#left-panel input {
    background: #f7f6f2 !important;
    border: 1.5px solid #ddd9d0 !important;
    border-radius: 8px !important;
    color: #1c1c1c !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    padding: 14px 16px !important;
    line-height: 1.6 !important;
    resize: none !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    width: 100% !important;
}

#left-panel textarea:focus,
#left-panel input:focus {
    border-color: #2d6a4f !important;
    box-shadow: 0 0 0 3px rgba(45,106,79,0.1) !important;
    outline: none !important;
    background: #ffffff !important;
}

#left-panel textarea::placeholder {
    color: #b0aca4 !important;
    font-style: italic !important;
}

/* label override */
#left-panel label span,
#right-panel label span {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    color: #2d6a4f !important;
}

#right-panel .sources-box label span {
    color: #7a7570 !important;
}

/* ── Ask button ── */
#ask-btn button {
    background: #2d6a4f !important;
    border: none !important;
    border-radius: 8px !important;
    color: #ffffff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    padding: 14px !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: background 0.2s, transform 0.1s, box-shadow 0.2s !important;
    box-shadow: 0 2px 8px rgba(45,106,79,0.25) !important;
}

#ask-btn button:hover {
    background: #40916c !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(45,106,79,0.35) !important;
}

/* ── Example chips ── */
#examples-section {
    margin-top: 4px;
}

#examples-section .chip-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #9c9890;
    margin-bottom: 10px;
}

#examples-section .chips {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

#examples-section .chip {
    background: #f0ede6;
    border: 1px solid #e5e2db;
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 12px;
    color: #4a4540;
    cursor: pointer;
    transition: background 0.15s, border-color 0.15s;
    text-align: left;
    font-family: 'DM Sans', sans-serif;
}

#examples-section .chip:hover {
    background: #e8f5ee;
    border-color: #2d6a4f;
    color: #2d6a4f;
}

/* ── Output panels ── */
#right-panel textarea {
    background: #ffffff !important;
    border: 1.5px solid #e5e2db !important;
    border-radius: 8px !important;
    color: #1c1c1c !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    line-height: 1.75 !important;
    padding: 16px !important;
    resize: none !important;
}

/* ── Footer ── */
#footer {
    background: #1a3a2a;
    padding: 20px 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

#footer .prof-list {
    font-size: 11px;
    color: #74c69d;
    letter-spacing: 0.04em;
}

#footer .built-tag {
    font-size: 11px;
    color: #4a8a6a;
    font-weight: 500;
}

/* scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #f7f6f2; }
::-webkit-scrollbar-thumb { background: #d5d0c8; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #2d6a4f; }
"""

with gr.Blocks(css=custom_css, title="McNeese Professor Guide") as demo:

    gr.HTML("""
    <div id="header">
        <div class="tag">McNeese State University</div>
        <h1>Unofficial <em>Professor Guide</em></h1>
        <p>Real student reviews · Grounded answers · No hallucination</p>
    </div>
    """)

    with gr.Row(elem_id="main-content"):

        with gr.Column(elem_id="left-panel"):
            inp = gr.Textbox(
                label="Your Question",
                placeholder='e.g. "Does Hardee give partial credit on exams?"',
                lines=4,
            )
            btn = gr.Button("Ask →", variant="primary", elem_id="ask-btn")

            gr.HTML("""
            <div id="examples-section">
                <div class="chip-label">Try asking</div>
                <div class="chips">
                    <div class="chip" onclick="document.querySelector('textarea').value='Does Hardee give partial credit on exams?'">
                        Does Hardee give partial credit on exams?
                    </div>
                    <div class="chip" onclick="document.querySelector('textarea').value='Who should I take CSCI309 with?'">
                        Who should I take CSCI309 with?
                    </div>
                    <div class="chip" onclick="document.querySelector('textarea').value='What strategies help in Bei Xie\\'s class?'">
                        What strategies help in Bei Xie's class?
                    </div>
                    <div class="chip" onclick="document.querySelector('textarea').value='Should I study past quizzes for Lavergne\\'s final?'">
                        Should I study past quizzes for Lavergne's final?
                    </div>
                </div>
            </div>
            """)

        with gr.Column(elem_id="right-panel"):
            answer = gr.Textbox(
                label="Answer",
                lines=14,
                interactive=False,
            )
            sources = gr.Textbox(
                label="Retrieved From",
                lines=6,
                interactive=False,
                elem_classes="sources-box",
            )

    gr.HTML("""
    <div id="footer">
        <div class="prof-list">
            Andrew Mudd &middot; Bei Xie &middot; Constance Kersten &middot; Jennifer Lavergne &middot;
            Lara Guidroz &middot; Lyle Hardee &middot; Shaikh Samad &middot; Susie Beasley &middot;
            Tristan Salinas &middot; Vipin Menon
        </div>
        <div class="built-tag">Built with Gradio + Groq</div>
    </div>
    """)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

if __name__ == "__main__":
    demo.launch()
