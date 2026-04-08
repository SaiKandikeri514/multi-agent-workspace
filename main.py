import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()
from pydantic import BaseModel
from database.db_setup import init_db
from agents.graph import build_graph
from langchain_core.messages import HumanMessage
import os

app = FastAPI(title="Multi-Agent API")

class ChatRequest(BaseModel):
    message: str

@app.on_event("startup")
def startup_event():
    init_db()

@app.post("/chat")
def chat(req: ChatRequest):
    graph = build_graph()
    initial_state = {
        "messages": [HumanMessage(content=req.message)],
        "active_context": []
    }
    result = graph.invoke(initial_state)
    return {
        "status": "success", 
        "context": result.get("active_context", []),
        # Next agent is returned to trace graph finish state
        "graph_state": result.get("next_agent", "FINISH")
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
