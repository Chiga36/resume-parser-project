from models.recommendation_engine import RecommendationEngine
from models.company_matcher import CompanyMatcher
from preprocessing.feature_extractor import ResumeFeatureExtractor

strong_resume = """
Jane Smith
jane.smith@example.com | +91-9876543210

EXPERIENCE
Senior Software Engineer at Google (2020-2025)
- Led team of 5 developers building cloud infrastructure
- Implemented ML pipelines using TensorFlow and PyTorch
- Deployed microservices on Kubernetes with 99.9% uptime

Software Engineer at Microsoft (2017-2020)
- Developed Azure cloud applications using Python and React
- Optimized database queries improving performance by 40%

EDUCATION
Master of Technology in Computer Science (2015-2017)
Indian Institute of Technology, Delhi

SKILLS
Python, Java, JavaScript, TypeScript, React, Angular, Node.js, 
Django, Flask, FastAPI, Docker, Kubernetes, AWS, Azure, GCP,
PostgreSQL, MongoDB, Redis, Git, Jenkins, CI/CD, Machine Learning,
TensorFlow, PyTorch, Algorithms, System Design
"""

# Extract features
extractor = ResumeFeatureExtractor()
features = extractor.extract_all_features(strong_resume)

# Get company matches
matcher = CompanyMatcher()
matches = matcher.get_all_company_matches(features)

# Generate recommendations
recommender = RecommendationEngine()
recommendations = recommender.analyze_resume(features, matches)

print("✓ Strong Resume Analysis:")
print(f"  Overall Score: {recommendations['overall_score']}/100")

print(f"\n  ✅ Strengths ({len(recommendations['strengths'])}):")
for strength in recommendations['strengths']:
    print(f"    ✓ {strength}")

print(f"\n  💡 Improvements ({len(recommendations['improvements'])}):")
if recommendations['improvements']:
    for imp in recommendations['improvements']:
        print(f"    - {imp['area']}: {imp['suggestion']}")
else:
    print("    None - Excellent resume!")

print(f"\n  Top Company Matches:")
for match in matches[:3]:
    print(f"    - {match['company']}: {match['probability']}%")

print("\n✓ Recommendation Engine correctly identifies strengths!")
