import { useRef, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000/api/extract";

function formatFileSize(bytes) {
  if (!bytes) return "PDF document";
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function getPromptMode(prompt) {
  const normalizedPrompt = prompt.toLowerCase();
  if (normalizedPrompt.includes("compare") || normalizedPrompt.includes("difference")) return "comparison";
  if (normalizedPrompt.includes("point") || normalizedPrompt.includes("step") || normalizedPrompt.includes("list")) return "points";
  if (normalizedPrompt.includes("summar")) return "summary";
  return "answer";
}

function displayLabel(value) {
  return String(value)
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/[_-]+/g, " ")
    .replace(/^./, (character) => character.toUpperCase());
}

function renderValue(value) {
  if (Array.isArray(value)) {
    return <ul className="value-list">{value.map((item, index) => <li key={`${index}-${String(item)}`}>{renderValue(item)}</li>)}</ul>;
  }
  if (value && typeof value === "object") {
    return <dl className="detail-list">{Object.entries(value).map(([key, item]) => <div className="detail-row" key={key}><dt>{displayLabel(key)}</dt><dd>{renderValue(item)}</dd></div>)}</dl>;
  }
  return <span>{String(value ?? "Not specified")}</span>;
}

function AnswerContent({ answer, mode }) {
  if (!answer) return <p className="muted-copy">No answer was returned for this question.</p>;
  const lines = answer.split(/\n+/).map((line) => line.replace(/^\s*(?:[-*•]|\d+[.)])\s*/, "").trim()).filter(Boolean);
  if (mode === "points" && lines.length > 1) {
    return <ol className="answer-points">{lines.map((line, index) => <li key={`${index}-${line}`}>{line}</li>)}</ol>;
  }
  return <div className="answer-copy">{answer.split(/\n+/).map((paragraph, index) => <p key={`${index}-${paragraph}`}>{paragraph}</p>)}</div>;
}

