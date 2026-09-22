import json

from pathlib import Path

from app.services.logger import logger


PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]


PROFILE_PATH = (
    PROJECT_ROOT
    / "app"
    / "knowledge"
    / "candidate_profile.json"
)


def load_candidate_profile():

    with open(
        PROFILE_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def normalize_question(question):

    return (
        question
        .strip()
        .lower()
    )


def answer_application_question(
    question: str
):
    """
    Answer an application question using
    verified candidate profile information.

    If the information is not available,
    return APPROVAL_REQUIRED instead of
    inventing an answer.
    """

    candidate = load_candidate_profile()

    normalized_question = (
        normalize_question(question)
    )

    education = candidate.get(
        "education",
        []
    )

    skills = candidate.get(
        "skills",
        []
    )

    experience = candidate.get(
        "experience",
        []
    )

    projects = candidate.get(
        "projects",
        []
    )

    preferences = candidate.get(
        "preferences",
        {}
    )

    name = candidate.get(
        "name"
    )

    email = candidate.get(
        "email"
    )

    phone = candidate.get(
        "phone"
    )

    # --------------------------------------------------
    # NAME
    # --------------------------------------------------

    if (
        "full name" in normalized_question
        or normalized_question == "name"
    ):

        if name and name != "Your Name":

            return {
                "status": "ANSWERED",
                "answer": name,
                "source": "candidate_profile"
            }

    # --------------------------------------------------
    # EMAIL
    # --------------------------------------------------

    if "email" in normalized_question:

        if email and (
            "your.email@example.com"
            not in email
        ):

            return {
                "status": "ANSWERED",
                "answer": email,
                "source": "candidate_profile"
            }

    # --------------------------------------------------
    # PHONE
    # --------------------------------------------------

    if (
        "phone" in normalized_question
        or "mobile" in normalized_question
    ):

        if phone and (
            "XXXXXXXXXX" not in phone
        ):

            return {
                "status": "ANSWERED",
                "answer": phone,
                "source": "candidate_profile"
            }

    # --------------------------------------------------
    # EDUCATION
    # --------------------------------------------------

    if (
        "degree" in normalized_question
        or "education" in normalized_question
        or "qualification" in normalized_question
    ):

        if education:

            degrees = [
                item.get("degree")
                for item in education
                if item.get("degree")
            ]

            if degrees:

                return {
                    "status": "ANSWERED",
                    "answer": ", ".join(
                        degrees
                    ),
                    "source": "candidate_profile"
                }

    # --------------------------------------------------
    # GRADUATION YEAR
    # --------------------------------------------------

    if (
        "graduation year"
        in normalized_question
        or "year of graduation"
        in normalized_question
        or "graduated" in normalized_question
    ):

        if education:

            years = [
                str(
                    item.get(
                        "graduation_year"
                    )
                )
                for item in education
                if item.get(
                    "graduation_year"
                )
            ]

            if years:

                return {
                    "status": "ANSWERED",
                    "answer": ", ".join(
                        years
                    ),
                    "source": "candidate_profile"
                }

    # --------------------------------------------------
    # SKILLS
    # --------------------------------------------------

    if (
        "skills" in normalized_question
        or "technologies" in normalized_question
        or "technical skills"
        in normalized_question
    ):

        if skills:

            return {
                "status": "ANSWERED",
                "answer": ", ".join(
                    skills
                ),
                "source": "candidate_profile"
            }

    # --------------------------------------------------
    # EXPERIENCE
    # --------------------------------------------------

    if (
        "experience" in normalized_question
        or "years of experience"
        in normalized_question
    ):

        if experience:

            return {
                "status": "ANSWERED",
                "answer": experience,
                "source": "candidate_profile"
            }

        return {
            "status": "ANSWERED",
            "answer": "Fresher",
            "source": "candidate_profile"
        }

    # --------------------------------------------------
    # JOB TITLE
    # --------------------------------------------------

    if (
        "desired role" in normalized_question
        or "preferred role"
        in normalized_question
        or "job title"
        in normalized_question
    ):

        job_titles = preferences.get(
            "job_titles",
            []
        )

        if job_titles:

            return {
                "status": "ANSWERED",
                "answer": job_titles[0],
                "source": "candidate_profile"
            }

    # --------------------------------------------------
    # LOCATION
    # --------------------------------------------------

    if (
        "preferred location"
        in normalized_question
        or "preferred city"
        in normalized_question
        or "location preference"
        in normalized_question
    ):

        locations = preferences.get(
            "locations",
            []
        )

        if locations:

            return {
                "status": "ANSWERED",
                "answer": locations[0],
                "source": "candidate_profile"
            }

    # --------------------------------------------------
    # WORK MODE
    # --------------------------------------------------

    if (
        "work mode" in normalized_question
        or "work preference"
        in normalized_question
        or "remote" in normalized_question
        or "hybrid" in normalized_question
    ):

        work_modes = preferences.get(
            "work_modes",
            []
        )

        if work_modes:

            return {
                "status": "ANSWERED",
                "answer": ", ".join(
                    work_modes
                ),
                "source": "candidate_profile"
            }

    # --------------------------------------------------
    # PROJECTS
    # --------------------------------------------------

    if (
        "project" in normalized_question
        or "projects" in normalized_question
    ):

        if projects:

            project_names = [
                project.get("name")
                for project in projects
                if project.get("name")
            ]

            if project_names:

                return {
                    "status": "ANSWERED",
                    "answer": ", ".join(
                        project_names
                    ),
                    "source": "candidate_profile"
                }

    # --------------------------------------------------
    # UNKNOWN QUESTION
    # --------------------------------------------------

    logger.warning(
        "Application question requires "
        f"candidate approval: {question}"
    )

    return {
        "status": "APPROVAL_REQUIRED",
        "answer": None,
        "question": question,
        "source": "candidate_profile",
        "message": (
            "Verified candidate information "
            "does not contain a safe answer. "
            "User approval is required."
        )
    }


def answer_application_questions(
    questions
):
    """
    Answer multiple application questions.
    """

    results = []

    for question in questions:

        result = (
            answer_application_question(
                question
            )
        )

        results.append(
            {
                "question": question,
                **result
            }
        )

    answered = sum(
        1
        for result in results
        if result["status"] == "ANSWERED"
    )

    approval_required = sum(
        1
        for result in results
        if result["status"]
        == "APPROVAL_REQUIRED"
    )

    return {
        "success": True,
        "total_questions": len(
            questions
        ),
        "answered": answered,
        "approval_required": (
            approval_required
        ),
        "results": results
    }