import sqlite3, json

conn = sqlite3.connect("data/university.db")
questions = json.load(open("eval/questions.json", encoding="utf-8"))

for q in questions:
    try:
        rows = conn.execute(q["gold_sql"]).fetchall()
        shown = rows if len(rows) <= 5 else rows[:5] + ["..."]
        print(f'{q["id"]:>2} [{q["category"]}] {q["question_en"]}\n    -> {shown}\n')
    except Exception as e:
        print(f'{q["id"]:>2} ERROR: {e}\n')