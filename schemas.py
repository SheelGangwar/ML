from typing import Dict, List, Optional
from pydantic import BaseModel, Field

# Profile Analysis
class DependencyInfo(BaseModel):
    packageJson: Optional[Dict] = None
    requirementsTxt: Optional[Dict] = None
    pyprojectToml: Optional[Dict] = None

class RepoData(BaseModel):
    name: str
    languages: Dict[str, int] = Field(default_factory=dict)
    topics: List[str] = Field(default_factory=list)
    readme: Optional[str] = ""
    dependencies: Optional[DependencyInfo] = None

class AnalyzeProfileRequest(BaseModel):
    userId: str
    repositories: List[RepoData]

class SkillConfidence(BaseModel):
    name: str
    confidence: float

class AnalyzeProfileResponse(BaseModel):
    success: bool = True
    skills: List[SkillConfidence]

# Skill Gap
class SkillGapRequest(BaseModel):
    studentSkills: List[SkillConfidence]
    targetSkills: List[str]

class GapDetail(BaseModel):
    skill: str
    priority: str  # high, medium, low

class SkillGapResponse(BaseModel):
    success: bool = True
    gaps: List[GapDetail]

# Issue Analysis
class RepositoryInfo(BaseModel):
    name: str
    language: Optional[str] = None

class AnalyzeIssueRequest(BaseModel):
    issueId: str
    title: str
    description: Optional[str] = ""
    labels: List[str] = Field(default_factory=list)
    repository: Optional[RepositoryInfo] = None

class IssueAnalysisDetail(BaseModel):
    technologies: List[str]
    difficulty: str  # beginner, intermediate, advanced
    concepts: List[str]

class AnalyzeIssueResponse(BaseModel):
    success: bool = True
    analysis: IssueAnalysisDetail

# Recommendations
class StudentPayload(BaseModel):
    skills: List[SkillConfidence]

class CandidateIssue(BaseModel):
    id: str
    technologies: List[str]
    difficulty: str
    description: Optional[str] = ""

class RecommendRequest(BaseModel):
    student: StudentPayload
    issues: List[CandidateIssue]

class RecommendationItem(BaseModel):
    issueId: str
    score: float
    matchedSkills: List[str]
    missingSkills: List[str]
    reason: str

class RecommendResponse(BaseModel):
    success: bool = True
    recommendations: List[RecommendationItem]