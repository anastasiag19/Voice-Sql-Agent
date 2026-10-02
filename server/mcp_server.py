import sqlite3
import re
from pathlib import Path
from mcp.server.fastmcp import FastMCP

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "university.db"
MAX_ROWS = 100

mcp = FastMCP("university-db")


def get_connection():
   
    return sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)


@mcp.tool()
def list_tables() -> list[str]:
    """List all tables in the university database."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
    return [r[0] for r in rows]


@mcp.tool()
def describe_table(table_name: str) -> list[dict]:
    """Describe the columns of a table: name, type, and whether it is required."""
    if table_name not in list_tables():
        return [{"error": f"Unknown table '{table_name}'. Use list_tables first."}]
    with get_connection() as conn:
        rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return [{"column": r[1], "type": r[2], "not_null": bool(r[3]), "primary_key": bool(r[5])}
            for r in rows]


@mcp.tool()
def run_readonly_query(sql: str) -> dict:
    """Run a single read-only SELECT query and return the columns and rows (max 100 rows)."""
    cleaned = sql.strip().rstrip(";").strip()

    if not re.match(r"^(select|with)\b", cleaned, re.IGNORECASE):
        return {"error": "Only SELECT queries are allowed."}
    if ";" in cleaned:
        return {"error": "Only one statement is allowed."}

    try:
        with get_connection() as conn:
            cursor = conn.execute(cleaned)
            columns = [d[0] for d in cursor.description]
            rows = cursor.fetchmany(MAX_ROWS)
        return {"columns": columns, "rows": rows, "row_count": len(rows)}
    except Exception as e:
        # return the error as text so the agent can read it and retry
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run()