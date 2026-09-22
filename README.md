# Autonomous Job Automation Agent

An AI-powered job search and application automation system built with
Python, FastAPI, SQLAlchemy, SQLite, APScheduler, and external job-search
APIs.

## Project Overview

The Autonomous Job Automation Agent helps automate the job-search workflow:

1. Discover jobs
2. Analyze job descriptions
3. Match jobs with a candidate profile
4. Rank jobs by priority
5. Prepare application materials
6. Create applications
7. Require approval before application submission
8. Track application status
9. Generate outreach
10. Schedule follow-ups
11. Record application feedback
12. Learn from historical feedback
13. Provide application analytics
14. Run scheduled job searches automatically

## Technology Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite
- APScheduler
- Pydantic

### External Services

- Adzuna Job Search API

### Development

- PyCharm
- Uvicorn
- Git

## Project Structure

```text
autonomous-job-agent
│
├── app
│   ├── api
│   │   ├── candidate.py
│   │   ├── jobs.py
│   │   └── outreach.py
│   │
│   ├── database
│   │   └── connection.py
│   │
│   ├── knowledge
│   │   ├── candidate_profile.json
│   │   └── portal_permissions.json
│   │
│   ├── models
│   │   ├── job.py
│   │   ├── application.py
│   │   ├── pipeline_run.py
│   │   ├── application_audit.py
│   │   ├── outreach.py
│   │   └── application_feedback.py
│   │
│   ├── portals
│   │   └── ...
│   │
│   ├── resume
│   │   └── resume_generator.py
│   │
│   └── services
│       ├── jd_analyzer.py
│       ├── job_matcher.py
│       ├── job_ranker.py
│       ├── job_discovery.py
│       ├── job_search_service.py
│       ├── resume_customizer.py
│       ├── cover_letter_generator.py
│       ├── automated_job_pipeline.py
│       ├── scheduler.py
│       ├── application_limits.py
│       ├── application_state_machine.py
│       ├── portal_permissions.py
│       ├── portal_adapter_factory.py
│       ├── duplicate_detector.py
│       ├── outreach_generator.py
│       ├── outreach_scheduler.py
│       ├── application_feedback_service.py
│       ├── application_learning_service.py
│       ├── learning_ranker.py
│       ├── application_analytics_service.py
│       └── detailed_analytics_service.py
│
├── data
│   ├── jobs.db
│   ├── resumes
│   ├── cover_letters
│   └── logs
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md

 <img width="1312" height="1199" alt="architecture png" src="https://github.com/user-attachments/assets/3f222da5-7e16-4fcd-b1a3-76a2261869c6" />

