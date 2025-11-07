# app/graphs/learning_session.py
from typing import TypedDict, List, Dict, Optional
from langgraph.graph import StateGraph, END

from app.agents import (
    MemoryAgent,
    PathGeneratorAgent,
    ExplanationAgent,
    QuizAgent,
    AnalyticsAgent,
)

# Create local agent instances for graph usage.
# If you want global/shared state across API calls, import the singletons from app.api instead.
memory_agent = MemoryAgent()
path_generator = PathGeneratorAgent(topics_graph={})
explanation_agent = ExplanationAgent(content_repo={})
quiz_agent = QuizAgent(question_bank={})
analytics_agent = AnalyticsAgent()


class LearningSessionState(TypedDict, total=False):
    user_id: str
    profile: Dict
    roadmap: List[str]
    current_idx: int
    current_topic: str
    explanation: str
    quiz: List[Dict]
    user_answers: Dict[int, str]
    score: float
    feedback: str
    recommendations: str
    finished: bool


# Node implementations ----------------------------------------------------
def load_profile(state: LearningSessionState) -> LearningSessionState:
    profile = memory_agent.get_profile(state["user_id"])
    return {**state, "profile": profile}


def generate_roadmap(state: LearningSessionState) -> LearningSessionState:
    roadmap = path_generator.generate_roadmap(state["user_id"], memory_agent)
    # Ensure roadmap is a list
    if not isinstance(roadmap, list):
        # If path_generator returned a newline-separated string, split defensively
        if isinstance(roadmap, str):
            roadmap = [line.strip() for line in roadmap.split("\n") if line.strip()]
        else:
            roadmap = []
    return {**state, "roadmap": roadmap, "current_idx": 0}


def pick_next_topic(state: LearningSessionState) -> LearningSessionState:
    roadmap = state.get("roadmap", [])
    idx = state.get("current_idx", 0)
    if idx >= len(roadmap):
        return {**state, "finished": True}
    topic = roadmap[idx]
    return {**state, "current_topic": topic}


def explain_topic(state: LearningSessionState) -> LearningSessionState:
    topic = state.get("current_topic", "")
    profile = state.get("profile", {})
    level = profile.get("level", "beginner")
    style = profile.get("style", "visual")
    explanation = explanation_agent.explain_concept(topic, level, style)
    return {**state, "explanation": explanation}


def generate_quiz(state: LearningSessionState) -> LearningSessionState:
    topic = state.get("current_topic", "")
    profile = state.get("profile", {})
    level = profile.get("level", "beginner")
    quiz = quiz_agent.generate_quiz(topic, level, num_questions=5)
    return {**state, "quiz": quiz}


def await_answers(state: LearningSessionState) -> LearningSessionState:
    """
    Placeholder node. External code (API) should populate 'user_answers' in the state
    prior to resuming the graph. This node simply returns the state unchanged.
    """
    return state


def score_and_feedback(state: LearningSessionState) -> LearningSessionState:
    quiz = state.get("quiz", [])
    answers = state.get("user_answers", {})
    score, feedback = quiz_agent.score_quiz(quiz, answers)

    # Update memory & adapt level
    memory_agent.update_performance(state["user_id"], state.get("current_topic", ""), score)
    new_level = quiz_agent.adjust_difficulty(state.get("profile", {}).get("level", "beginner"), score)
    memory_agent.update_profile(state["user_id"], "level", new_level)

    return {
        **state,
        "score": score,
        "feedback": feedback,
        "current_idx": state.get("current_idx", 0) + 1,
    }


def give_recommendations(state: LearningSessionState) -> LearningSessionState:
    rec = analytics_agent.generate_recommendations(state["user_id"], memory_agent)
    return {**state, "recommendations": rec}


def decide_next(state: LearningSessionState) -> str:
    if state.get("finished"):
        return END
    # If the student did poorly, repeat explanation for the same topic
    if state.get("score", 1.0) < 0.5:
        return "explain_topic"
    # Otherwise continue to pick next topic (which advances current_idx)
    return "pick_next_topic"


# Build the graph --------------------------------------------------------
workflow = StateGraph(LearningSessionState)

# Add nodes
workflow.add_node("load_profile", load_profile)
workflow.add_node("generate_roadmap", generate_roadmap)
workflow.add_node("pick_next_topic", pick_next_topic)
workflow.add_node("explain_topic", explain_topic)
workflow.add_node("generate_quiz", generate_quiz)
workflow.add_node("await_answers", await_answers)
workflow.add_node("score_and_feedback", score_and_feedback)
workflow.add_node("give_recommendations", give_recommendations)

# Edges and flow:
workflow.set_entry_point("load_profile")
workflow.add_edge("load_profile", "generate_roadmap")
workflow.add_edge("generate_roadmap", "pick_next_topic")
workflow.add_edge("pick_next_topic", "explain_topic")
workflow.add_edge("explain_topic", "generate_quiz")

# After generating quiz, wait for answers externally, then resume to scoring
workflow.add_edge("generate_quiz", "await_answers")
workflow.add_edge("await_answers", "score_and_feedback")

# After scoring, give recommendations then decide the next step
workflow.add_edge("score_and_feedback", "give_recommendations")

# Decide next step: either explain_topic (repeat), pick_next_topic (advance), or END
workflow.add_conditional_edges("give_recommendations", decide_next, {
    "explain_topic": "explain_topic",
    "pick_next_topic": "pick_next_topic",
    END: END,
})

# Compile graph for execution
learning_session_graph = workflow.compile()
