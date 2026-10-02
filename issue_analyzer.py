import re
from typing import List


BEGINNER_LABELS = {
    "good first issue",
    "easy",
    "beginner",
    "starter",
    "first-timers-only"
}

ADVANCED_LABELS = {
    "architectural",
    "performance",
    "breaking-change",
    "complex"
}


def extract_issue_features(
    title: str,
    description: str,
    labels: List[str]
):
    text = f"{title} {description}".lower()

    label_set = {l.lower() for l in labels}

    if label_set.intersection(BEGINNER_LABELS):
        difficulty = "beginner"
    elif label_set.intersection(ADVANCED_LABELS):
        difficulty = "advanced"
    else:
        difficulty = "intermediate"

    tech_keywords = {
        "react": "React",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "css": "CSS",
        "html": "HTML",
        "node": "Node.js",
        "express": "Express",
        "mongodb": "MongoDB",
        "python": "Python",
        "fastapi": "FastAPI"
    }

    found_techs = set()

    for kw, display_name in tech_keywords.items():
        if re.search(r'\b' + re.escape(kw) + r'\b', text):
            found_techs.add(display_name)

    concepts = []

    if "responsive" in text or "navbar" in text or "layout" in text:
        concepts.append("responsive design")

    if "api" in text or "endpoint" in text:
        concepts.append("REST API")

    if "auth" in text or "jwt" in text:
        concepts.append("Authentication")

    return list(found_techs), difficulty, concepts