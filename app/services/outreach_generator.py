from app.models.job import Job


def generate_outreach_message(
    job: Job,
    candidate_name: str = "Candidate"
):
    """
    Generate a professional recruiter outreach message.
    """

    company = job.company or "your company"
    title = job.title or "the position"

    message = (
        f"Hello,\n\n"
        f"My name is {candidate_name}. I am interested in "
        f"the {title} opportunity at {company}.\n\n"
        f"I have a strong interest in software development "
        f"and believe my technical skills and projects "
        f"could be relevant to this position.\n\n"
        f"I would appreciate the opportunity to discuss "
        f"the role and my profile.\n\n"
        f"Thank you for your time.\n\n"
        f"Best regards,\n"
        f"{candidate_name}"
    )

    return {
        "success": True,
        "job_id": job.id,
        "company": company,
        "job_title": title,
        "message": message
    }