import { useEffect, useState, useRef } from "react";
import { api } from "../api";
import UploadForm from "../components/UploadForm";
import MatchResult from "../components/MatchResult";

export default function Dashboard() {
  const [resumes, setResumes] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [selectedResume, setSelectedResume] = useState(null);
  const [selectedJob, setSelectedJob] = useState(null);
  const [uploading, setUploading] = useState(false);

  const [jobTitle, setJobTitle] = useState("");
  const [jobText, setJobText] = useState("");
  const [creatingJob, setCreatingJob] = useState(false);

  const [match, setMatch] = useState(null);
  const [matching, setMatching] = useState(false);
  const [error, setError] = useState(null);
  const pollRef = useRef(null);

  useEffect(() => {
    refreshResumes();
    refreshJobs();
    return () => clearInterval(pollRef.current);
  }, []);

  async function refreshResumes() {
    try {
      setResumes(await api.listResumes());
    } catch (err) {
      setError(err.message);
    }
  }

  async function refreshJobs() {
    try {
      setJobs(await api.listJobs());
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleUpload(file) {
    setUploading(true);
    setError(null);
    try {
      const resume = await api.uploadResume(file);
      setResumes((prev) => [resume, ...prev]);
      setSelectedResume(resume.id);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  async function handleDeleteResume(id) {
    try {
      await api.deleteResume(id);
      setResumes((prev) => prev.filter((r) => r.id !== id));
      if (selectedResume === id) setSelectedResume(null);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleCreateJob(e) {
    e.preventDefault();
    setCreatingJob(true);
    setError(null);
    try {
      const job = await api.createJob(jobTitle, jobText);
      setJobs((prev) => [job, ...prev]);
      setSelectedJob(job.id);
      setJobTitle("");
      setJobText("");
    } catch (err) {
      setError(err.message);
    } finally {
      setCreatingJob(false);
    }
  }

  async function handleDeleteJob(id) {
    try {
      await api.deleteJob(id);
      setJobs((prev) => prev.filter((j) => j.id !== id));
      if (selectedJob === id) setSelectedJob(null);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleRunMatch() {
    if (!selectedResume || !selectedJob) return;
    setMatching(true);
    setError(null);
    setMatch(null);
    try {
      const created = await api.createMatch(selectedResume, selectedJob);
      setMatch(created);
      pollRef.current = setInterval(async () => {
        const updated = await api.getMatch(created.id);
        setMatch(updated);
        if (updated.status === "done" || updated.status === "failed") {
          clearInterval(pollRef.current);
          setMatching(false);
        }
      }, 1800);
    } catch (err) {
      setError(err.message);
      setMatching(false);
    }
  }

  return (
    <div className="page">
      <div className="container">
        <div className="masthead">
          <p className="eyebrow">Workspace</p>
          <h1>Line up a resume against a role</h1>
          <p>Select or upload a resume, paste in a job description, then run the match.</p>
        </div>

        {error && <div className="error-box">{error}</div>}

        <div className="two-col">
          <div className="panel">
            <div className="panel-title">Resume</div>
            <UploadForm onUpload={handleUpload} uploading={uploading} />

            {resumes.length > 0 ? (
              <ul className="select-list">
                {resumes.map((r) => (
                  <li
                    key={r.id}
                    className={selectedResume === r.id ? "active" : ""}
                    onClick={() => setSelectedResume(r.id)}
                  >
                    <span>{r.filename}</span>
                    <span className="meta">
                      {new Date(r.created_at).toLocaleDateString()}
                      <button
                        className="chip"
                        style={{ marginLeft: 10 }}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteResume(r.id);
                        }}
                      >
                        remove
                      </button>
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="empty-note">No resumes uploaded yet.</div>
            )}
          </div>

          <div className="panel">
            <div className="panel-title">Job description</div>
            <form onSubmit={handleCreateJob}>
              <label htmlFor="jobTitle">Role title</label>
              <input
                id="jobTitle"
                type="text"
                required
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder="e.g. Senior Backend Engineer"
              />
              <label htmlFor="jobText">Paste the full job description</label>
              <textarea
                id="jobText"
                required
                value={jobText}
                onChange={(e) => setJobText(e.target.value)}
                placeholder="Requirements, responsibilities, qualifications…"
              />
              <button className="btn btn-outline" type="submit" disabled={creatingJob}>
                {creatingJob ? "Saving…" : "Save job description"}
              </button>
            </form>

            {jobs.length > 0 && (
              <ul className="select-list" style={{ marginTop: 18 }}>
                {jobs.map((j) => (
                  <li
                    key={j.id}
                    className={selectedJob === j.id ? "active" : ""}
                    onClick={() => setSelectedJob(j.id)}
                  >
                    <span>{j.title}</span>
                    <span className="meta">
                      {new Date(j.created_at).toLocaleDateString()}
                      <button
                        className="chip"
                        style={{ marginLeft: 10 }}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteJob(j.id);
                        }}
                      >
                        remove
                      </button>
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        <button
          className="btn"
          disabled={!selectedResume || !selectedJob || matching}
          onClick={handleRunMatch}
        >
          {matching ? "Matching…" : "Run match"}
        </button>

        {match && (
          <div style={{ marginTop: 32 }}>
            <MatchResult match={match} />
          </div>
        )}
      </div>
    </div>
  );
}
