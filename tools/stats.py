import sqlite3


conn = sqlite3.connect(
    "data/db/energy_data.sqlite"
)

cursor = conn.cursor()

cursor.execute(
    """
    SELECT
        status,
        COUNT(*)
    FROM downloads
    GROUP BY status
    """
)

rows = cursor.fetchall()

conn.close()

print("\nDOWNLOAD STATS\n")

for status, count in rows:
    print(f"{status}: {count}")