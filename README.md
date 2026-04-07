# Mini RAG PDF QA

A small, interview-friendly PDF question answering project in Python.

It is intentionally simple:

- `pypdf` extracts text from PDFs
- the text is split into chunks
- `TfidfVectorizer` builds a lightweight local vector index
- the app retrieves the most relevant chunks for a question
- a tiny answer synthesizer builds a grounded answer with sources

There are no paid APIs, no database, and no model downloads.

## Why This Is GitHub Friendly

- Small and easy to read
- No paid API keys required
- No database setup
- Local-only dependencies
- Clean `.gitignore` so virtual environments and cache files stay out of the repo

## Features

- Upload a PDF from the browser
- Ask questions against the uploaded document
- View retrieved context chunks and page references
- Run fully on a local machine for free

## Project Structure

```text
mini_rag_pdf_qa/
  app.py
  requirements.txt
  README.md
  sample_data/
    make_sample_pdf.py
  rag/
    __init__.py
    pdf_loader.py
    chunking.py
    retriever.py
    qa.py
```



## Sample PDF

You can generate a tiny demo PDF with:

```bash
python sample_data/make_sample_pdf.py
```

This creates `sample_data/sample_company_handbook.pdf`.



## Limitations

- Best for text-based PDFs, not scanned image PDFs
- Answer generation is extractive rather than LLM-based
- Index is rebuilt per request to keep the demo small and stateless
