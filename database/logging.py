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
    file_path=None,
    error_message=None,
):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO downloads (
                source,
                dataset,
                start_date,
                end_date,
                file_path,
                status,
                error_message
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source,
                dataset,
                str(start_date),
                str(end_date),
                str(file_path) if file_path else None,
                status,
                error_message,
            ),
        )