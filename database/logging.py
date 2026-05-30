from database.connection import get_connection


def init_db():
    with open("database/schema.sql", "r", encoding="utf-8") as file:
        schema = file.read()

    with get_connection() as connection:
        connection.executescript(schema)


def log_download(
    source,
    dataset,
    start_date,
    end_date,
    status,
    category=None,
    requested_frequency=None,
    actual_frequency=None,
    file_path=None,
    error_message=None,
):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO downloads (
                source,
                category,
                dataset,
                start_date,
                end_date,
                requested_frequency,
                actual_frequency,
                file_path,
                status,
                error_message
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source,
                category,
                dataset,
                str(start_date),
                str(end_date),
                requested_frequency,
                actual_frequency,
                str(file_path) if file_path else None,
                status,
                error_message,
            ),
        )