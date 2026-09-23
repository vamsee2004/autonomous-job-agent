import { useEffect, useState } from "react";

import {
  getJobs,
  discoverJobs,
} from "./services/api";


function Jobs() {

  const [jobs, setJobs] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [searching, setSearching] =
    useState(false);

  const [searchText, setSearchText] =
    useState("");

  const [error, setError] =
    useState("");


  async function loadJobs() {

    try {

      setLoading(true);
      setError("");

      const response =
        await getJobs();

      setJobs(
        response.jobs || []
      );

    } catch (err) {

      console.error(
        "Unable to load jobs:",
        err
      );

      setError(
        err.message ||
        "Unable to load jobs."
      );

    } finally {

      setLoading(false);

    }
  }


  useEffect(() => {

    loadJobs();

  }, []);


  async function handleDiscover() {

    try {

      setSearching(true);
      setError("");

      await discoverJobs({
        title: "Java Developer",
        location: "Hyderabad",
        maxPages: 1,
        resultsPerPage: 10,
      });

      await loadJobs();

    } catch (err) {

      console.error(
        "Unable to discover jobs:",
        err
      );

      setError(
        err.message ||
        "Unable to discover jobs."
      );

    } finally {

      setSearching(false);

    }
  }


  const filteredJobs =
    jobs.filter((job) => {

      const text =
        searchText
          .trim()
          .toLowerCase();

      if (!text) {
        return true;
      }

      return (

        job.title
          ?.toLowerCase()
          .includes(text)

        ||

        job.company
          ?.toLowerCase()
          .includes(text)

        ||

        job.location
          ?.toLowerCase()
          .includes(text)

      );

    });


  return (

    <main className="jobs-page">

      {/* HEADER */}

      <div className="jobs-page-header">

        <div>

          <h1>
            Jobs
          </h1>

          <p>
            Discover and manage matching
            job opportunities.
          </p>

        </div>


        <button
          className="primary-button"
          onClick={handleDiscover}
          disabled={searching}
        >

          {searching
            ? "Searching..."
            : "🔎 Discover Jobs"}

        </button>

      </div>


      {/* ERROR */}

      {error && (

        <div className="error-message">

          {error}

        </div>

      )}


      {/* SEARCH */}

      <div className="jobs-toolbar">

        <input
          type="text"
          placeholder="Search jobs, companies or locations..."
          value={searchText}
          onChange={(event) =>
            setSearchText(
              event.target.value
            )
          }
        />


        <button
          className="secondary-button"
          onClick={loadJobs}
        >
          Refresh
        </button>

      </div>


      {/* SUMMARY */}

      <div className="jobs-summary">

        Showing{" "}

        <strong>
          {filteredJobs.length}
        </strong>

        {" "}of{" "}

        <strong>
          {jobs.length}
        </strong>

        {" "}jobs

      </div>


      {/* JOB LIST */}

      {loading ? (

        <div className="jobs-empty">

          Loading jobs...

        </div>

      ) : filteredJobs.length === 0 ? (

        <div className="jobs-empty">

          No matching jobs found.

        </div>

      ) : (

        <div className="jobs-list">

          {filteredJobs.map(
            (job) => (

              <div
                className="job-card"
                key={job.id}
              >

                <div className="job-card-main">

                  <h2>

                    {job.title ||
                      "Untitled Job"}

                  </h2>


                  <h3>

                    {job.company ||
                      "Unknown Company"}

                  </h3>


                  <p>

                    📍{" "}

                    {job.location ||
                      "Location not specified"}

                  </p>


                  <span className="job-source">

                    Source:{" "}

                    {job.source ||
                      "Unknown"}

                  </span>

                </div>


                <div className="job-card-score">

                  <strong>

                    {job.match_score ??
                      0}%

                  </strong>

                  <span>
                    Match
                  </span>

                </div>


                <div className="job-card-action">

                  {job.url && (

                    <a
                      href={job.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="job-link"
                    >
                      View Job
                    </a>

                  )}

                </div>

              </div>

            )
          )}

        </div>

      )}

    </main>

  );
}


export default Jobs;