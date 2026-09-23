// API service for Autonomous Job Automation Agent

const API_BASE_URL = "https://autonomous-job-agent-1.onrender.com";

async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;

  const config = {
    method: options.method || "GET",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);

    const contentType = response.headers.get("content-type") || "";

    let data;

    if (contentType.includes("application/json")) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    if (!response.ok) {
      const errorMessage =
        typeof data === "object" && data?.detail
          ? data.detail
          : `API request failed: ${response.status} ${response.statusText}`;

      throw new Error(errorMessage);
    }

    return data;
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

/* =========================
   JOB APIs
   ========================= */

export async function getJobs() {
  return apiRequest("/jobs/");
}

export async function getJob(jobId) {
  return apiRequest(`/jobs/${jobId}`);
}

export async function searchJobs(searchParams = {}) {
  return apiRequest("/jobs/search", {
    method: "POST",
    body: JSON.stringify(searchParams),
  });
}

export async function discoverJobs(discoverParams = {}) {
  return apiRequest("/jobs/discover", {
    method: "POST",
    body: JSON.stringify(discoverParams),
  });
}

/* =========================
   APPLICATION APIs
   ========================= */

export async function getApplications() {
  return apiRequest("/jobs/applications/");
}

export async function getApplication(applicationId) {
  return apiRequest(`/jobs/applications/${applicationId}`);
}

/* =========================
   HEALTH CHECK
   ========================= */

export async function healthCheck() {
  return apiRequest("/health");
}

/* =========================
   DEFAULT API OBJECT
   ========================= */

const api = {
  getJobs,
  getJob,
  searchJobs,
  discoverJobs,
  getApplications,
  getApplication,
  healthCheck,
};

export default api;