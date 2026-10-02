from fastapi import FastAPI, HTTPException, status

from schemas import (
    AnalyzeProfileRequest,
    AnalyzeProfileResponse,
    SkillGapRequest,
    SkillGapResponse,
    GapDetail,
    AnalyzeIssueRequest,
    AnalyzeIssueResponse,
    IssueAnalysisDetail,
    RecommendRequest,
    RecommendResponse
)

from services.profile_analyzer import analyze_repositories

from services.issue_analyzer import (
    extract_issue_features
)

from services.recommendation_engine import (
    calculate_recommendations
)


app = FastAPI(
    title="OpenSourceMentor ML Service",
    version="1.0.0",
    description="Internal ML microservice for profile analysis and issue matching"
)


@app.get("/health")
def health_check():

    return {
        "status": "ok",
        "service": "ML Engine"
    }


@app.post(
    "/ml/analyze-profile",
    response_model=AnalyzeProfileResponse
)
def analyze_profile(
    payload: AnalyzeProfileRequest
):

    try:

        skills = analyze_repositories(
            payload.repositories
        )

        return AnalyzeProfileResponse(
            success=True,
            skills=skills
        )

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile analysis failed: {str(e)}"
        )


@app.post(
    "/ml/skill-gap",
    response_model=SkillGapResponse
)
def skill_gap(
    payload: SkillGapRequest
):

    existing_skills = {
        s.name.lower()
        for s in payload.studentSkills
    }

    gaps = []

    for target in payload.targetSkills:

        target_lower = target.lower()

        if target_lower not in existing_skills:

            priority = (
                "high"
                if target_lower in [
                    "typescript",
                    "testing"
                ]
                else "medium"
            )

            gaps.append(
                GapDetail(
                    skill=target,
                    priority=priority
                )
            )

    return SkillGapResponse(
        success=True,
        gaps=gaps
    )


@app.post(
    "/ml/analyze-issue",
    response_model=AnalyzeIssueResponse
)
def analyze_issue(
    payload: AnalyzeIssueRequest
):

    techs, difficulty, concepts = extract_issue_features(
        payload.title,
        payload.description,
        payload.labels
    )

    if (
        not techs
        and payload.repository
        and payload.repository.language
    ):

        techs.append(
            payload.repository.language
        )

    return AnalyzeIssueResponse(
        success=True,
        analysis=IssueAnalysisDetail(
            technologies=techs,
            difficulty=difficulty,
            concepts=concepts
        )
    )


@app.post(
    "/ml/recommend",
    response_model=RecommendResponse
)
def recommend_issues(
    payload: RecommendRequest
):

    recommendations = calculate_recommendations(
        payload.student.skills,
        payload.issues
    )

    return RecommendResponse(
        success=True,
        recommendations=recommendations
    )


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )