"""
Data Content Package
Handles loading, writing, and indexing of study content
for the AI Tutor system.
"""
from pathlib import Path

BASE_CONTENT_DIR = Path(__file__).resolve().parent
EXPLANATION_DIR = BASE_CONTENT_DIR / "explanation"

# Ensure necessary folders exist
for path in [BASE_CONTENT_DIR, EXPLANATION_DIR]:
    path.mkdir(parents=True, exist_ok=True)