function App() {
  const inputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [prompt, setPrompt] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isDragging, setIsDragging] = useState(false);

  const selectFile = (selectedFile) => {
    if (!selectedFile) return;
    if (selectedFile.type !== "application/pdf" && !selectedFile.name.toLowerCase().endsWith(".pdf")) {
      setError("Please choose a PDF document.");
      return;
    }
    setFile(selectedFile);
    setResult(null);
    setError("");
  };

  const handleFileChange = (event) => selectFile(event.target.files[0]);
  const handleDrop = (event) => { event.preventDefault(); setIsDragging(false); selectFile(event.dataTransfer.files[0]); };

  const handleUpload = async (event) => {
    event.preventDefault();
    if (!file) { setError("Add a PDF before asking a question."); return; }
    if (!prompt.trim()) { setError("Add a question or instruction for the document."); return; }
    setLoading(true);
    setError("");
    setResult(null);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("prompt", prompt.trim());
    try {
      const response = await fetch(API_URL, { method: "POST", body: formData });
      const data = await response.json().catch(() => null);
      if (!response.ok) throw new Error(data?.detail || "Document extraction failed.");
      if (!data?.document) throw new Error("The document service returned an incomplete response.");
      setResult(data);
    } catch (err) {
      setError(err.message || "We could not process that document. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const document = result?.document;
  const extractedInformation = document?.extracted_information;
  const informationEntries = extractedInformation && typeof extractedInformation === "object" ? Object.entries(extractedInformation) : [];
  const mode = getPromptMode(prompt);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-lockup"><div className="brand-mark" aria-hidden="true"><span /></div><div><strong>FDE</strong><span>Document Intelligence</span></div></div>
        <div className="secure-label"><span className="status-dot" /> Grounded in your document</div>
      </header>

      <main className="workspace">
        <section className="intro-block"><p className="eyebrow">AI document workspace</p><h1>Ask your documents<br /><em>anything.</em></h1><p className="intro-copy">Upload a PDF and get clear, source-grounded answers in seconds.</p></section>

        <form className="query-layout" onSubmit={handleUpload}>
          <section className="query-panel panel">
            <div className="section-heading"><div><span className="step-number">01</span><h2>Choose a document</h2></div>{file && <button className="text-button" type="button" onClick={() => inputRef.current?.click()}>Replace</button>}</div>
            <input ref={inputRef} className="visually-hidden" type="file" accept="application/pdf,.pdf" onChange={handleFileChange} />
            <div className={`dropzone ${isDragging ? "is-dragging" : ""} ${file ? "has-file" : ""}`} onDragOver={(event) => { event.preventDefault(); setIsDragging(true); }} onDragLeave={() => setIsDragging(false)} onDrop={handleDrop} onClick={() => inputRef.current?.click()} role="button" tabIndex="0" onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") inputRef.current?.click(); }}><div className="file-icon" aria-hidden="true">PDF</div>{file ? <><strong>{file.name}</strong><span>{formatFileSize(file.size)} · Ready to analyze</span></> : <><strong>Drop your PDF here</strong><span>or click to browse from your computer</span></>}</div>

            <div className="section-heading prompt-heading"><div><span className="step-number">02</span><h2>What would you like to know?</h2></div></div>
            <textarea value={prompt} onChange={(event) => { setPrompt(event.target.value); setError(""); }} placeholder="Ask a question or describe what you want to find..." rows="5" />
            <div className="prompt-footer"><span>Answers are generated only from your uploaded document.</span><span>{prompt.length}/2,000</span></div>
            {error && <div className="message error-message" role="alert"><span className="message-icon">!</span><div><strong>Something needs your attention</strong><span>{error}</span></div></div>}
            <button className="ask-button" type="submit" disabled={loading || !file || !prompt.trim()}>{loading ? <><span className="loader" /> Reading your document...</> : <>Ask document <span aria-hidden="true">-&gt;</span></>}</button>
          </section>

          <aside className="context-panel"><div className="side-heading"><span className="eyebrow">Your workspace</span><span className="context-badge">Private</span></div><div className="side-divider" /><div className="side-feature"><span className="feature-icon">01</span><div><strong>One clear answer</strong><p>Get focused responses shaped around your question.</p></div></div><div className="side-feature"><span className="feature-icon">02</span><div><strong>Source aware</strong><p>Every result stays grounded in the pages you upload.</p></div></div><div className="side-feature"><span className="feature-icon">03</span><div><strong>Made for reading</strong><p>See key information without sorting through raw data.</p></div></div><div className="side-note"><span className="status-dot" /> Your files are processed for this session only.</div></aside>
        </form>

        {loading && <section className="loading-panel panel"><div className="loading-orb"><span /></div><div><p className="eyebrow">Working on it</p><h2>Reading between the lines...</h2><p>Searching the document for the most relevant context.</p></div></section>}
        {!loading && !result && !error && <section className="empty-state"><div className="empty-line" /><p className="eyebrow">Your answer will appear here</p><h2>Insight, without the search.</h2><p>Ask for an explanation, a summary, a comparison, or a specific detail from your document.</p></section>}
        {!loading && result && document && <section className="results-area"><div className="results-header"><div><p className="eyebrow">Document insight</p><h2>{mode === "comparison" ? "A closer comparison" : mode === "summary" ? "Document summary" : "Here is what I found"}</h2></div><span className="grounded-badge"><span className="status-dot" /> Grounded response</span></div><div className="results-grid"><div className="answer-column"><article className="answer-card panel"><div className="card-label"><span className="answer-symbol">A</span><span>Answer</span></div><AnswerContent answer={document.answer} mode={mode} /></article>{informationEntries.length > 0 && <article className="info-card panel"><div className="card-label"><span className="answer-symbol">+</span><span>Extracted information</span></div><div className="information-grid">{informationEntries.map(([key, value]) => <div className="information-item" key={key}><span>{displayLabel(key)}</span>{renderValue(value)}</div>)}</div></article>}{document.missing_information?.length > 0 && <article className="missing-card panel"><div className="card-label"><span className="answer-symbol">?</span><span>Not found in document</span></div><ul>{document.missing_information.map((item) => <li key={item}>{item}</li>)}</ul></article>}</div><aside className="sources-card panel"><div className="card-label"><span className="answer-symbol">#</span><span>Sources</span></div><p className="source-intro">This answer was informed by these document pages.</p>{document.sources?.length ? <div className="source-list">{document.sources.map((source, index) => <div className="source-item" key={`${source.file_name}-${source.page_number}-${index}`}><span className="page-number">{source.page_number}</span><div><strong>{source.file_name}</strong><span>Page {source.page_number}</span></div></div>)}</div> : <p className="muted-copy">No page references were returned.</p>}</aside></div></section>}
      </main>
      <footer className="footer"><span>FDE Document Intelligence</span><span>Answers stay grounded in your source material</span></footer>
    </div>
  );
}

export default App;