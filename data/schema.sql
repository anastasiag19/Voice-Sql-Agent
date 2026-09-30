CREATE TABLE students (
    student_id   INTEGER PRIMARY KEY,
    first_name   TEXT NOT NULL,
    last_name    TEXT NOT NULL,
    year         INTEGER CHECK (year BETWEEN 1 AND 4),
    major        TEXT NOT NULL
);

CREATE TABLE courses (
    course_id    INTEGER PRIMARY KEY,
    title        TEXT NOT NULL,
    department   TEXT NOT NULL,
    credits      INTEGER NOT NULL
);

CREATE TABLE instructors (
    instructor_id INTEGER PRIMARY KEY,
    name          TEXT NOT NULL,
    department    TEXT NOT NULL
);

CREATE TABLE enrollments (
    enrollment_id INTEGER PRIMARY KEY,
    student_id    INTEGER REFERENCES students(student_id),
    course_id     INTEGER REFERENCES courses(course_id),
    instructor_id INTEGER REFERENCES instructors(instructor_id),
    semester      TEXT NOT NULL,
    grade         REAL
);