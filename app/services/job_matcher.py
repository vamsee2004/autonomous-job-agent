def calculate_match(candidate_skills, job_skills):
    """
    Compare candidate skills with skills required by a job.
    """

    # Convert everything to lowercase for comparison
    candidate_skills = {
        skill.lower().strip()
        for skill in candidate_skills
    }

    job_skills = {
        skill.lower().strip()
        for skill in job_skills
    }

    # If the job has no detected skills
    if not job_skills:
        return {
            "score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "message": "No job skills detected"
        }

    # Skills available in both candidate and job
    matched_skills = candidate_skills.intersection(
        job_skills
    )

    # Skills required by job but not found in candidate
    missing_skills = job_skills.difference(
        candidate_skills
    )

    # Calculate percentage
    score = round(
        (len(matched_skills) / len(job_skills)) * 100,
        2
    )

    return {
        "score": score,
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills)
    }