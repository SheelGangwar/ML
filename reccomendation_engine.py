import re
from typing import List
from schemas import CandidateIssue, RecommendationItem, SkillConfidence

BEGINNER_LABELS = {"good first issue", "easy", "beginner", "starter", "first-timers-only"}
ADVANCED_LABELS = {"architectural", "performance", "breaking-change", "complex"}

def extract_issue_features(title: str, description: str, labels: List[str]):
    text = f"{title} {description}".lower()
    
    # 1. Infer difficulty level
    label_set = {l.lower() for l in labels}
    if label_set.intersection(BEGINNER_LABELS):
        difficulty = "beginner"
    elif label_set.intersection(ADVANCED_LABELS):
        difficulty = "advanced"
    else:
        difficulty = "intermediate"

    # 2. Extract key technologies
    tech_keywords = {
        "react": "React", "javascript": "JavaScript", "typescript": "TypeScript",
        "css": "CSS", "html": "HTML", "node": "Node.js", "express": "Express",
        "mongodb": "MongoDB", "python": "Python", "fastapi": "FastAPI"
    }
    found_techs = set()
    for kw, display_name in tech_keywords.items():
        if re.search(r'\b' + re.escape(kw) + r'\b', text):
            found_techs.add(display_name)

    # 3. Extract concepts
    concepts = []
    if "responsive" in text or "navbar" in text or "layout" in text:
        concepts.append("responsive design")
    if "api" in text or "endpoint" in text:
        concepts.append("REST API")
    if "auth" in text or "jwt" in text:
        concepts.append("Authentication")

    return list(found_techs), difficulty, concepts

def calculate_recommendations(
    student_skills: List[SkillConfidence], 
    issues: List[CandidateIssue]
) -> List[RecommendationItem]:
    user_skill_map = {s.name.lower(): s.confidence for s in student_skills}
    recommendations = []

    for issue in issues:
        issue_techs = [t.lower() for t in issue.technologies]
        if not issue_techs:
            continue

        matched = []
        missing = []
        total_confidence = 0.0

        for tech in issue.technologies:
            tech_lower = tech.lower()
            if tech_lower in user_skill_map:
                matched.append(tech)
                total_confidence += user_skill_map[tech_lower]
            else:
                missing.append(tech)

        # Match Ratio (60%) + Skill Confidence Weight (40%)
        coverage_ratio = len(matched) / len(issue.technologies)
        avg_confidence = (total_confidence / len(matched)) if matched else 0.0
        match_score = round((coverage_ratio * 0.60) + (avg_confidence * 0.40), 2)

        # Reason generator
        if matched and missing:
            reason = f"Matches your experience in {', '.join(matched)}. You may need to learn {', '.join(missing)}."
        elif matched:
            reason = f"Strong technology overlap with your GitHub-derived skills ({', '.join(matched)})."
        else:
            reason = f"Good entry opportunity to learn {', '.join(missing)}."

        recommendations.append(
            RecommendationItem(
                issueId=issue.id,
                score=match_score,
                matchedSkills=matched,
                missingSkills=missing,
                reason=reason
            )
        )

    # Sort descending by suitability score
    recommendations.sort(key=lambda x: x.score, reverse=True)
    return recommendations