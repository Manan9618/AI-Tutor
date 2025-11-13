# app/agents/quiz_agent.py
from .base_agent import BaseAgent


class QuizAgent(BaseAgent):
    """
    Creates quizzes and evaluates performance.
    """

    def __init__(self, question_bank: dict | None = None, model_name: str = "gemini-2.0-flash-lite"):
        super().__init__(model_name=model_name)
        self.question_bank = question_bank or {
            "addition": ["What is {a} + {b}? | {answer}"],
        }

    async def generate_quiz(self, topic: str, level: str = "beginner", num_questions: int = 5, mcq: bool = True):
        if mcq:
            # ✅ STRONGER PROMPT with explicit formatting rules
            prompt = (
    f"Generate exactly {num_questions} multiple-choice questions on '{topic}' for {level} learners. "
    f"Follow these rules STRICTLY:\n"
    f"1. Each question must have exactly 4 options labeled A), B), C), D)\n"
    f"2. Only one option is correct\n"
    f"3. After options, write 'Answer: X' where X is A, B, C, or D\n"
    f"4. Separate each question with two newlines (\\n\\n)\n"
    f"5. Do NOT output any extra text, numbers, or markdown headers\n"
    f"6. Output ONLY the questions in this exact format.\n\n"
    f"Example:\n"
    f"What is 2 + 2?\n"
    f"A) 3\n"
    f"B) 4\n"
    f"C) 5\n"
    f"D) 6\n"
    f"Answer: B\n\n"
)
            raw_quiz = await self.call_llm(
                prompt,
                system_message="You are a precise quiz generator. Output ONLY questions in the exact format specified. No explanations."
            )
            quiz = self._parse_mcq_quiz(raw_quiz)
        else:
            prompt = (
                f"Generate {num_questions} {level}-level questions on {topic} with answers, "
                f"in 'Question | Answer' format (one per line)."
            )
            raw_quiz = await self.call_llm(
                prompt,
                system_message="You are a quiz generator."
            )
            quiz = self._parse_simple_quiz(raw_quiz)
        
        # Ensure we return exactly `num_questions` (fallback if parsing fails)
        if len(quiz) < num_questions and mcq:
            # Optionally fill with simple questions or log warning
            pass

        return quiz

    def _parse_mcq_quiz(self, raw_quiz: str) -> list[dict]:
        quiz = []
        if not raw_quiz or not raw_quiz.strip():
            return quiz

        # Split by double newline (robust)
        blocks = [block.strip() for block in raw_quiz.strip().split("\n\n") if block.strip()]
        
        for i, block in enumerate(blocks):
            lines = [line.strip() for line in block.split("\n") if line.strip()]
            if len(lines) < 6:  # At least: Q, A, B, C, D, Answer
                continue

            question_text = lines[0]
            options = {}
            correct_answer = None

            # Parse options A-D
            expected_letters = ["A", "B", "C", "D"]
            for j, letter in enumerate(expected_letters):
                if j + 1 < len(lines):
                    line = lines[j + 1]
                    if line.startswith(f"{letter})"):
                        option_text = line[2:].strip()
                        if option_text:
                            options[letter] = option_text

            # Validate: must have exactly 4 options
            if len(options) != 4:
                continue

            # Parse answer line (usually last line)
            answer_line = None
            for line in reversed(lines):
                if line.lower().startswith("answer:"):
                    answer_line = line
                    break

            if not answer_line:
                continue

            # Extract answer letter
            try:
                ans_part = answer_line.split(":", 1)[1].strip().upper()
                # Extract first letter if it's A-D
                if ans_part and ans_part[0] in "ABCD":
                    correct_answer = ans_part[0]
                else:
                    continue
            except (IndexError, AttributeError):
                continue

            # Validate correct_answer is in options
            if correct_answer not in options:
                continue

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
        if not raw_quiz:
            return quiz
        for i, line in enumerate(raw_quiz.split("\n")):
            line = line.strip()
            if not line or "|" not in line:
                continue
            parts = line.split("|", 1)
            if len(parts) == 2:
                q, a = parts
                quiz.append({
                    "id": i,
                    "question": q.strip(),
                    "answer": a.strip(),
                    "type": "simple"
                })
        return quiz

    async def score_quiz(self, quiz: list[dict], user_answers: dict) -> tuple[float, str]:
        score = 0
        feedback = []
        
        for q in quiz:
            user_ans = user_answers.get(str(q["id"]), "").strip().upper()
            
            if q.get("type") == "mcq":
                correct = q["answer"].upper()
                if user_ans == correct:
                    score += 1
                else:
                    correct_option = q["options"].get(correct, "Unknown")
                    user_option = q["options"].get(user_ans, user_ans) if user_ans else "No answer"
                    fb = await self.call_llm(
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
                    fb = await self.call_llm(
                        f"Explain why '{user_ans}' is wrong for '{q['question']}'. Correct is '{q['answer']}'.",
                        max_tokens=100,
                    )
                    feedback.append(f"Q{q['id']+1}: {fb}")
        
        final_score = score / len(quiz) if quiz else 0
        return final_score, "\n\n".join(feedback)

    def adjust_difficulty(self, current_level: str, score: float) -> str:
        if score > 0.8:
            return "advanced"
        elif score < 0.5:
            return "beginner"
        return current_level


# ✅ EXPORT INSTANCE
quiz_agent = QuizAgent()