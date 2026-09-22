from app.database.connection import SessionLocal
from app.models.job import Job
from app.services.learning_ranker import (
    calculate_learning_adjustment
)


db = SessionLocal()

try:

    job = (
        db.query(Job)
        .first()
    )

    if not job:

        print(
            "No jobs found in database."
        )

    else:

        result = (
            calculate_learning_adjustment(
                db=db,
                job=job
            )
        )

        print(
            "Learning result:"
        )

        print(result)

finally:

    db.close()