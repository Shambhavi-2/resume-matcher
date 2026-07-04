import { useState, useRef } from "react";

export default function UploadForm({ onUpload, uploading }) {
  const [dragging, setDragging] = useState(false);
  const [filename, setFilename] = useState(null);
  const inputRef = useRef(null);

  function handleFile(file) {
    if (!file) return;
    setFilename(file.name);
    onUpload(file);
  }

  return (
    <div
      className={`dropzone ${dragging ? "dragging" : ""}`}
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        handleFile(e.dataTransfer.files[0]);
      }}
      onClick={() => inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx,.txt"
        hidden
        onChange={(e) => handleFile(e.target.files[0])}
      />
      {uploading ? (
        <p>Reading resume…</p>
      ) : filename ? (
        <p>
          Uploaded: <span className="filename">{filename}</span>
        </p>
      ) : (
        <p>Drop a PDF, DOCX, or TXT resume here, or click to browse.</p>
      )}
    </div>
  );
}
