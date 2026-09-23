const API_BASE_URL = "http://127.0.0.1:8000";

async function apiRequest(endpoint, options = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || `API request failed: ${response.status}`
    );
  }

  return data;
}


// --------------------------------------------------
// Jobs
// --------------------------------------------------

export async function getJobs() {
  return apiRequest("/jobs/");
}


export async function getJob(jobId) {
  return apiRequest(`/jobs/${jobId}`);
}


export async function searchJobs({
  title = "Java Developer",
  location = "Hyderabad",
  maxPages = 1,
  resultsPerPage = 10,
} = {}) {
  return apiRequest("/jobs/search", {
    method: "POST",
    body: JSON.stringify({
      title,
      location,
      max_pages: maxPages,
      results_per_page: resultsPerPage,
    }),
  });
}


export async function discoverJobs({
  title = "Java Developer",
  location = "Hyderabad",
  maxPages = 1,
  resultsPerPage = 10,
} = {}) {
  return apiRequest("/jobs/discover", {
    method: "POST",
    body: JSON.stringify({
      title,
      location,
      max_pages: maxPages,
      results_per_page: resultsPerPage,
    }),
  });
}


// --------------------------------------------------
// Applications
// --------------------------------------------------

export async function getApplications() {
  return apiRequest("/jobs/applications/");
}


export async function getApplication(applicationId) {
  return apiRequest(`/jobs/applications/${applicationId}`);
}


// --------------------------------------------------
// Health
// --------------------------------------------------

export async function getHealth() {
  return apiRequest("/health");
}


const api = {
  getJobs,
  getJob,
  searchJobs,
  discoverJobs,
  getApplications,
  getApplication,
  getHealth,
};

export default api;