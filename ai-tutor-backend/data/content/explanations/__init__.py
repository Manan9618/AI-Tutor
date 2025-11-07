"""
Explanation submodule for AI Tutor.
Handles storage and retrieval of generated explanations.
"""
from pathlib import Path

EXPLANATION_DIR = Path(__file__).resolve().parent
EXPLANATION_DIR.mkdir(parents=True, exist_ok=True)
