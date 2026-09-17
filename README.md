# FDE Document Intelligence

FDE is a prompt-driven AI document understanding and extraction system. A user uploads a PDF, asks a natural-language question, and receives a grounded answer, structured information, missing-information notices, and page-aware source references.

This project is a document understanding/extraction system. It is not an insurance underwriting engine, risk-scoring system, or automated decision-making system.

## Project Objective

The system is designed to:

1. Accept a PDF document and a user prompt.
2. Extract and prepare document text for retrieval.
3. Retrieve relevant content from the uploaded document.
4. Ask the LLM to answer the user's request using that retrieved context.
5. Return a flexible, source-aware response for the frontend.

Answers are intended to remain grounded in the uploaded document rather than rely on unrelated external knowledge.

## Architecture

```text
React/Vite frontend
				|
				| multipart/form-data: file + prompt
				v
FastAPI API
				|
				v
Document pipeline
	PDF parsing -> preprocessing -> chunking -> embeddings
				-> Chroma persistence -> retrieval -> prompt-driven extraction
				v
Structured document response
```

The backend is organized by responsibility under `backend/`. The frontend is a separate React/Vite application under `frontend/`.

## Backend Pipeline

`DocumentPipeline` processes each request in this order:

1. Parse the PDF.
2. Preprocess the extracted document text.
3. Create text chunks with document metadata.
4. Generate embeddings for the chunks.
5. Persist chunks and embeddings in ChromaDB.
6. Retrieve relevant chunks for the user's prompt.
7. Build context containing source filename and page metadata.
8. Generate a prompt-driven response from the grounded context.
9. Deduplicate source references by filename and page number.

The API currently calls the pipeline with `top_k=15`.

## RAG Workflow

The retriever performs the following work:

- Understands the query and identifies topics, concepts, keywords, and section hints.
- Performs semantic retrieval using embeddings.
- Performs lexical retrieval using query topics and terms.
- Combines the retrieval signals.
- Selects relevant and diverse chunks for the final context.

Retrieved context is filtered to the uploaded document filename. Each context item carries page metadata so the response can include source references.

## Prompt-Driven Extraction

The prompt analyzer identifies response requirements such as:

- Explanation, summary, comparison, or information extraction requests.
- Requested word limits.
- Requested point counts.
- Table, list, points, or paragraph formats.
- Weak prompts that do not describe a specific task.

Weak prompts receive a request for clarification instead of triggering an unnecessary LLM generation request.

## Grounding Approach

The LLM receives retrieved text labeled with the source document and page number. The extraction prompt instructs the response generation to use the supplied document context. The resulting source list is built from the retrieved chunks and deduplicated by `(file_name, page_number)`.

The frontend displays the returned answer and structured fields; it does not invent document facts or create source references.

## Flexible Response Schema

`POST /api/extract` returns:

```json
{
	"document": {
		"answer": "...",
		"extracted_information": {},
		"missing_information": [],
		"sources": [
			{
				"file_name": "...",
				"page_number": 11
			}
		]
	}
}
```

`extracted_information` is a dynamic dictionary and may contain strings, numbers, arrays, nested objects, or empty values. `missing_information` contains requested details that were not found in the retrieved document context.

## Frontend

The React/Vite frontend provides:

- PDF selection, replacement, and drag-and-drop upload.
- A natural-language prompt input.
- Loading, validation, network, and API error states.
- Human-readable answer presentation for prose, numbered responses, and Markdown tables.
- Dynamic extracted-information cards.
- Missing-information and source sections with filenames, page numbers, and source counts.
- Responsive presentation without exposing raw JSON to the user.

The frontend calls `http://127.0.0.1:8000/api/extract` during local development.

## API Endpoint

```text
POST /api/extract
Content-Type: multipart/form-data
```

Form fields:

- `file`: the uploaded PDF.
- `prompt`: the user's question or extraction request.

The API rejects missing filenames, non-PDF files, and empty prompts with HTTP 400. Processing or pipeline failures are returned as HTTP 500 responses.

## Project Structure

```text
backend/
	api/             FastAPI application and routes
	parser/          PDF parsing
	preprocessing/   Text cleanup
	chunking/        Chunk creation
	embeddings/      Embedding generation
	vector_store/    ChromaDB persistence
	rag/             Retrieval and ranking
	prompts/         Query and response analysis
	extraction/      Grounded response extraction
	llm/             Groq LLM service
	schemas/         Response models
	pipeline/        End-to-end document pipeline
frontend/
	src/             React application and styles
tests/             Backend extraction, prompt, and safety tests
data/raw/pdf/      Local PDF inputs and test documents
documents/         Local uploads, processed data, and vector stores
```

Generated uploads, processed files, vector databases, `.env`, and virtual environments should remain untracked.

## Installation

### Backend

From the repository root, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the backend dependencies used by this project:

```powershell
python -m pip install fastapi uvicorn python-multipart pydantic python-dotenv groq chromadb sentence-transformers pymupdf pytest requests
```

The embedding and language-model packages may download additional model data on first use.

### Frontend

```powershell
cd frontend
npm install
```

## Environment Variables

Create a local `.env` file in the repository root:

```text
GROQ_API_KEY=your_groq_api_key
```

The backend loads `GROQ_API_KEY` with `python-dotenv`. Never commit `.env`, API keys, or other secrets. The model used by the current LLM service defaults to `openai/gpt-oss-120b` through the Groq client.

## Run the Backend

From the repository root with the virtual environment active:

```powershell
python -m uvicorn backend.api.main:app --reload
```

The API is available at `http://127.0.0.1:8000`. FastAPI's interactive documentation is available at `http://127.0.0.1:8000/docs`.

## Run the Frontend

In a second terminal:

```powershell
cd frontend
npm run dev
```

The Vite development server is normally available at `http://127.0.0.1:5173`.

## How to Test

Run the backend test suite from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Build and lint the frontend:

```powershell
cd frontend
npm run build
npm run lint
```

Test the API directly with a PDF and prompt:

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/extract `
	-F "file=@data/raw/pdf/Lecture Notes_CC UNIT-3.pdf" `
	-F "prompt=What is MapReduce?"
```

For an end-to-end test, start both servers, upload a PDF in the frontend, enter a prompt, and verify the answer, missing-information section, and page references.

## Dataset and Testing Documents

Local PDF inputs are stored under `data/raw/pdf/`. The repository includes documents such as:

- `Lecture Notes_CC UNIT-3.pdf`
- `s10462-026-11678-4_reference.pdf`
- Additional research PDFs used for parser and retrieval checks.

Backend tests are under `tests/` and cover document extraction, prompt behavior, safety behavior, and real extraction scenarios. Local Chroma stores and processed artifacts under `documents/` are runtime/test data and should not be committed.

## Limitations

- A valid `GROQ_API_KEY` and network access to the configured LLM provider are required for extraction requests.
- The current API accepts PDF uploads only.
- Results depend on the text that can be extracted from the PDF and the quality of retrieval.
- ChromaDB persistence is local to the configured `documents/` directories.
- The frontend shows page references but does not open or navigate to a PDF page.
- LLM responses can vary between requests, and an occasional provider or processing failure may require retrying.
- This project does not provide authentication, multi-user isolation, or production deployment configuration.

## Current Scope

The current scope is document parsing, retrieval, grounded question answering, and flexible information extraction from uploaded PDFs.

It does not include insurance underwriting, risk analysis, risk scoring, eligibility decisions, claims decisions, or any other automated decision-making workflow.
