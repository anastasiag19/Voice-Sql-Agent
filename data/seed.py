import sqlite3, random, os
from faker import Faker

random.seed(42)
fake = Faker()
Faker.seed(42)

MAJORS = ["Computer Science", "Mathematics", "Physics", "Business", "Biology"]
DEPTS = MAJORS
SEMESTERS = ["Fall 2024", "Spring 2025", "Fall 2025", "Spring 2026"]

course_titles = [
    ("Intro to Programming", "Computer Science", 6),
    ("Data Structures", "Computer Science", 6),
    ("Databases", "Computer Science", 5),
    ("Machine Learning", "Computer Science", 6),
    ("Calculus I", "Mathematics", 6),
    ("Linear Algebra", "Mathematics", 5),
    ("Statistics", "Mathematics", 5),
    ("Mechanics", "Physics", 6),
    ("Microeconomics", "Business", 5),
    ("Marketing Basics", "Business", 4),
    ("Genetics", "Biology", 5),
    ("Ecology", "Biology", 4),
]

if os.path.exists("data/university.db"):
    os.remove("data/university.db")

conn = sqlite3.connect("data/university.db")
conn.executescript(open("data/schema.sql").read())

for i, (t, d, c) in enumerate(course_titles, 1):
    conn.execute("INSERT INTO courses VALUES (?,?,?,?)", (i, t, d, c))

for i in range(1, 13):
    conn.execute("INSERT INTO instructors VALUES (?,?,?)",
                 (i, fake.name(), random.choice(DEPTS)))

for i in range(1, 81):
    conn.execute("INSERT INTO students VALUES (?,?,?,?,?)",
                 (i, fake.first_name(), fake.last_name(),
                  random.randint(1, 4), random.choice(MAJORS)))

eid = 1
for s in range(1, 81):
    for c in random.sample(range(1, 13), k=random.randint(3, 6)):
        sem = random.choice(SEMESTERS)
        if sem == "Spring 2026" and random.random() < 0.5:
            grade = None
        else:
            grade = round(max(0, min(100, random.gauss(72, 12))), 1)
        conn.execute("INSERT INTO enrollments VALUES (?,?,?,?,?,?)",
                     (eid, s, c, random.randint(1, 12), sem, grade))
        eid += 1

conn.commit()
conn.close()
print("Database created.")