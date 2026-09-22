import re


COMMON_SKILLS = [
    "java",
    "spring boot",
    "spring",
    "sql",
    "react",
    "javascript",
    "python",
    "django",
    "node.js",
    "mongodb",
    "aws",
    "docker",
    "git",
    "html",
    "css",
    "rest api"
]


def analyze_job_description(description: str):

    text = description.lower()

    detected_skills = []

    for skill in COMMON_SKILLS:
        if skill in text:
            detected_skills.append(skill)

    experience = None

    match = re.search(
        r"(\d+)\s*(?:to|-)?\s*(\d+)?\s*years?",
        text
    )

    if match:
        experience = match.group(0)

    return {
        "skills": detected_skills,
        "experience_requirement": experience,
        "description_length": len(description)
    }