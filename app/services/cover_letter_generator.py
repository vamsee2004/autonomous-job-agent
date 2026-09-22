import json
from pathlib import Path


PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]


PROFILE_PATH = (
    PROJECT_ROOT
    / "app"
    / "knowledge"
    / "candidate_profile.json"
)


OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "cover_letters"
)


OUTPUT_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True
)


def load_candidate_profile():
    with open(
        PROFILE_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def generate_cover_letter(
    job_title: str,
    company: str,
    job_description: str
):
    """
    Generate a job-specific cover letter
    using verified candidate information.
    """

    candidate = load_candidate_profile()

    candidate_name = candidate.get(
        "name",
        "Candidate"
    )

    candidate_email = candidate.get(
        "email",
        ""
    )

    candidate_phone = candidate.get(
        "phone",
        ""
    )

    skills = candidate.get(
        "skills",
        []
    )

    skill_text = ", ".join(
        skills[:8]
    )

    cover_letter = f"""Dear Hiring Manager,

I am writing to express my interest in the {job_title} position at {company}.

I recently completed my B.Tech and have developed skills in {skill_text}. I am particularly interested in this opportunity because it aligns with my technical background and my interest in building software applications.

I am a fresher who is eager to apply my technical knowledge in a professional environment, learn from experienced team members, and contribute to the development of reliable software solutions.

I would appreciate the opportunity to discuss how my skills and projects could contribute to your team.

Thank you for considering my application.

Sincerely,
{candidate_name}
{candidate_email}
{candidate_phone}
"""

    safe_company = "".join(
        character
        if character.isalnum()
        else "_"
        for character in company
    )

    safe_title = "".join(
        character
        if character.isalnum()
        else "_"
        for character in job_title
    )

    filename = (
        f"{safe_company}_"
        f"{safe_title}_cover_letter.txt"
    )

    output_path = (
        OUTPUT_DIRECTORY
        / filename
    )

    output_path.write_text(
        cover_letter,
        encoding="utf-8"
    )

    return output_path