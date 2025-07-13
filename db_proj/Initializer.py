import sqlite3

conn = sqlite3.connect("dd.db")

conn.execute("PRAGMA foreign_keys = ON;")

with open("schema.sql", "r") as f:
    schema_script = f.read()

conn.executescript(schema_script)

conn.commit()
conn.close()

print("✅ Database initialized successfully!")
