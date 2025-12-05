from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from models.resume_validator import ResumeValidator
from models.company_matcher import CompanyMatcher
from models.recommendation_engine import RecommendationEngine
from preprocessing.pdf_parser import PDFParser
from preprocessing.feature_extractor import ResumeFeatureExtractor
from api.schemas import *
from config import Config

app = FastAPI(
    title="Resume Parser & Company Matcher API",
    description="AI-powered resume analysis with company placement predictions",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
config = Config()
validator = ResumeValidator()
matcher = CompanyMatcher()
recommender = RecommendationEngine()
feature_extractor = ResumeFeatureExtractor()

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/")
async def root():
    return {
        "message": "Resume Parser API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/api/analyze",
            "validate": "/api/validate-only",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "companies_loaded": len(matcher.company_profiles)
    }

@app.post("/api/analyze")
async def analyze_resume(file: UploadFile = File(...)):
    """
    Analyze uploaded resume PDF
    - Validates if file is a resume
    - Extracts features
    - Calculates company match probabilities
    - Provides improvement recommendations
    """
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    # Save uploaded file
    file_path = UPLOAD_DIR / file.filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    try:
        # Step 1: Validate resume
        is_valid, validation_details = validator.validate_resume(str(file_path))
        
        if not is_valid:
            return JSONResponse(
                status_code=400,
                content={
                    "validation": {
                        "is_valid": False,
                        "confidence": validation_details['confidence'],
                        "message": validation_details['reason'],
                        "suggestions": validation_details.get('suggestions', [])
                    }
                }
            )
        
        # Step 2: Extract text and features
        resume_text = PDFParser.extract_text(str(file_path))
        resume_features = feature_extractor.extract_all_features(resume_text)
        
        # Step 3: Calculate company matches
        company_matches = matcher.get_all_company_matches(resume_features)
        
        # Step 4: Generate recommendations
        recommendations = recommender.analyze_resume(resume_features, company_matches)
        
        # Prepare response
        response = {
            "validation": {
                "is_valid": True,
                "confidence": validation_details['confidence'],
                "message": "Valid resume detected",
                "details": validation_details
            },
            "features": {
                "skills": resume_features['skills'],
                "experience_years": resume_features['experience']['total_years'],
                "education_level": resume_features['education']['highest_level'],
                "word_count": resume_features['word_count']
            },
            "company_matches": company_matches[:10],  # Top 10
            "recommendations": recommendations,
            "top_3_companies": [
                {
                    "company": m['company'],
                    "probability": m['probability'],
                    "confidence": m['confidence']
                }
                for m in company_matches[:3]
            ]
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
    finally:
        # Cleanup
        if file_path.exists():
            file_path.unlink()

@app.post("/api/validate-only")
async def validate_only(file: UploadFile = File(...)):
    """Quick validation endpoint"""
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files supported")
    
    file_path = UPLOAD_DIR / file.filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        is_valid, details = validator.validate_resume(str(file_path))
        
        return {
            "is_valid": is_valid,
            "confidence": details['confidence'],
            "details": details
        }
    
    finally:
        if file_path.exists():
            file_path.unlink()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
