// API requests use the same server as the React frontend.
// An empty base URL means requests are sent to the current domain.

const API_BASE_URL = "";

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

// Get all saved jobs
export async function getJobs() {
  return apiRequest("/jobs/");
}

// Get a single job
export async function getJob(jobId) {
  return apiRequest(`/jobs/${jobId}`);
}

// Search jobs
export async function searchJobs(searchParams = {}) {
  return apiRequest("/jobs/search", {
    method: "POST",
    body: JSON.stringify(searchParams),
  });
}

// Discover new jobs
export async function discoverJobs(discoverParams = {}) {
  return apiRequest("/jobs/discover", {
    method: "POST",
    body: JSON.stringify(discoverParams),
  });
}

// Get all applications
export async function getApplications() {
  return apiRequest("/jobs/applications/");
}

// Get a single application
export async function getApplication(applicationId) {
  return apiRequest(`/jobs/applications/${applicationId}`);
}

// Check backend health
export async function healthCheck() {
  return apiRequest("/health");
}

// Default API object
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