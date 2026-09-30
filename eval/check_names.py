import sqlite3
conn = sqlite3.connect("data/university.db")

names = [("Cynthia","Diaz"), ("Veronica","Bowman"), ("Joseph","Zuniga"),
         ("Craig","Ramirez"), ("Frank","Gray"), ("George","Daniel"),
         ("Michelle","Ray")]

for first, last in names:
    n = conn.execute("SELECT COUNT(*) FROM students WHERE first_name=? AND last_name=?",
                     (first, last)).fetchone()[0]
    avg = conn.execute("""SELECT ROUND(AVG(e.grade),1) FROM students s
        JOIN enrollments e ON s.student_id=e.student_id
        WHERE s.first_name=? AND s.last_name=?""", (first, last)).fetchone()[0]
    total = conn.execute("""SELECT COUNT(*) FROM students s
        JOIN enrollments e ON s.student_id=e.student_id
        WHERE s.first_name=? AND s.last_name=?""", (first, last)).fetchone()[0]
    print(f"{first} {last}: {n} student(s), {total} enrollments, avg grade {avg}")