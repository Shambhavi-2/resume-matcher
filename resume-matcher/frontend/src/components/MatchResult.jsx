import { useState } from "react";
import ScoreStamp from "./ScoreStamp";
import { api } from "../api";

export default function MatchResult({ match }) {
  const [feedback, setFeedback] = useState(match.feedback);

  if (match.status === "pending" || match.status === "processing") {
    return (
      <div className="panel">
        <div className="status-line">
          <span className="dot" />
          {match.status === "pending" ? "Queued…" : "Scoring resume against job requirements…"}
        </div>
      </div>
    );
  }

  if (match.status === "failed") {
    return (
      <div className="panel">
        <div className="error-box">Match failed: {match.error || "Unknown error."}</div>
      </div>
    );
  }

  async function submitFeedback(value) {
    setFeedback(value);
    try {
      await api.sendFeedback(match.id, value);
    } catch {
      // non-critical, ignore
    }
  }

  return (
    <div className="panel">
      <ScoreStamp score={match.score ?? 0} />

      <div className="two-col" style={{ marginTop: 28 }}>
        <div>
          <div className="panel-title">Strengths</div>
          {match.strengths?.length ? (
            match.strengths.map((s, i) => (
              <div key={i} className="margin-note strength">
                <span className="margin-note-label">Covered</span>
                {s}
              </div>
            ))
          ) : (
            <div className="empty-note">No strong matches found.</div>
          )}
        </div>

        <div>
          <div className="panel-title">Gaps</div>
          {match.gaps?.length ? (
            match.gaps.map((g, i) => (
              <div key={i} className="margin-note gap">
                <span className="margin-note-label">Missing</span>
                {g}
              </div>
            ))
          ) : (
            <div className="empty-note">No significant gaps found.</div>
          )}
        </div>
      </div>

      {match.suggestions?.length > 0 && (
        <div style={{ marginTop: 28 }}>
          <div className="panel-title">Suggested rewrites</div>
          {match.suggestions.map((s, i) => (
            <div key={i} className="suggestion-item">
              {s}
            </div>
          ))}
        </div>
      )}

      <div className="feedback-row">
        <span>Was this useful?</span>
        <button
          className={`chip ${feedback === "helpful" ? "selected" : ""}`}
          onClick={() => submitFeedback("helpful")}
        >
          Helpful
        </button>
        <button
          className={`chip ${feedback === "not_helpful" ? "selected" : ""}`}
          onClick={() => submitFeedback("not_helpful")}
        >
          Not helpful
        </button>
      </div>
    </div>
  );
}
