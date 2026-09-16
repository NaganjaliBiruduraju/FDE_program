import { useState } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    setFile(selectedFile || null);
    setResult(null);
    setError("");
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a PDF file.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/extract",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Document extraction failed."
        );
      }

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>FDE Document Extraction</h1>

      <p>
        Upload a PDF to extract structured document information.
      </p>

      <input
        type="file"
        accept=".pdf"
        onChange={handleFileChange}
      />

      {file && (
        <p>
          Selected file: <strong>{file.name}</strong>
        </p>
      )}

      <button
        onClick={handleUpload}
        disabled={!file || loading}
      >
        {loading ? "Processing..." : "Extract Document"}
      </button>

      {error && (
        <p>
          <strong>Error:</strong> {error}
        </p>
      )}

      {result && (
        <div>
          <h2>Extraction Result</h2>

          <h3>Metadata</h3>
          <pre>
            {JSON.stringify(result.document.metadata, null, 2)}
          </pre>

          <h3>Content</h3>
          <pre>
            {JSON.stringify(result.document.content, null, 2)}
          </pre>

          <h3>Evaluation</h3>
          <pre>
            {JSON.stringify(result.evaluation, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

export default App;