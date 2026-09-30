import sqlite3
conn = sqlite3.connect("data/university.db")
q = """
SELECT s.first_name, s.last_name, COUNT(*)
FROM students s JOIN enrollments e ON s.student_id = e.student_id
WHERE e.semester = 'Fall 2025'
GROUP BY s.student_id
LIMIT 15
"""
for row in conn.execute(q):
    print(row)