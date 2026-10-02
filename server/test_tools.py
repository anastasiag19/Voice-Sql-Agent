from mcp_server import list_tables, describe_table, run_readonly_query

print(list_tables())
print(describe_table("students"))
print(describe_table("nonexistent"))
print(run_readonly_query("SELECT COUNT(*) FROM students;"))
print(run_readonly_query("SELECT * FROM students LIMIT 2"))
print(run_readonly_query("SELECT bad_column FROM students"))
print(run_readonly_query("DROP TABLE students"))
print(run_readonly_query("SELECT 1; DELETE FROM students"))