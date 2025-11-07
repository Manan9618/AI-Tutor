# app/graphs/quiz_workflow.py
from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END

from app.agents import QuizAgent, MemoryAgent

# Local agents for this graph. If you prefer shared singletons, import from app.api instead.
quiz_agent = QuizAgent(question_bank={})
memory_agent = MemoryAgent()


class QuizState(TypedDict):
    user_id: str
    topic: str
    level: str
    quiz: List[Dict]
    answers: Dict[int, str]
    score: float
    feedback: str


def gen_quiz(state: QuizState) -> QuizState:
    # Generate quiz and store it in state
    q = quiz_agent.generate_quiz(state["topic"], state["level"], num_questions=5)
    return {**state, "quiz": q}


def score_quiz(state: QuizState) -> QuizState:
    # Score using provided answers, update memory, and adapt level
    score, fb = quiz_agent.score_quiz(state.get("quiz", []), state.get("answers", {}))
    memory_agent.update_performance(state["user_id"], state["topic"], score)
    new_lvl = quiz_agent.adjust_difficulty(state.get("level", "beginner"), score)
    memory_agent.update_profile(state["user_id"], "level", new_lvl)
    return {**state, "score": score, "feedback": fb}


# Build the workflow
workflow = StateGraph(QuizState)

workflow.add_node("generate", gen_quiz)
workflow.add_node("score", score_quiz)

workflow.set_entry_point("generate")
workflow.add_edge("generate", "score")
workflow.add_edge("score", END)

quiz_workflow_graph = workflow.compile()
