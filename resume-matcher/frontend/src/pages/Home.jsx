import { Link } from "react-router-dom";
import { api } from "../api";

export default function Home() {
  return (
    <div className="page">
      <div className="container">
        <div className="masthead">
          <p className="eyebrow">Issue No. 1 — Explainable matching</p>
          <h1>Read your resume the way a hiring manager will.</h1>
          <p>
            Upload a resume and a job description. Fieldnotes finds which requirements are
            actually covered, which are missing, and drafts the specific line you should add
            to close the gap — no black-box percentage, just the evidence.
          </p>
        </div>

        <div className="two-col">
          <div className="panel">
            <div className="panel-title">01 — Upload</div>
            <p style={{ margin: 0, color: "var(--ink-soft)", fontSize: 14 }}>
              Drop in a PDF, DOCX, or plain text resume. We parse it into sections a model can
              actually reason over.
            </p>
          </div>
          <div className="panel">
            <div className="panel-title">02 — Match</div>
            <p style={{ margin: 0, color: "var(--ink-soft)", fontSize: 14 }}>
              Every job requirement is scored against the best-matching resume line, then
              explained in plain language — strengths, gaps, and rewrites.
            </p>
          </div>
        </div>

        <Link to={api.isAuthed() ? "/dashboard" : "/register"} className="btn">
          {api.isAuthed() ? "Go to dashboard" : "Get started"}
        </Link>
      </div>
    </div>
  );
}
