from app.services.jd_analyzer import analyze_job_description
from app.services.job_matcher import calculate_match


def customize_resume_data(
    candidate,
    job_description
):
    """
    Create job-specific resume data.

    Only information already present in the
    candidate profile is used.
    """

    # Analyze the job description
    job_analysis = analyze_job_description(
        job_description
    )

    # Get verified candidate skills
    candidate_skills = candidate.get(
        "skills",
        []
    )

    # Compare candidate skills with job skills
    match = calculate_match(
        candidate_skills,
        job_analysis["skills"]
    )

    # Convert matched skills to lowercase
    matched_skill_names = {
        skill.lower().strip()
        for skill in match["matched_skills"]
    }

    # Keep only candidate skills that match
    # the job requirements
    matched_skills = [
        skill
        for skill in candidate_skills
        if skill.lower().strip()
        in matched_skill_names
    ]

    # Get candidate projects
    projects = candidate.get(
        "projects",
        []
    )

    # Get candidate education
    education = candidate.get(
        "education",
        []
    )

    # Build customized resume data
    customized_resume = {

        "name": candidate.get(
            "name",
            ""
        ),

        "email": candidate.get(
            "email",
            ""
        ),

        "phone": candidate.get(
            "phone",
            ""
        ),

        "education": education,

        # All verified candidate skills
        "skills": candidate_skills,

        # Skills relevant to this job
        "matched_skills": matched_skills,

        # Required skills that candidate doesn't have
        "missing_skills": match[
            "missing_skills"
        ],

        # Existing candidate projects
        "projects": projects,

        # Overall matching score
        "match_score": match[
            "score"
        ],

        # Full JD analysis
        "job_analysis": job_analysis
    }

    return customized_resume


# Test the resume customizer
if __name__ == "__main__":

    # Example candidate profile
    candidate = {

        "name": "Your Name",

        "email": "your.email@example.com",

        "phone": "+91XXXXXXXXXX",

        "skills": [
            "Java",
            "Spring Boot",
            "SQL",
            "React"
        ],

        "education": [
            {
                "degree": "B.Tech",
                "graduation_year": 2026
            }
        ],

        "projects": [
            {
                "name": "Health and Fitness Application",
                "technologies": [
                    "React",
                    "Node.js",
                    "MongoDB"
                ],
                "description":
                    "A health and fitness application."
            }
        ]
    }

    # Example job description
    job_description = """
    We are looking for a Java Developer.

    Required skills:
    Java,
    Spring Boot,
    SQL,
    Docker
    """

    # Customize resume data
    result = customize_resume_data(
        candidate,
        job_description
    )

    # Display results
    print()
    print("==============================")
    print("RESUME CUSTOMIZATION RESULT")
    print("==============================")

    print()
    print(
        "Match Score:",
        result["match_score"]
    )

    print()
    print(
        "Matched Skills:"
    )

    for skill in result["matched_skills"]:
        print(
            "-",
            skill
        )

    print()
    print(
        "Missing Skills:"
    )

    for skill in result["missing_skills"]:
        print(
            "-",
            skill
        )

    print()
    print(
        "Job Analysis:"
    )

    print(
        result["job_analysis"]
    )