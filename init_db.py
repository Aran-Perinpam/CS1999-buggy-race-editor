import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_FILE = os.path.join(BASE_DIR, "database.db")

#-----------------------------------------------------------------------------
# This script initialises your SQLite database for you, just to get you
# started... there are better ways to express the data you're going to need,
# especially outside SQLite. For example... maybe flag_pattern should be an
# ENUM (which is available in most other SQL databases), or a foreign key
# to a pattern table?
#
# Also... the name of the database (here, in SQLite, it's a filename) appears
# in more than one place in the project. That doesn't feel right, does it?
#-----------------------------------------------------------------------------

connection = sqlite3.connect(DATABASE_FILE)
print(f"- Opened database successfully in file \"{DATABASE_FILE}\"")

# using Python's triple-quote for multi-line strings:

connection.execute("""
  DROP TABLE buggies                
""")

connection.execute("""

  CREATE TABLE IF NOT EXISTS buggies (
    id                    INTEGER PRIMARY KEY,
    qty_wheels            INTEGER DEFAULT 4,
    flag_color            VARCHAR(20),
    flag_color_secondary  VARCHAR(20),
    flag_pattern          VARCHAR(20),
    cost_limit            INTEGER,
    total_cost            INTEGER DEFAULT 6
  )

""")

print("- OK, table \"buggies\" exists")

cursor = connection.cursor()

cursor.execute("SELECT * FROM buggies LIMIT 1")
rows = cursor.fetchall()
if len(rows) == 0:
    cursor.execute("INSERT INTO buggies (qty_wheels) VALUES (4)")
    connection.commit()
    print("- Added one 4-wheeled buggy")
else:
    print("- Found a buggy in the database, nice")

print("- OK, your database is ready")

connection.close()
