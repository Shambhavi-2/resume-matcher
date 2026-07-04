const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function getToken() {
  return localStorage.getItem("token");
}

async function request(path, { method = "GET", body, isForm = false } = {}) {
  const headers = {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (!isForm && body) headers["Content-Type"] = "application/json";

  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers,
    body: isForm ? body : body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      detail = data.detail || detail;
    } catch {
      // ignore parse errors
    }
    throw new Error(detail);
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  async register(email, password) {
    return request("/auth/register", { method: "POST", body: { email, password } });
  },

  async login(email, password) {
    const form = new URLSearchParams();
    form.set("username", email);
    form.set("password", password);
    const res = await fetch(`${API_URL}/auth/login`, { method: "POST", body: form });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || "Login failed");
    }
    const data = await res.json();
    localStorage.setItem("token", data.access_token);
    return data;
  },

  logout() {
    localStorage.removeItem("token");
  },

  isAuthed() {
    return !!getToken();
  },

  async listResumes() {
    return request("/resumes");
  },

  async uploadResume(file) {
    const form = new FormData();
    form.append("file", file);
    return request("/resumes/upload", { method: "POST", body: form, isForm: true });
  },

  async deleteResume(id) {
    return request(`/resumes/${id}`, { method: "DELETE" });
  },

  async listJobs() {
    return request("/jobs");
  },

  async createJob(title, raw_text) {
    return request("/jobs", { method: "POST", body: { title, raw_text } });
  },

  async deleteJob(id) {
    return request(`/jobs/${id}`, { method: "DELETE" });
  },

  async createMatch(resume_id, job_id) {
    return request("/matches", { method: "POST", body: { resume_id, job_id } });
  },

  async getMatch(id) {
    return request(`/matches/${id}`);
  },

  async listMatches() {
    return request("/matches");
  },

  async sendFeedback(id, feedback) {
    return request(`/matches/${id}/feedback`, { method: "POST", body: { feedback } });
  },
};
