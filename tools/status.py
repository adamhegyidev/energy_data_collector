import sqlite3


conn = sqlite3.connect(
    "data/db/energy_data.sqlite"
)

cursor = conn.cursor()

cursor.execute(
    """
    SELECT
        created_at,
        dataset,
        status
    FROM downloads
    ORDER BY created_at DESC
    LIMIT 20
    """
)

rows = cursor.fetchall()

conn.close()

for row in rows:
    print(row)