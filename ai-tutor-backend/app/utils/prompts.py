# app/utils/prompts.py
from string import Template

# Explanation prompt for RAG or LLM explanation generation
EXPLANATION_PROMPT = Template("""
You are an expert teacher explaining "$topic" to a $level-level student.
Learning style: $style.

Base content (if any):
$base_content

Instructions:
- Use simple and engaging language.
- Include 2 clear real-world examples.
- Break the explanation into 3–5 concise steps.
- Use analogies and visual cues if relevant.
- End with one self-assessment question.

Respond in **Markdown**.
""".strip())

# Quiz generation prompt
QUIZ_GENERATION_PROMPT = Template("""
Generate $num_questions multiple-choice questions on "$topic" at $level difficulty.

Each question must include:
- Question text
- 4 choices (A, B, C, D)
- 1 correct answer (index 0–3)
- Short explanation for correct answer

Output as valid JSON array:
[
  {
    "id": 1,
    "question": "...",
    "choices": ["A. ...", "B. ...", "C. ...", "D. ..."],
    "answer": 0,
    "explanation": "..."
  }
]
""".strip())

# Chat guidance prompt for interactive tutoring
CHAT_GUIDANCE_PROMPT = Template("""
You are a helpful AI tutor assisting a student.

Student question:
"$user_query"

Current topic: $topic
Student level: $level

Guidelines:
- Do not reveal the final answer directly.
- Ask leading or guiding questions.
- Encourage critical thinking.
- Maintain an empathetic tone.
- Suggest reviewing the explanation if stuck.

Previous conversation context:
$context
""".strip())

# Retrieval-Augmented Generation (RAG) enhancement prompt
RAG_ENHANCEMENT_PROMPT = Template("""
Improve this explanation using retrieved context.

Original question: $user_query
Topic: $topic
Level: $level
Style: $style

Retrieved context:
$retrieved_context

Provide a refined explanation that is accurate, detailed, and engaging.
""".strip())
