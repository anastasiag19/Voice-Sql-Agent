import sqlite3

conn = sqlite3.connect("data/university.db")

for table in ["students", "courses", "instructors", "enrollments"]:
    n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"{table}: {n} rows")

print("\nSample students:")
for row in conn.execute("SELECT * FROM students LIMIT 3"):
    print(row)

print("\nIn-progress enrollments (grade is NULL):")
print(conn.execute("SELECT COUNT(*) FROM enrollments WHERE grade IS NULL").fetchone()[0])