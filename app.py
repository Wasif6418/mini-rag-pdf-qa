from __future__ import annotations

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse

from rag.chunking import split_into_chunks
from rag.pdf_loader import extract_pages
from rag.qa import build_answer
from rag.retriever import TfidfRetriever

app = FastAPI(title="Mini RAG PDF QA")


HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Mini RAG PDF QA</title>
  <style>
    :root {
      --bg: #f5f0e8;
      --card: #fffaf2;
      --ink: #1f2937;
      --muted: #6b7280;
      --line: #d6c7b2;
      --accent: #b45309;
      --accent-soft: #fde7c2;
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, #fff8ef 0%, transparent 35%),
        linear-gradient(135deg, #f3eadb 0%, #efe4d1 100%);
      min-height: 100vh;
    }

    .shell {
      max-width: 900px;
      margin: 40px auto;
      padding: 24px;
    }

    .hero {
      padding: 28px;
      border: 1px solid var(--line);
      background: rgba(255, 250, 242, 0.92);
      box-shadow: 0 12px 32px rgba(120, 78, 21, 0.08);
    }

    h1 {
      margin: 0 0 10px;
      font-size: clamp(2rem, 5vw, 3.5rem);
      line-height: 1;
    }

    p {
      color: var(--muted);
      line-height: 1.6;
    }

    form {
      margin-top: 24px;
      display: grid;
      gap: 14px;
    }

    label {
      font-size: 0.95rem;
      font-weight: 700;
    }

    input, textarea, button {
      width: 100%;
      padding: 12px 14px;
      border: 1px solid var(--line);
      background: white;
      font: inherit;
    }

    textarea { min-height: 120px; resize: vertical; }

    button {
      background: var(--accent);
      color: white;
      cursor: pointer;
      border: none;
      font-weight: 700;
    }

    button:hover { filter: brightness(0.96); }

    .result {
      margin-top: 24px;
      padding: 18px;
      border-left: 4px solid var(--accent);
      background: var(--accent-soft);
      white-space: pre-wrap;
    }

    .sources {
      margin-top: 22px;
      display: grid;
      gap: 14px;
    }

    .source {
      background: var(--card);
      border: 1px solid var(--line);
      padding: 16px;
    }

    .source strong {
      display: block;
      margin-bottom: 8px;
    }
  </style>
</head>
<body>
  <div class="shell">
    <div class="hero">
      <h1>Mini RAG PDF QA</h1>
      <p>Upload one PDF, ask one question, and inspect the retrieved context. This is a lightweight local Retrieval-Augmented Generation demo built for interviews and side projects.</p>
      <form id="qa-form">
        <div>
          <label for="file">PDF file</label>
          <input id="file" name="file" type="file" accept="application/pdf" required />
        </div>
        <div>
          <label for="question">Question</label>
          <textarea id="question" name="question" placeholder="Ask something about the PDF..." required></textarea>
        </div>
        <button type="submit">Ask</button>
      </form>
      <div id="result"></div>
    </div>
  </div>

  <script>
    const form = document.getElementById("qa-form");
    const result = document.getElementById("result");

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      result.innerHTML = "<div class='result'>Working on it...</div>";

      const formData = new FormData(form);
      const response = await fetch("/ask", {
        method: "POST",
        body: formData
      });

      const payload = await response.json();

      if (!response.ok) {
        result.innerHTML = `<div class="result">${payload.detail || "Something went wrong."}</div>`;
        return;
      }

      const sources = payload.sources.map((source) => `
        <div class="source">
          <strong>Page ${source.page} • ${source.chunk_id} • score ${source.score}</strong>
          <div>${source.text}</div>
        </div>
      `).join("");

      result.innerHTML = `
        <div class="result">${payload.answer}</div>
        <div class="sources">${sources}</div>
      `;
    });
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return HTML_PAGE


@app.post("/ask")
async def ask_pdf(
    file: UploadFile = File(...),
    question: str = Form(...),
) -> dict:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    pdf_bytes = await file.read()
    pages = extract_pages(pdf_bytes)
    if not pages:
        raise HTTPException(
            status_code=400,
            detail="No text could be extracted from this PDF. Try a text-based PDF.",
        )

    chunks = split_into_chunks(pages)
    retriever = TfidfRetriever(chunks)
    retrieved_chunks = retriever.search(question)
    answer = build_answer(question, retrieved_chunks)

    return {
      "question": question,
      "answer": answer.answer,
      "pages_indexed": len(pages),
      "chunks_indexed": len(chunks),
      "sources": answer.sources,
    }
