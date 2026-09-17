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

function splitTableRow(line) {
  return line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim());
}

function isTableSeparator(line) {
  return splitTableRow(line).every((cell) => /^:?-{3,}:?$/.test(cell));
}

function parseMarkdownTable(answer) {
  const lines = answer.split(/\r?\n/);
  for (let index = 0; index < lines.length - 1; index += 1) {
    if (!lines[index].includes("|") || !isTableSeparator(lines[index + 1])) continue;
    const headers = splitTableRow(lines[index]);
    const rows = [];
    let end = index + 2;
    while (end < lines.length && lines[end].trim() && lines[end].includes("|")) {
      rows.push(splitTableRow(lines[end]));
      end += 1;
    }
    return {
      before: lines.slice(0, index).join("\n").trim(),
      headers,
      rows,
      after: lines.slice(end).join("\n").trim(),
    };
  }
  return null;
}

function getNumberedItems(answer) {
  return answer.split(/\r?\n/).map((line) => {
    const match = line.match(/^\s*\d+[.)]\s+(.+)$/);
    return match ? match[1].trim() : null;
  }).filter(Boolean);
}

function renderParagraphs(text, className = "answer-copy") {
  if (!text) return null;
  return <div className={className}>{text.split(/\n+/).map((paragraph, index) => <p key={`${index}-${paragraph}`}>{paragraph}</p>)}</div>;
}

function MarkdownTable({ table }) {
  return <div className="answer-table-wrap"><table className="answer-table"><thead><tr>{table.headers.map((header, index) => <th key={`${header}-${index}`}>{header}</th>)}</tr></thead><tbody>{table.rows.map((row, rowIndex) => <tr key={`row-${rowIndex}`}>{table.headers.map((_, cellIndex) => <td key={`cell-${rowIndex}-${cellIndex}`}>{row[cellIndex] || ""}</td>)}</tr>)}</tbody></table></div>;
}

function AnswerContent({ answer }) {
  if (!answer) return <p className="muted-copy">No answer was returned for this question.</p>;
  const table = parseMarkdownTable(answer);
  if (table) return <div className="answer-content">{renderParagraphs(table.before)}<MarkdownTable table={table} />{renderParagraphs(table.after)}</div>;
  const numberedItems = getNumberedItems(answer);
  if (numberedItems.length > 1) return <ol className="answer-points">{numberedItems.map((item, index) => <li key={`${index}-${item}`}>{item}</li>)}</ol>;
  return renderParagraphs(answer);
}

function ExtractedInformation({ information }) {
  if (!information || typeof information !== "object" || Array.isArray(information)) return null;
  const entries = Object.entries(information);
  if (!entries.length) return null;
  return <article className="info-card panel"><div className="card-label"><span className="answer-symbol">+</span><span>Extracted information</span></div><div className="information-grid">{entries.map(([key, value]) => <div className="information-item" key={key}><span>{displayLabel(key)}</span>{renderValue(value)}</div>)}</div></article>;
}

function MissingInformation({ items }) {
  if (!Array.isArray(items) || !items.length) return null;
  return <article className="missing-card panel"><div className="card-label"><span className="answer-symbol">?</span><span>Information not found in document</span></div><ul>{items.map((item, index) => <li key={`${item}-${index}`}>{item}</li>)}</ul></article>;
}

function Sources({ sources }) {
  return <aside className="sources-card panel"><div className="card-label"><span className="answer-symbol">#</span><span>Sources</span></div><p className="source-intro">This answer was informed by these document pages.</p>{Array.isArray(sources) && sources.length ? <div className="source-list">{sources.map((source, index) => <div className="source-item" key={`${source.file_name}-${source.page_number}-${index}`}><span className="page-number">{source.page_number}</span><div><strong>{source.file_name}</strong><span>Page {source.page_number}</span></div></div>)}</div> : <p className="muted-copy">No page references were returned.</p>}</aside>;
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
        {!loading && result && document && <section className="results-area"><div className="results-header"><div><p className="eyebrow">Document insight</p><h2>{mode === "comparison" ? "A closer comparison" : mode === "summary" ? "Document summary" : "Here is what I found"}</h2></div><span className="grounded-badge"><span className="status-dot" /> Grounded response</span></div><div className="results-grid"><div className="answer-column"><article className="answer-card panel"><div className="card-label"><span className="answer-symbol">A</span><span>Answer</span></div><AnswerContent answer={document.answer} /></article><ExtractedInformation information={document.extracted_information} /><MissingInformation items={document.missing_information} /></div><Sources sources={document.sources} /></div></section>}
      </main>
      <footer className="footer"><span>FDE Document Intelligence</span><span>Answers stay grounded in your source material</span></footer>
    </div>
  );
}

export default App;