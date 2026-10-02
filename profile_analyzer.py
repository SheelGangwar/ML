import re
from typing import Dict, List
from schemas import RepoData, SkillConfidence

KNOWN_FRAMEWORKS = {
    "react": "React",
    "express": "Express",
    "mongoose": "MongoDB",
    "mongodb": "MongoDB",
    "socket.io": "Socket.IO",
    "next": "Next.js",
    "vue": "Vue.js",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "tailwindcss": "Tailwind CSS",
    "typescript": "TypeScript"
}

def analyze_repositories(repositories: List[RepoData]) -> List[SkillConfidence]:
    skill_scores: Dict[str, float] = {}

    for repo in repositories:
        # 1. Byte ratio calculation for languages
        total_bytes = sum(repo.languages.values()) if repo.languages else 0
        if total_bytes > 0:
            for lang, bytes_cnt in repo.languages.items():
                ratio = bytes_cnt / total_bytes
                skill_scores[lang] = skill_scores.get(lang, 0.0) + (ratio * 1.5)

        # 2. GitHub Topics extraction
        for topic in repo.topics:
            normalized = topic.lower()
            canonical_name = KNOWN_FRAMEWORKS.get(normalized, topic.capitalize())
            skill_scores[canonical_name] = skill_scores.get(canonical_name, 0.0) + 1.2

        # 3. Package Dependencies parsing
        if repo.dependencies and repo.dependencies.packageJson:
            deps = repo.dependencies.packageJson.get("dependencies", {})
            dev_deps = repo.dependencies.packageJson.get("devDependencies", {})
            all_deps = {**deps, **dev_deps}

            for pkg in all_deps.keys():
                clean_pkg = pkg.replace("@", "").split("/")[0].lower()
                if clean_pkg in KNOWN_FRAMEWORKS:
                    canonical = KNOWN_FRAMEWORKS[clean_pkg]
                    skill_scores[canonical] = skill_scores.get(canonical, 0.0) + 1.8

    if not skill_scores:
        return []

    # Normalize scores into a confidence range [0.5, 0.98]
    max_score = max(skill_scores.values())
    results = []
    for skill, raw_score in skill_scores.items():
        confidence = round(0.50 + (raw_score / max_score) * 0.48, 2)
        results.append(SkillConfidence(name=skill, confidence=min(confidence, 0.98)))

    # Sort descending by confidence
    results.sort(key=lambda x: x.confidence, reverse=True)
    return results