"""
Loads educational content (text, markdown, etc.)
for processing by AI Tutor agents.
"""
import json
from pathlib import Path
from typing import Dict, List, Optional

CONTENT_DIR = Path(__file__).resolve().parent

def load_text_files() -> List[str]:
    """Load all .txt files in the content directory."""
    texts = []
    for file in CONTENT_DIR.glob("*.txt"):
        with open(file, "r", encoding="utf-8") as f:
            texts.append(f.read())
    return texts

def load_metadata() -> Dict:
    """Load metadata from JSON file if available."""
    metadata_path = CONTENT_DIR / "metadata.json"
    if metadata_path.exists():
        with open(metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def get_content_by_id(content_id: str) -> Optional[str]:
    """Retrieve specific content by ID from metadata."""
    metadata = load_metadata()
    entry = metadata.get(content_id)
    if not entry:
        return None

    file_path = CONTENT_DIR / entry.get("filename", "")
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return None
