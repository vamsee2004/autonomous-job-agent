import { useEffect, useState } from "react";

import Jobs from "./Jobs";

import {
  getJobs,
  getApplications,
  discoverJobs,
} from "./services/api";


function App() {
  const [currentPage, setCurrentPage] = useState("dashboard");

  const [jobs, setJobs] = useState([]);
  const [applications, setApplications] = useState([]);

  const [loading, setLoading] = useState(true);
  const [discovering, setDiscovering] = useState(false);

  const [resumeView, setResumeView] = useState("dashboard");
  const [selectedResumeVersion, setSelectedResumeVersion] =
    useState(null);

  const [outreachView, setOutreachView] =
    useState("dashboard");

  const [selectedTemplate, setSelectedTemplate] =
    useState(null);


  /* ======================================================
     LOAD DASHBOARD DATA
     ====================================================== */

  async function loadDashboardData() {
    try {
      setLoading(true);

      const [jobsResponse, applicationsResponse] =
        await Promise.all([
          getJobs(),
          getApplications(),
        ]);

      setJobs(jobsResponse.jobs || []);
      setApplications(
        applicationsResponse.applications || []
      );
    } catch (error) {
      console.error(
        "Unable to load dashboard data:",
        error
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    loadDashboardData();
  }, []);


  /* ======================================================
     DISCOVER JOBS
     ====================================================== */

  async function handleDiscoverJobs() {
    try {
      setDiscovering(true);

      await discoverJobs({
        title: "Java Developer",
        location: "Hyderabad",
        maxPages: 1,
        resultsPerPage: 10,
      });

      await loadDashboardData();
    } catch (error) {
      console.error(
        "Unable to discover jobs:",
        error
      );
    } finally {
      setDiscovering(false);
    }
  }


  /* ======================================================
     NAVIGATION
     ====================================================== */

  function navigateTo(page) {
    setCurrentPage(page);

    if (page === "resume") {
      setResumeView("dashboard");
    }

    if (page === "outreach") {
      setOutreachView("dashboard");
    }
  }


  /* ======================================================
     CALCULATED DASHBOARD VALUES
     ====================================================== */

  const totalJobs = jobs.length;

  const totalApplications =
    applications.length;

  const submittedApplications =
    applications.filter(
      (application) =>
        application.status === "SUBMITTED"
    ).length;

  const approvedApplications =
    applications.filter(
      (application) =>
        application.status === "APPROVED"
    ).length;

  const pendingApplications =
    applications.filter(
      (application) =>
        application.status ===
        "PENDING_APPROVAL"
    ).length;

  const averageMatch =
    jobs.length > 0
      ? Math.round(
          jobs.reduce(
            (sum, job) =>
              sum +
              Number(job.match_score || 0),
            0
          ) / jobs.length
        )
      : 0;


  /* ======================================================
     SIDEBAR
     ====================================================== */

  function Sidebar() {
    const navigationItems = [
      {
        id: "dashboard",
        label: "Dashboard",
        icon: "▦",
      },
      {
        id: "jobs",
        label: "Jobs",
        icon: "💼",
      },
      {
        id: "applications",
        label: "Applications",
        icon: "📄",
      },
      {
        id: "resume",
        label: "Resume",
        icon: "📝",
      },
      {
        id: "outreach",
        label: "Outreach",
        icon: "✉",
      },
      {
        id: "analytics",
        label: "Analytics",
        icon: "📊",
      },
      {
        id: "settings",
        label: "Settings",
        icon: "⚙",
      },
    ];

    return (
      <aside className="sidebar">

        <div className="sidebar-logo">
          <h2>Job Agent</h2>
          <p>Autonomous Job Automation</p>
        </div>

        <nav className="sidebar-nav">

          {navigationItems.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${
                currentPage === item.id
                  ? "active"
                  : ""
              }`}
              onClick={() =>
                navigateTo(item.id)
              }
            >
              <span className="nav-icon">
                {item.icon}
              </span>

              <span>
                {item.label}
              </span>
            </button>
          ))}

        </nav>

        <div className="sidebar-footer">
          <p>
            Autonomous Job Automation Agent
          </p>
        </div>

      </aside>
    );
  }


  /* ======================================================
     DASHBOARD
     ====================================================== */

  function Dashboard() {
    const recentJobs = jobs.slice(0, 5);

    return (
      <main className="dashboard">

        <div className="dashboard-header">

          <div>
            <h1>Dashboard</h1>

            <p>
              Monitor your automated job search,
              applications and career pipeline.
            </p>
          </div>

          <div className="dashboard-actions">

            <button
              className="secondary-button"
              onClick={loadDashboardData}
            >
              Refresh
            </button>

            <button
              className="primary-button"
              onClick={handleDiscoverJobs}
              disabled={discovering}
            >
              {discovering
                ? "Searching..."
                : "🔎 Discover Jobs"}
            </button>

          </div>

        </div>


        {/* ================= STATS ================= */}

        <div className="stats-grid">

          <div className="stat-card">

            <div className="stat-card-header">
              <span className="stat-card-title">
                Jobs Found
              </span>

              <span className="stat-card-icon">
                💼
              </span>
            </div>

            <div className="stat-card-value">
              {loading ? "—" : totalJobs}
            </div>

            <div className="stat-card-subtitle">
              Matching opportunities
            </div>

          </div>


          <div className="stat-card">

            <div className="stat-card-header">
              <span className="stat-card-title">
                Applications
              </span>

              <span className="stat-card-icon">
                📄
              </span>
            </div>

            <div className="stat-card-value">
              {loading
                ? "—"
                : totalApplications}
            </div>

            <div className="stat-card-subtitle">
              Applications tracked
            </div>

          </div>


          <div className="stat-card">

            <div className="stat-card-header">
              <span className="stat-card-title">
                Submitted
              </span>

              <span className="stat-card-icon">
                🚀
              </span>
            </div>

            <div className="stat-card-value">
              {loading
                ? "—"
                : submittedApplications}
            </div>

            <div className="stat-card-subtitle">
              Submitted applications
            </div>

          </div>


          <div className="stat-card">

            <div className="stat-card-header">
              <span className="stat-card-title">
                Average Match
              </span>

              <span className="stat-card-icon">
                🎯
              </span>
            </div>

            <div className="stat-card-value">
              {loading
                ? "—"
                : `${averageMatch}%`}
            </div>

            <div className="stat-card-subtitle">
              Job profile compatibility
            </div>

          </div>

        </div>


        {/* ================= DASHBOARD GRID ================= */}

        <div className="dashboard-grid">

          {/* Recent Jobs */}

          <section className="dashboard-card">

            <div className="dashboard-card-header">

              <h2>
                Recent Job Opportunities
              </h2>

              <button
                className="small-button"
                onClick={() =>
                  navigateTo("jobs")
                }
              >
                View All
              </button>

            </div>


            {loading ? (

              <div className="loading-state">
                Loading jobs...
              </div>

            ) : recentJobs.length === 0 ? (

              <div className="empty-state">
                No jobs found.
              </div>

            ) : (

              <table className="jobs-table">

                <thead>
                  <tr>
                    <th>Job</th>
                    <th>Company</th>
                    <th>Match</th>
                    <th>Status</th>
                  </tr>
                </thead>

                <tbody>

                  {recentJobs.map((job) => (

                    <tr key={job.id}>

                      <td className="job-title-cell">
                        {job.title ||
                          "Untitled Job"}
                      </td>

                      <td>
                        {job.company ||
                          "Unknown"}
                      </td>

                      <td className="match-score">
                        {job.match_score ?? 0}%
                      </td>

                      <td>

                        <span className="status-badge status-ready">
                          {job.status ||
                            "DISCOVERED"}
                        </span>

                      </td>

                    </tr>

                  ))}

                </tbody>

              </table>

            )}

          </section>


          {/* Pipeline */}

          <section className="dashboard-card">

            <div className="dashboard-card-header">
              <h2>
                Application Pipeline
              </h2>
            </div>


            <div className="pipeline-list">

              <div className="pipeline-row">

                <span className="pipeline-label">
                  Pending
                </span>

                <div className="pipeline-bar">
                  <div
                    className="pipeline-fill"
                    style={{
                      width: `${Math.min(
                        pendingApplications *
                          10,
                        100
                      )}%`,
                    }}
                  />
                </div>

                <span className="pipeline-count">
                  {pendingApplications}
                </span>

              </div>


              <div className="pipeline-row">

                <span className="pipeline-label">
                  Approved
                </span>

                <div className="pipeline-bar">
                  <div
                    className="pipeline-fill"
                    style={{
                      width: `${Math.min(
                        approvedApplications *
                          10,
                        100
                      )}%`,
                    }}
                  />
                </div>

                <span className="pipeline-count">
                  {approvedApplications}
                </span>

              </div>


              <div className="pipeline-row">

                <span className="pipeline-label">
                  Submitted
                </span>

                <div className="pipeline-bar">
                  <div
                    className="pipeline-fill"
                    style={{
                      width: `${Math.min(
                        submittedApplications *
                          10,
                        100
                      )}%`,
                    }}
                  />
                </div>

                <span className="pipeline-count">
                  {submittedApplications}
                </span>

              </div>

            </div>

          </section>

        </div>


        {/* ================= AUTOMATION ================= */}

        <section
          className="dashboard-card"
          style={{ marginTop: "18px" }}
        >

          <div className="dashboard-card-header">

            <h2>
              Automation Status
            </h2>

            <span>
              Active
            </span>

          </div>


          <div className="automation-list">

            <div className="automation-item">

              <div className="automation-info">

                <span className="automation-icon">
                  🔎
                </span>

                <div>
                  <strong>
                    Job Discovery
                  </strong>

                  <span>
                    Searching for matching
                    opportunities
                  </span>
                </div>

              </div>

              <span className="automation-status">
                Active
              </span>

            </div>


            <div className="automation-item">

              <div className="automation-info">

                <span className="automation-icon">
                  🎯
                </span>

                <div>
                  <strong>
                    Job Matching
                  </strong>

                  <span>
                    Evaluating profile
                    compatibility
                  </span>
                </div>

              </div>

              <span className="automation-status">
                Active
              </span>

            </div>


            <div className="automation-item">

              <div className="automation-info">

                <span className="automation-icon">
                  📊
                </span>

                <div>
                  <strong>
                    Analytics
                  </strong>

                  <span>
                    Tracking application
                    performance
                  </span>
                </div>

              </div>

              <span className="automation-status">
                Active
              </span>

            </div>

          </div>

        </section>


        {/* ================= QUICK ACTIONS ================= */}

        <section
          className="dashboard-card"
          style={{ marginTop: "18px" }}
        >

          <div className="dashboard-card-header">
            <h2>
              Quick Actions
            </h2>
          </div>


          <div className="quick-actions">

            <button
              className="quick-action"
              onClick={() =>
                navigateTo("jobs")
              }
            >
              <span className="quick-action-icon">
                💼
              </span>

              Browse Jobs
            </button>


            <button
              className="quick-action"
              onClick={() =>
                navigateTo(
                  "applications"
                )
              }
            >
              <span className="quick-action-icon">
                📄
              </span>

              View Applications
            </button>


            <button
              className="quick-action"
              onClick={() =>
                navigateTo("resume")
              }
            >
              <span className="quick-action-icon">
                📝
              </span>

              Manage Resume
            </button>


            <button
              className="quick-action"
              onClick={() =>
                navigateTo("outreach")
              }
            >
              <span className="quick-action-icon">
                ✉
              </span>

              Recruiter Outreach
            </button>

          </div>

        </section>

      </main>
    );
  }


  /* ======================================================
     APPLICATIONS PAGE
     ====================================================== */

  function ApplicationsPage() {
    return (
      <main className="applications-page">

        <div className="applications-header">

          <div>
            <h1>
              Applications
            </h1>

            <p>
              Track and manage your
              application pipeline.
            </p>
          </div>

          <button
            className="secondary-button"
            onClick={loadDashboardData}
          >
            Refresh
          </button>

        </div>


        <div className="applications-card">

          {loading ? (

            <div className="loading-state">
              Loading applications...
            </div>

          ) : applications.length === 0 ? (

            <div className="empty-state">
              No applications found.
            </div>

          ) : (

            applications.map(
              (application) => (

                <div
                  className="application-row"
                  key={application.id}
                >

                  <div className="application-main">

                    <h3>
                      {application.job_title ||
                        application.title ||
                        `Application #${application.id}`}
                    </h3>

                    <p>
                      {application.company ||
                        "Company not specified"}
                    </p>

                  </div>


                  <span
                    className={`status-badge ${
                      application.status ===
                      "SUBMITTED"
                        ? "status-submitted"
                        : application.status ===
                          "APPROVED"
                        ? "status-approved"
                        : application.status ===
                          "REJECTED"
                        ? "status-rejected"
                        : "status-pending"
                    }`}
                  >
                    {application.status ||
                      "PENDING_APPROVAL"}
                  </span>


                  <span className="application-date">
                    {application.created_at
                      ? new Date(
                          application.created_at
                        ).toLocaleDateString()
                      : ""}
                  </span>

                </div>

              )
            )

          )}

        </div>

      </main>
    );
  }


  /* ======================================================
     RESUME DASHBOARD
     ====================================================== */

  function ResumeDashboard() {
    return (
      <main className="resume-page">

        <div className="resume-header">

          <div>
            <h1>
              Resume
            </h1>

            <p>
              Manage, customize and review
              your resume versions.
            </p>
          </div>

        </div>


        <div className="resume-dashboard-grid">

          <section className="resume-card">

            <div className="resume-card-header">

              <h2>
                Current Resume
              </h2>

              <span>
                Active Version
              </span>

            </div>


            <div className="resume-preview">

              <div className="resume-preview-header">

                <h2>
                  Java Full Stack Developer
                </h2>

                <p>
                  Hyderabad, India
                </p>

              </div>


              <div className="resume-preview-section">

                <h3>
                  Professional Summary
                </h3>

                <p>
                  B.Tech graduate with
                  knowledge of Java,
                  Spring Boot, React,
                  SQL and web application
                  development.
                </p>

              </div>


              <div className="resume-preview-section">

                <h3>
                  Skills
                </h3>

                <p>
                  Java · Spring Boot ·
                  React · JavaScript ·
                  SQL · MongoDB
                </p>

              </div>


              <div className="resume-preview-section">

                <h3>
                  Projects
                </h3>

                <p>
                  Java and full-stack
                  development projects
                  demonstrating backend,
                  frontend and database
                  skills.
                </p>

              </div>

            </div>

          </section>


          <section className="resume-card">

            <div className="resume-card-header">

              <h2>
                Resume Actions
              </h2>

            </div>


            <div className="resume-action-list">

              <button
                className="resume-action"
                onClick={() =>
                  setResumeView("view")
                }
              >

                <span className="resume-action-icon">
                  👁
                </span>

                <div>
                  <strong>
                    View Resume
                  </strong>

                  <span>
                    Review your current resume
                  </span>
                </div>

              </button>


              <button
                className="resume-action"
                onClick={() =>
                  setResumeView(
                    "customize"
                  )
                }
              >

                <span className="resume-action-icon">
                  ✏
                </span>

                <div>
                  <strong>
                    Customize Resume
                  </strong>

                  <span>
                    Tailor your resume for
                    a target role
                  </span>
                </div>

              </button>


              <button
                className="resume-action"
                onClick={() =>
                  setResumeView(
                    "versions"
                  )
                }
              >

                <span className="resume-action-icon">
                  🗂
                </span>

                <div>
                  <strong>
                    View Versions
                  </strong>

                  <span>
                    Review saved resume
                    versions
                  </span>
                </div>

              </button>

            </div>

          </section>

        </div>

      </main>
    );
  }


  /* ======================================================
     RESUME VIEW
     ====================================================== */

  function ResumeView() {
    return (
      <main className="resume-view-page">

        <div className="resume-inner-header">

          <div>
            <h2>
              Resume Preview
            </h2>

            <p>
              Current resume version
            </p>
          </div>

          <button
            className="secondary-button"
            onClick={() =>
              setResumeView("dashboard")
            }
          >
            ← Back
          </button>

        </div>


        <div className="resume-document">

          <div className="resume-document-header">

            <h1>
              Java Full Stack Developer
            </h1>

            <p>
              B.Tech Graduate
            </p>

            <div className="resume-document-contact">
              <span>
                Hyderabad, India
              </span>

              <span>
                Java Developer
              </span>

              <span>
                Full Stack Development
              </span>
            </div>

          </div>


          <div className="resume-document-section">

            <h3>
              Professional Summary
            </h3>

            <p>
              Motivated B.Tech graduate
              seeking an entry-level
              Java Developer or Full
              Stack Developer opportunity.
              Skilled in Java, object-oriented
              programming, web technologies,
              databases and modern
              development frameworks.
            </p>

          </div>


          <div className="resume-document-section">

            <h3>
              Technical Skills
            </h3>

            <div className="resume-skills">

              <span>Java</span>
              <span>Spring Boot</span>
              <span>JavaScript</span>
              <span>React</span>
              <span>HTML</span>
              <span>CSS</span>
              <span>SQL</span>
              <span>MongoDB</span>
              <span>Git</span>
              <span>REST APIs</span>

            </div>

          </div>


          <div className="resume-document-section">

            <h3>
              Projects
            </h3>


            <div className="resume-project">

              <strong>
                MERN Health & Fitness App
              </strong>

              <p>
                Developed a web application
                for user registration and
                health and BMI tracking.
              </p>

            </div>


            <div className="resume-project">

              <strong>
                Online Shopping Portal
              </strong>

              <p>
                Developed a Django-based
                shopping application with
                payment integration.
              </p>

            </div>


            <div className="resume-project">

              <strong>
                Tic Tac Toe
              </strong>

              <p>
                Built a responsive browser
                game using HTML, CSS and
                JavaScript.
              </p>

            </div>

          </div>


          <div className="resume-document-actions">

            <button
              className="secondary-button"
              onClick={() =>
                setResumeView(
                  "customize"
                )
              }
            >
              Customize This Resume
            </button>

            <button
              className="primary-button"
              onClick={() =>
                setResumeView(
                  "versions"
                )
              }
            >
              View Versions
            </button>

          </div>

        </div>

      </main>
    );
  }


  /* ======================================================
     RESUME CUSTOMIZE
     ====================================================== */

  function ResumeCustomize() {

    const [targetRole, setTargetRole] =
      useState("Java Developer");

    const [targetLocation, setTargetLocation] =
      useState("Hyderabad");

    const [resumeFocus, setResumeFocus] =
      useState(
        "Focus on Java, Spring Boot, REST APIs, SQL and full-stack development."
      );


    function generateResumeVersion() {
      setSelectedResumeVersion({
        title:
          targetRole ||
          "Customized Resume",
        location:
          targetLocation ||
          "India",
        focus:
          resumeFocus,
        date:
          new Date().toLocaleDateString(),
      });

      setResumeView("versions");
    }


    return (
      <main className="resume-customize-page">

        <div className="resume-inner-header">

          <div>
            <h2>
              Customize Resume
            </h2>

            <p>
              Define the target role and
              resume focus.
            </p>
          </div>

          <button
            className="secondary-button"
            onClick={() =>
              setResumeView("dashboard")
            }
          >
            ← Back
          </button>

        </div>


        <div className="customize-card">

          <div className="customize-field">

            <label>
              Target Role
            </label>

            <select
              className="resume-input"
              value={targetRole}
              onChange={(event) =>
                setTargetRole(
                  event.target.value
                )
              }
            >

              <option>
                Java Developer
              </option>

              <option>
                Java Full Stack Developer
              </option>

              <option>
                Software Engineer
              </option>

              <option>
                Full Stack Developer
              </option>

              <option>
                Web Developer
              </option>

            </select>

          </div>


          <div className="customize-field">

            <label>
              Target Location
            </label>

            <input
              className="resume-input"
              value={targetLocation}
              onChange={(event) =>
                setTargetLocation(
                  event.target.value
                )
              }
              placeholder="Enter target location"
            />

          </div>


          <div className="customize-field">

            <label>
              Resume Focus
            </label>

            <textarea
              className="resume-textarea"
              value={resumeFocus}
              onChange={(event) =>
                setResumeFocus(
                  event.target.value
                )
              }
              placeholder="Describe what you want the resume to emphasize..."
            />

          </div>


          <div className="customize-actions">

            <button
              className="secondary-button"
              onClick={() =>
                setResumeView(
                  "dashboard"
                )
              }
            >
              Cancel
            </button>

            <button
              className="primary-button"
              onClick={
                generateResumeVersion
              }
            >
              Generate Resume Version
            </button>

          </div>

        </div>

      </main>
    );
  }


  /* ======================================================
     RESUME VERSIONS
     ====================================================== */

  function ResumeVersions() {

    const versions = [
      {
        id: 1,
        title:
          "Java Developer Resume",
        description:
          "Focused on Java, Spring Boot and backend development.",
        date:
          "Current",
      },
      {
        id: 2,
        title:
          "Java Full Stack Resume",
        description:
          "Focused on Java, React, SQL and full-stack development.",
        date:
          "Previous Version",
      },
    ];


    if (selectedResumeVersion) {
      versions.unshift({
        id: 3,
        title:
          selectedResumeVersion.title,
        description:
          selectedResumeVersion.focus,
        date:
          selectedResumeVersion.date,
      });
    }


    return (
      <main className="resume-versions-page">

        <div className="resume-inner-header">

          <div>
            <h2>
              Resume Versions
            </h2>

            <p>
              Review your resume versions.
            </p>
          </div>

          <button
            className="secondary-button"
            onClick={() =>
              setResumeView(
                "dashboard"
              )
            }
          >
            ← Back
          </button>

        </div>


        <div className="version-list">

          {versions.map((version) => (

            <div
              className={`version-card ${
                selectedResumeVersion &&
                version.id === 3
                  ? "selected-version"
                  : ""
              }`}
              key={version.id}
            >

              <div className="version-icon">
                📄
              </div>


              <div className="version-info">

                <strong>
                  {version.title}
                </strong>

                <span>
                  {version.description}
                </span>

                <span>
                  {version.date}
                </span>

              </div>


              <div className="version-actions">

                <button
                  className="small-button"
                  onClick={() => {
                    setSelectedResumeVersion(
                      version
                    );

                    setResumeView(
                      "view"
                    );
                  }}
                >
                  View
                </button>

              </div>

            </div>

          ))}

        </div>

      </main>
    );
  }


  /* ======================================================
     RESUME PAGE ROUTER
     ====================================================== */

  function ResumePage() {

    if (resumeView === "view") {
      return <ResumeView />;
    }

    if (resumeView === "customize") {
      return <ResumeCustomize />;
    }

    if (resumeView === "versions") {
      return <ResumeVersions />;
    }

    return <ResumeDashboard />;
  }


  /* ======================================================
     OUTREACH DASHBOARD
     ====================================================== */

  function OutreachDashboard() {
    return (
      <main className="outreach-page">

        <div className="outreach-header">

          <div>
            <h1>
              Outreach
            </h1>

            <p>
              Prepare recruiter messages,
              templates and follow-ups.
            </p>
          </div>

        </div>


        <div className="outreach-dashboard-grid">

          <div className="outreach-stat">

            <div className="outreach-stat-label">
              Messages Prepared
            </div>

            <div className="outreach-stat-value">
              0
            </div>

          </div>


          <div className="outreach-stat">

            <div className="outreach-stat-label">
              Follow-ups
            </div>

            <div className="outreach-stat-value">
              0
            </div>

          </div>


          <div className="outreach-stat">

            <div className="outreach-stat-label">
              Scheduled
            </div>

            <div className="outreach-stat-value">
              0
            </div>

          </div>

        </div>


        <div className="outreach-options">

          <button
            className="outreach-option"
            onClick={() =>
              setOutreachView(
                "compose"
              )
            }
          >

            <div className="outreach-option-icon">
              ✉
            </div>

            <h3>
              Create Message
            </h3>

            <p>
              Prepare a personalized
              recruiter message.
            </p>

          </button>


          <button
            className="outreach-option"
            onClick={() =>
              setOutreachView(
                "templates"
              )
            }
          >

            <div className="outreach-option-icon">
              📝
            </div>

            <h3>
              View Templates
            </h3>

            <p>
              Use predefined outreach
              templates.
            </p>

          </button>


          <button
            className="outreach-option"
            onClick={() =>
              setOutreachView(
                "followups"
              )
            }
          >

            <div className="outreach-option-icon">
              🔔
            </div>

            <h3>
              View Follow-ups
            </h3>

            <p>
              Manage recruiter follow-ups.
            </p>

          </button>


          <button
            className="outreach-option"
            onClick={() =>
              setOutreachView(
                "history"
              )
            }
          >

            <div className="outreach-option-icon">
              🕘
            </div>

            <h3>
              View History
            </h3>

            <p>
              Review prepared outreach
              messages.
            </p>

          </button>


          <button
            className="outreach-option"
            onClick={() =>
              setOutreachView(
                "schedule"
              )
            }
          >

            <div className="outreach-option-icon">
              📅
            </div>

            <h3>
              Schedule
            </h3>

            <p>
              Prepare a scheduled
              follow-up.
            </p>

          </button>


          <button
            className="outreach-option"
            onClick={() =>
              setOutreachView(
                "settings"
              )
            }
          >

            <div className="outreach-option-icon">
              ⚙
            </div>

            <h3>
              Settings
            </h3>

            <p>
              Configure outreach
              preferences.
            </p>

          </button>

        </div>

      </main>
    );
  }


  /* ======================================================
     OUTREACH COMPOSE
     ====================================================== */

  function OutreachCompose() {

    const [recruiterName, setRecruiterName] =
      useState("");

    const [company, setCompany] =
      useState("");

    const [jobRole, setJobRole] =
      useState("");

    const [message, setMessage] =
      useState("");


    function prepareMessage() {
      alert(
        "Outreach message prepared successfully."
      );
    }


    return (
      <main className="outreach-inner-page">

        <div className="outreach-inner-header">

          <div>
            <h2>
              Create Outreach Message
            </h2>

            <p>
              Prepare a personalized
              recruiter message.
            </p>
          </div>

          <button
            className="secondary-button"
            onClick={() =>
              setOutreachView(
                "dashboard"
              )
            }
          >
            ← Back
          </button>

        </div>


        <div className="outreach-compose-card">

          <div className="outreach-field">

            <label>
              Recruiter Name
            </label>

            <input
              className="outreach-input"
              value={recruiterName}
              onChange={(event) =>
                setRecruiterName(
                  event.target.value
                )
              }
              placeholder="Enter recruiter name"
            />

          </div>


          <div className="outreach-field">

            <label>
              Company
            </label>

            <input
              className="outreach-input"
              value={company}
              onChange={(event) =>
                setCompany(
                  event.target.value
                )
              }
              placeholder="Enter company name"
            />

          </div>


          <div className="outreach-field">

            <label>
              Job Role
            </label>

            <input
              className="outreach-input"
              value={jobRole}
              onChange={(event) =>
                setJobRole(
                  event.target.value
                )
              }
              placeholder="Java Developer"
            />

          </div>


          <div className="outreach-field">

            <label>
              Message
            </label>

            <textarea
              className="outreach-textarea"
              value={message}
              onChange={(event) =>
                setMessage(
                  event.target.value
                )
              }
              placeholder="Write your recruiter message..."
            />

          </div>


          <div className="outreach-compose-actions">

            <button
              className="secondary-button"
              onClick={() =>
                setOutreachView(
                  "templates"
                )
              }
            >
              Use Template
            </button>

            <button
              className="primary-button"
              onClick={prepareMessage}
            >
              Prepare Message
            </button>

          </div>

        </div>

      </main>
    );
  }


  /* ======================================================
     OUTREACH TEMPLATES
     ====================================================== */

  function OutreachTemplates() {

    const templates = [
      {
        id: 1,
        title:
          "Job Application",
        description:
          "Introduce yourself and express interest in a job opportunity.",
      },
      {
        id: 2,
        title:
          "Recruiter Introduction",
        description:
          "Introduce yourself to a recruiter professionally.",
      },
      {
        id: 3,
        title:
          "Follow-up Message",
        description:
          "Follow up after an application or previous conversation.",
      },
    ];


    function useTemplate(template) {
      setSelectedTemplate(
        template
      );

      setOutreachView(
        "compose"
      );
    }


    return (
      <main className="outreach-inner-page">

        <div className="outreach-inner-header">

          <div>
            <h2>
              Outreach Templates
            </h2>

            <p>
              Select a template to use.
            </p>
          </div>

          <button
            className="secondary-button"
            onClick={() =>
              setOutreachView(
                "dashboard"
              )
            }
          >
            ← Back
          </button>

        </div>


        <div className="template-list">

          {templates.map(
            (template) => (

              <div
                className={`template-card ${
                  selectedTemplate?.id ===
                  template.id
                    ? "selected-template"
                    : ""
                }`}
                key={template.id}
              >

                <div className="template-card-main">

                  <h3>
                    {template.title}
                  </h3>

                  <p>
                    {template.description}
                  </p>

                </div>


                <button
                  className="small-button"
                  onClick={() =>
                    useTemplate(
                      template
                    )
                  }
                >
                  Use Template
                </button>

              </div>

            )
          )}

        </div>

      </main>
    );
  }


  /* ======================================================
     OUTREACH FOLLOW-UPS
     ====================================================== */

  function OutreachFollowUps() {
    return (
      <main className="outreach-inner-page">

        <div className="outreach-inner-header">

          <div>
            <h2>
              Follow-ups
            </h2>

            <p>
              Manage recruiter follow-ups.
            </p>
          </div>

          <button
            className="secondary-button"
            onClick={() =>
              setOutreachView(
                "dashboard"
              )
            }
          >
            ← Back
          </button>

        </div>


        <div className="empty-outreach">

          <div className="empty-outreach-icon">
            🔔
          </div>

          <h3>
            No follow-ups scheduled
          </h3>

          <p>
            Create an outreach message
            to prepare a follow-up.
          </p>

          <button
            className="primary-button"
            onClick={() =>
              setOutreachView(
                "compose"
              )
            }
          >
            Create Outreach
          </button>

        </div>

      </main>
    );
  }


  /* ======================================================
     OUTREACH HISTORY
     ====================================================== */

  function OutreachHistory() {
    return (
      <main className="outreach-inner-page">

        <div className="outreach-inner-header">

          <div>
            <h2>
              Outreach History
            </h2>

            <p>
              Review prepared outreach
              messages.
            </p>
          </div>

          <button
            className="secondary-button"
            onClick={() =>
              setOutreachView(
                "dashboard"
              )
            }
          >
            ← Back
          </button>

        </div>


        <div className="empty-outreach">

          <div className="empty-outreach-icon">
            🕘
          </div>

          <h3>
            No outreach history
          </h3>

          <p>
            Your prepared outreach
            messages will appear here.
          </p>

          <button
            className="primary-button"
            onClick={() =>
              setOutreachView(
                "compose"
              )
            }
          >
            Create Message
          </button>

        </div>

      </main>
    );
  }


  /* ======================================================
     OUTREACH SCHEDULE
     ====================================================== */

  function OutreachSchedule() {

    const [recruiter, setRecruiter] =
      useState("");

    const [company, setCompany] =
      useState("");

    const [date, setDate] =
      useState("");

    const [time, setTime] =
      useState("");

    const [message, setMessage] =
      useState("");


    function saveSchedule() {
      alert(
        "Outreach schedule prepared successfully."
      );
    }


    return (
      <main className="outreach-inner-page">

        <div className="outreach-inner-header">

          <div>
            <h2>
              Schedule Outreach
            </h2>

            <p>
              Prepare a future follow-up.
            </p>
          </div>

          <button
            className="secondary-button"
            onClick={() =>
              setOutreachView(
                "dashboard"
              )
            }
          >
            ← Back
          </button>

        </div>


        <div className="outreach-compose-card">

          <div className="outreach-field">

            <label>
              Recruiter Name
            </label>

            <input
              className="outreach-input"
              value={recruiter}
              onChange={(event) =>
                setRecruiter(
                  event.target.value
                )
              }
              placeholder="Recruiter name"
            />

          </div>


          <div className="outreach-field">

            <label>
              Company
            </label>

            <input
              className="outreach-input"
              value={company}
              onChange={(event) =>
                setCompany(
                  event.target.value
                )
              }
              placeholder="Company name"
            />

          </div>


          <div className="outreach-field">

            <label>
              Date
            </label>

            <input
              type="date"
              className="outreach-input"
              value={date}
              onChange={(event) =>
                setDate(
                  event.target.value
                )
              }
            />

          </div>


          <div className="outreach-field">

            <label>
              Time
            </label>

            <input
              type="time"
              className="outreach-input"
              value={time}
              onChange={(event) =>
                setTime(
                  event.target.value
                )
              }
            />

          </div>


          <div className="outreach-field">

            <label>
              Message
            </label>

            <textarea
              className="outreach-textarea"
              value={message}
              onChange={(event) =>
                setMessage(
                  event.target.value
                )
              }
              placeholder="Follow-up message..."
            />

          </div>


          <div className="outreach-compose-actions">

            <button
              className="secondary-button"
              onClick={() =>
                setOutreachView(
                  "dashboard"
                )
              }
            >
              Cancel
            </button>

            <button
              className="primary-button"
              onClick={saveSchedule}
            >
              Save Schedule
            </button>

          </div>

        </div>

      </main>
    );
  }


  /* ======================================================
     OUTREACH SETTINGS
     ====================================================== */

  function OutreachSettings() {

    const [
      automaticFollowups,
      setAutomaticFollowups,
    ] = useState(true);

    const [
      personalizedMessages,
      setPersonalizedMessages,
    ] = useState(true);

    const [
      approvalBeforeSending,
      setApprovalBeforeSending,
    ] = useState(true);


    function saveSettings() {
      alert(
        "Outreach settings saved successfully."
      );
    }


    return (
      <main className="outreach-inner-page">

        <div className="outreach-inner-header">

          <div>
            <h2>
              Outreach Settings
            </h2>

            <p>
              Configure outreach preferences.
            </p>
          </div>

          <button
            className="secondary-button"
            onClick={() =>
              setOutreachView(
                "dashboard"
              )
            }
          >
            ← Back
          </button>

        </div>


        <div className="outreach-settings-card">

          <div className="outreach-setting-row">

            <div className="outreach-setting-info">

              <strong>
                Automatic Follow-ups
              </strong>

              <span>
                Enable follow-up preparation
                for applications.
              </span>

            </div>

            <input
              type="checkbox"
              checked={automaticFollowups}
              onChange={(event) =>
                setAutomaticFollowups(
                  event.target.checked
                )
              }
            />

          </div>


          <div className="outreach-setting-row">

            <div className="outreach-setting-info">

              <strong>
                Personalized Messages
              </strong>

              <span>
                Personalize messages for
                each recruiter.
              </span>

            </div>

            <input
              type="checkbox"
              checked={personalizedMessages}
              onChange={(event) =>
                setPersonalizedMessages(
                  event.target.checked
                )
              }
            />

          </div>


          <div className="outreach-setting-row">

            <div className="outreach-setting-info">

              <strong>
                Approval Before Sending
              </strong>

              <span>
                Require approval before
                outreach is sent.
              </span>

            </div>

            <input
              type="checkbox"
              checked={approvalBeforeSending}
              onChange={(event) =>
                setApprovalBeforeSending(
                  event.target.checked
                )
              }
            />

          </div>


          <div className="outreach-compose-actions">

            <button
              className="primary-button"
              onClick={saveSettings}
            >
              Save Settings
            </button>

          </div>

        </div>

      </main>
    );
  }


  /* ======================================================
     OUTREACH PAGE ROUTER
     ====================================================== */

  function OutreachPage() {

    if (outreachView === "compose") {
      return <OutreachCompose />;
    }

    if (
      outreachView ===
      "templates"
    ) {
      return <OutreachTemplates />;
    }

    if (
      outreachView ===
      "followups"
    ) {
      return <OutreachFollowUps />;
    }

    if (
      outreachView ===
      "history"
    ) {
      return <OutreachHistory />;
    }

    if (
      outreachView ===
      "schedule"
    ) {
      return <OutreachSchedule />;
    }

    if (
      outreachView ===
      "settings"
    ) {
      return <OutreachSettings />;
    }

    return <OutreachDashboard />;
  }


  /* ======================================================
     ANALYTICS
     ====================================================== */

  function AnalyticsPage() {

    const submitted =
      submittedApplications;

    const approved =
      approvedApplications;

    const pending =
      pendingApplications;


    return (
      <main className="analytics-page">

        <div className="analytics-header">

          <h1>
            Analytics
          </h1>

          <p>
            Review your job search and
            application performance.
          </p>

        </div>


        <div className="analytics-grid">

          <section className="analytics-card">

            <h2>
              Application Metrics
            </h2>


            <div className="analytics-metric">

              <span>
                Total Applications
              </span>

              <strong>
                {totalApplications}
              </strong>

            </div>


            <div className="analytics-metric">

              <span>
                Pending Approval
              </span>

              <strong>
                {pending}
              </strong>

            </div>


            <div className="analytics-metric">

              <span>
                Approved
              </span>

              <strong>
                {approved}
              </strong>

            </div>


            <div className="analytics-metric">

              <span>
                Submitted
              </span>

              <strong>
                {submitted}
              </strong>

            </div>

          </section>


          <section className="analytics-card">

            <h2>
              Job Matching
            </h2>


            <div className="analytics-metric">

              <span>
                Jobs Discovered
              </span>

              <strong>
                {totalJobs}
              </strong>

            </div>


            <div className="analytics-metric">

              <span>
                Average Match
              </span>

              <strong>
                {averageMatch}%
              </strong>

            </div>


            <div>

              <span
                style={{
                  fontSize: "11px",
                  color: "#6b7280",
                }}
              >
                Average profile compatibility
              </span>

              <div className="analytics-progress">

                <div
                  className="analytics-progress-fill"
                  style={{
                    width: `${averageMatch}%`,
                  }}
                />

              </div>

            </div>

          </section>

        </div>

      </main>
    );
  }


  /* ======================================================
     SETTINGS
     ====================================================== */

  function SettingsPage() {

    const [jobTitle, setJobTitle] =
      useState("Java Developer");

    const [location, setLocation] =
      useState("Hyderabad");

    const [maxPages, setMaxPages] =
      useState("1");


    function saveSettings() {
      alert(
        "Settings saved successfully."
      );
    }


    return (
      <main className="settings-page">

        <div className="settings-header">

          <h1>
            Settings
          </h1>

          <p>
            Configure job search preferences.
          </p>

        </div>


        <div className="settings-grid">

          <section className="settings-card">

            <h2>
              Job Search Preferences
            </h2>


            <div className="settings-field">

              <label>
                Target Job Title
              </label>

              <input
                className="settings-input"
                value={jobTitle}
                onChange={(event) =>
                  setJobTitle(
                    event.target.value
                  )
                }
              />

            </div>


            <div className="settings-field">

              <label>
                Target Location
              </label>

              <input
                className="settings-input"
                value={location}
                onChange={(event) =>
                  setLocation(
                    event.target.value
                  )
                }
              />

            </div>


            <div className="settings-field">

              <label>
                Maximum Search Pages
              </label>

              <select
                className="settings-select"
                value={maxPages}
                onChange={(event) =>
                  setMaxPages(
                    event.target.value
                  )
                }
              >

                <option value="1">
                  1
                </option>

                <option value="2">
                  2
                </option>

                <option value="3">
                  3
                </option>

                <option value="5">
                  5
                </option>

              </select>

            </div>


            <div className="settings-actions">

              <button
                className="primary-button"
                onClick={
                  saveSettings
                }
              >
                Save Settings
              </button>

            </div>

          </section>


          <section className="settings-card">

            <h2>
              System Information
            </h2>


            <div className="analytics-metric">

              <span>
                Backend
              </span>

              <strong>
                FastAPI
              </strong>

            </div>


            <div className="analytics-metric">

              <span>
                Database
              </span>

              <strong>
                SQLite
              </strong>

            </div>


            <div className="analytics-metric">

              <span>
                Job Scheduler
              </span>

              <strong>
                APScheduler
              </strong>

            </div>


            <div className="analytics-metric">

              <span>
                Application
              </span>

              <strong>
                Job Automation Agent
              </strong>

            </div>

          </section>

        </div>

      </main>
    );
  }


  /* ======================================================
     PAGE ROUTER
     ====================================================== */

  function renderPage() {

    switch (currentPage) {

      case "jobs":
        return <Jobs />;

      case "applications":
        return (
          <ApplicationsPage />
        );

      case "resume":
        return <ResumePage />;

      case "outreach":
        return <OutreachPage />;

      case "analytics":
        return (
          <AnalyticsPage />
        );

      case "settings":
        return (
          <SettingsPage />
        );

      case "dashboard":
      default:
        return <Dashboard />;
    }
  }


  /* ======================================================
     FINAL APP
     ====================================================== */

  return (
    <div className="app">

      <Sidebar />

      <div className="main-content">
        {renderPage()}
      </div>

    </div>
  );
}


export default App;