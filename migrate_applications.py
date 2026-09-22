from sqlalchemy import text

from app.database.connection import engine


def add_column_if_missing(
    connection,
    table_name,
    column_name,
    column_definition
):
    result = connection.execute(
        text(
            f"PRAGMA table_info({table_name})"
        )
    )

    existing_columns = {
        row[1]
        for row in result.fetchall()
    }

    if column_name not in existing_columns:
        connection.execute(
            text(
                f"""
                ALTER TABLE {table_name}
                ADD COLUMN {column_name}
                {column_definition}
                """
            )
        )

        print(
            f"Added column: {column_name}"
        )

    else:
        print(
            f"Column already exists: {column_name}"
        )


with engine.begin() as connection:

    add_column_if_missing(
        connection,
        "applications",
        "approval_required",
        "INTEGER DEFAULT 1"
    )

    add_column_if_missing(
        connection,
        "applications",
        "approved",
        "INTEGER DEFAULT 0"
    )


print(
    "Application table migration completed."
)