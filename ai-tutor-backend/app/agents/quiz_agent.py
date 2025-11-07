# app/agents/quiz_agent.py
from .base_agent import BaseAgent


class QuizAgent(BaseAgent):
    """
    Creates quizzes and evaluates performance.
    """

    def __init__(self, question_bank: dict | None = None, model_name: str = "mistral"):
        super().__init__(model_name=model_name)
        self.question_bank = question_bank or {
            "addition": ["What is {a} + {b}? | {answer}"],
        }

    def generate_quiz(self, topic: str, level: str = "beginner", num_questions: int = 5, mcq: bool = True):
        if mcq:
            prompt = (
                f"Generate {num_questions} {level}-level multiple choice questions on {topic}. "
                f"Format each question as:\n"
                f"Question text\n"
                f"A) Option 1\n"
                f"B) Option 2\n"
                f"C) Option 3\n"
                f"D) Option 4\n"
                f"Answer: X (where X is the correct option letter)\n\n"
                f"Separate each question with a blank line."
            )
            raw_quiz = self.call_llm(prompt, system_message="You are a quiz generator. Follow the format exactly.")
            quiz = self._parse_mcq_quiz(raw_quiz)
        else:
            prompt = (
                f"Generate {num_questions} {level}-level questions on {topic} with answers, "
                f"in 'Question | Answer' format (one per line)."
            )
            raw_quiz = self.call_llm(prompt, system_message="You are a quiz generator.")
            quiz = self._parse_simple_quiz(raw_quiz)
        
        return quiz

    def _parse_mcq_quiz(self, raw_quiz: str) -> list[dict]:
        quiz = []
        questions = raw_quiz.strip().split("\n\n")
        
        for i, question_block in enumerate(questions):
            lines = [line.strip() for line in question_block.split("\n") if line.strip()]
            
            if len(lines) < 6:  # Need at least question + 4 options + answer
                continue
            
            question_text = lines[0]
            options = {}
            correct_answer = None
            
            for line in lines[1:]:
                if line.startswith(("A)", "B)", "C)", "D)")):
                    option_letter = line[0]
                    option_text = line[2:].strip()
                    options[option_letter] = option_text
                elif line.lower().startswith("answer:"):
                    correct_answer = line.split(":", 1)[1].strip().upper()
                    if ")" in correct_answer:
                        correct_answer = correct_answer.split(")")[0].strip()
                    correct_answer = correct_answer[0] if correct_answer else None
            
            if question_text and len(options) == 4 and correct_answer:
                quiz.append({
                    "id": i,
                    "question": question_text,
                    "options": options,
                    "answer": correct_answer,
                    "type": "mcq"
                })
        
        return quiz

    def _parse_simple_quiz(self, raw_quiz: str) -> list[dict]:
        quiz = []
        for i, line in enumerate(raw_quiz.split("\n")):
            if "|" in line:
                q, a = line.split("|", 1)
                quiz.append({
                    "id": i,
                    "question": q.strip(),
                    "answer": a.strip(),
                    "type": "simple"
                })
        return quiz

    def score_quiz(self, quiz: list[dict], user_answers: dict) -> tuple[float, str]:
        score = 0
        feedback = []
        
        for q in quiz:
            user_ans = user_answers.get(q["id"], "").strip().upper()
            
            if q.get("type") == "mcq":
                correct = q["answer"].upper()
                if user_ans == correct:
                    score += 1
                else:
                    correct_option = q["options"].get(correct, "Unknown")
                    user_option = q["options"].get(user_ans, user_ans) if user_ans else "No answer"
                    fb = self.call_llm(
                        f"Briefly explain why option {user_ans} ({user_option}) is incorrect for the question: '{q['question']}'. "
                        f"The correct answer is {correct} ({correct_option}).",
                        max_tokens=100,
                    )
                    feedback.append(f"Q{q['id']+1}: {fb}")
            else:
                correct = q["answer"].strip().lower()
                user_ans_lower = user_ans.lower()
                if user_ans_lower == correct:
                    score += 1
                else:
                    fb = self.call_llm(
                        f"Explain why '{user_ans}' is wrong for '{q['question']}'. Correct is '{q['answer']}'.",
                        max_tokens=100,
                    )
                    feedback.append(f"Q{q['id']+1}: {fb}")
        
        return score / len(quiz) if quiz else 0, "\n\n".join(feedback)

    def adjust_difficulty(self, current_level: str, score: float) -> str:
        if score > 0.8:
            return "advanced"
        elif score < 0.5:
            return "beginner"
        return current_level