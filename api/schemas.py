from pydantic import BaseModel
from typing import List, Dict, Optional

class ResumeValidationResponse(BaseModel):
    is_valid: bool
    confidence: float
    message: str
    details: Optional[Dict] = None
    suggestions: Optional[List[str]] = None

class CompanyMatchResult(BaseModel):
    company: str
    probability: float
    factors: Dict[str, float]
    confidence: str
    required_experience: float
    candidate_experience: float

class RecommendationResponse(BaseModel):
    overall_score: float
    strengths: List[str]
    improvements: List[Dict]
    missing_skills: List[str]
    format_suggestions: List[str]

class ResumeAnalysisResponse(BaseModel):
    validation: ResumeValidationResponse
    features: Dict
    company_matches: List[CompanyMatchResult]
    recommendations: RecommendationResponse
    top_3_companies: List[Dict]