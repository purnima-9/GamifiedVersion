import sqlite3
from pathlib import Path


# Update this path if your SQLite database lives elsewhere.
BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "survey.db"

# print(DB_PATH)

columns = {
    "survey_json": "JSON",
    "served_question_ids": "JSON",
    "current_question_id": "VARCHAR(50)",
}

with sqlite3.connect(DB_PATH) as connection:
    existing = {
        row[1]
        for row in connection.execute("PRAGMA table_info(survey_sessions)")
    }

    for name, sql_type in columns.items():
        if name not in existing:
            connection.execute(
                f"ALTER TABLE survey_sessions ADD COLUMN {name} {sql_type}"
            )

print("Phase 7 migration completed.")