import os, sys, json, asyncio
from pathlib import Path
from typing import TypedDict
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, END

load_dotenv()
ROOT = Path(__file__).resolve().parent.parent
MAX_ATTEMPTS = 3

llm = ChatGoogleGenerativeAI(model=os.getenv("LLM_MODEL"), temperature=0)


# ---------- helpers ----------
def text_of(msg):
    """Get plain text out of a model reply (it may be a list of blocks)."""
    c = msg.content
    if isinstance(c, str):
        return c
    return "".join(b.get("text", "") for b in c if isinstance(b, dict))


def unpack(result):
    """Turn an MCP tool result into plain Python data."""
    if isinstance(result, tuple):
        result = result[0]
    if isinstance(result, str):
        blocks = [result]
    else:
        blocks = [b["text"] if isinstance(b, dict) else getattr(b, "text", str(b))
                  for b in result]
    out = []
    for b in blocks:
        try:
            out.append(json.loads(b))
        except Exception:
            out.append(b)
    if len(out) == 1 and isinstance(out[0], list):
        out = out[0]
    return out


def clean_sql(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("sql"):
            text = text[3:]
    return text.strip().rstrip(";").strip()


# ---------- state ----------
class State(TypedDict):
    question: str
    schema: str
    sql: str
    result: dict
    error: str
    attempts: int
    answer: str


# ---------- graph ----------
async def build_graph():
    client = MultiServerMCPClient({
        "university": {
            "command": sys.executable,
            "args": [str(ROOT / "server" / "mcp_server.py")],
            "transport": "stdio",
        }
    })
    tools = {t.name: t for t in await client.get_tools()}

    async def inspect_schema(state: State):
        tables = unpack(await tools["list_tables"].ainvoke({}))
        lines = []
        for t in tables:
            cols = unpack(await tools["describe_table"].ainvoke({"table_name": t}))
            desc = ", ".join(f"{c['column']} {c['type']}" for c in cols)
            lines.append(f"{t}({desc})")
        return {"schema": "\n".join(lines), "attempts": 0, "error": ""}

    async def generate_sql(state: State):
        prompt = (
            "You write SQLite queries.\n"
            f"Schema:\n{state['schema']}\n\n"
            "Notes: enrollments.grade is NULL when the course is still in progress. "
            "Use exact names from the question.\n"
            "Return ONLY one SQL SELECT statement, with no explanation and no markdown.\n\n"
            f"Question: {state['question']}\n"
        )
        if state["error"]:
            prompt += (f"\nYour previous query was:\n{state['sql']}\n"
                       f"It failed with: {state['error']}\nFix it.\n")
        reply = await llm.ainvoke(prompt)
        return {"sql": clean_sql(text_of(reply))}

    async def execute(state: State):
        res = unpack(await tools["run_readonly_query"].ainvoke({"sql": state["sql"]}))[0]
        if isinstance(res, dict) and "error" in res:
            return {"error": res["error"], "attempts": state["attempts"] + 1}
        return {"result": res, "error": ""}

    async def answer(state: State):
        if state["error"]:
            return {"answer": f"I could not answer this. Last error: {state['error']}"}
        prompt = (
            f"Question: {state['question']}\n"
            f"SQL result (columns and rows): {json.dumps(state['result'])}\n"
            "Answer the question in one short sentence using only this result."
        )
        reply = await llm.ainvoke(prompt)
        return {"answer": text_of(reply).strip()}

    def after_execute(state: State):
        if state["error"] and state["attempts"] < MAX_ATTEMPTS:
            return "retry"
        return "done"

    g = StateGraph(State)
    g.add_node("inspect_schema", inspect_schema)
    g.add_node("generate_sql", generate_sql)
    g.add_node("execute", execute)
    g.add_node("answer", answer)
    g.set_entry_point("inspect_schema")
    g.add_edge("inspect_schema", "generate_sql")
    g.add_edge("generate_sql", "execute")
    g.add_conditional_edges("execute", after_execute,
                            {"retry": "generate_sql", "done": "answer"})
    g.add_edge("answer", END)
    return g.compile()


async def ask(graph, question):
    return await graph.ainvoke({"question": question, "schema": "", "sql": "",
                                "result": {}, "error": "", "attempts": 0, "answer": ""})


async def main():
    graph = await build_graph()
    questions = json.load(open(ROOT / "eval" / "questions.json", encoding="utf-8"))
    for q in questions[:3]:
        out = await ask(graph, q["question_en"])
        print(f"Q: {q['question_en']}")
        print(f"SQL: {out['sql']}")
        print(f"Attempts with errors: {out['attempts']}")
        print(f"A: {out['answer']}\n")

if __name__ == "__main__":
    asyncio.run(main())