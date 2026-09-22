# Autonomous Job Automation Agent

An AI-powered job discovery and application-preparation system built with Python, FastAPI, SQLAlchemy, SQLite, and APScheduler.

## Features

- Automated job discovery
- Adzuna job-search integration
- Candidate preference filtering
- Job-description skill analysis
- Candidate/job skill matching
- Match-score filtering
- Salary filtering
- Job priority ranking
- Duplicate-job detection
- Stale-job detection
- Pipeline run tracking
- Automated resume generation
- Automated cover-letter generation
- Application tracking
- Approval-required workflow
- Scheduled job searching
- Structured application logging
- Configuration validation
- FastAPI REST APIs
- Swagger API documentation

## Project Structure

```text
autonomous-job-agent
│
├── app
│   ├── api
│   ├── database
│   ├── knowledge
│   ├── models
│   ├── resume
│   ├── services
│   └── templates
│
├── data
│   ├── resumes
│   ├── cover_letters
│   ├── logs
│   └── jobs.db
│
├── .env
├── .gitignore
└── README.md