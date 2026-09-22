import json
import re
import subprocess
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from app.services.resume_customizer import (
    customize_resume_data
)


# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Candidate profile
PROFILE_PATH = (
    PROJECT_ROOT
    / "app"
    / "knowledge"
    / "candidate_profile.json"
)

# Resume templates
TEMPLATE_PATH = (
    PROJECT_ROOT
    / "app"
    / "templates"
)


def create_safe_filename(text):
    """
    Convert job title/company into a safe filename.
    """

    filename = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        text
    )

    return filename.strip("_").lower()


def generate_job_resume(
    job_title,
    company,
    job_description
):
    """
    Generate a job-specific PDF resume.
    """

    # Load candidate profile
    with open(
        PROFILE_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        candidate = json.load(file)

    # Customize resume data
    resume_data = customize_resume_data(
        candidate,
        job_description
    )

    # Configure Jinja2
    environment = Environment(
        loader=FileSystemLoader(
            str(TEMPLATE_PATH)
        )
    )

    # Load template
    template = environment.get_template(
        "resume_template.tex"
    )

    # Generate LaTeX
    resume = template.render(
        name=resume_data["name"],
        email=resume_data["email"],
        phone=resume_data["phone"],
        education_list=resume_data["education"],
        skills=", ".join(
            resume_data["matched_skills"]
        ),
        projects=resume_data["projects"]
    )

    # Create output directory
    output_directory = (
        PROJECT_ROOT
        / "data"
        / "resumes"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    # Create safe filename
    job_name = create_safe_filename(
        job_title
    )

    company_name = create_safe_filename(
        company
    )

    filename = (
        f"{job_name}_{company_name}"
    )

    # Save .tex
    tex_file = (
        output_directory
        / f"{filename}.tex"
    )

    with open(
        tex_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(resume)

    print()
    print("Job-specific LaTeX resume created:")
    print(tex_file)

    # Generate PDF
    try:

        result = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-output-directory",
                str(output_directory),
                str(tex_file)
            ],
            capture_output=True,
            text=True
        )

    except FileNotFoundError:

        print(
            "ERROR: pdflatex was not found."
        )

        return tex_file

    # Check compilation
    if result.returncode != 0:

        print()
        print(
            "ERROR: PDF generation failed."
        )

        print(result.stdout)

        if result.stderr:
            print(result.stderr)

        return tex_file

    # PDF path
    pdf_file = (
        output_directory
        / f"{filename}.pdf"
    )

    if pdf_file.exists():

        print()
        print(
            "Job-specific PDF generated successfully!"
        )

        print(
            "PDF location:"
        )

        print(pdf_file)

        print()
        print(
            "Match score:",
            resume_data["match_score"]
        )

        return pdf_file

    print(
        "PDF was not created."
    )

    return tex_file


# Test
if __name__ == "__main__":

    test_job_title = (
        "Java Developer"
    )

    test_company = (
        "Example Company"
    )

    test_job_description = """
    We are looking for a Java Developer.

    Required skills:
    Java,
    Spring Boot,
    SQL,
    Docker
    """

    result = generate_job_resume(
        test_job_title,
        test_company,
        test_job_description
    )

    print()
    print(
        "Generated file:"
    )

    print(result)