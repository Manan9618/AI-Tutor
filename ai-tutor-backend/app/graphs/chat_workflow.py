# app/graphs/chat_workflow.py
from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END

# Use the agent class from app.agents (creates a local instance for graph use)
from app.agents import ChatAgent

# Create a ChatAgent instance local to the graph.
# If you want to share state with the API, use the shared agent singleton from app.api instead.
chat_agent = ChatAgent()


class ChatState(TypedDict):
    user_id: str
    history: List[Dict[str, str]]       # [{"role": "user"/"assistant", "content": "..."}]
    user_message: str
    assistant_reply: str


def append_user(state: ChatState) -> ChatState:
    history = state.get("history", [])
    history.append({"role": "user", "content": state["user_message"]})
    return {**state, "history": history}


def generate_reply(state: ChatState) -> ChatState:
    # Route message to ChatAgent and append assistant reply
    reply = chat_agent.respond(state["user_message"], {"user_id": state["user_id"]})
    history = state.get("history", [])
    history.append({"role": "assistant", "content": reply})
    return {**state, "assistant_reply": reply, "history": history}


# Build the graph
workflow = StateGraph(ChatState)

workflow.add_node("add_user", append_user)
workflow.add_node("reply", generate_reply)

workflow.set_entry_point("add_user")
workflow.add_edge("add_user", "reply")
workflow.add_edge("reply", END)

chat_workflow_graph = workflow.compile()
