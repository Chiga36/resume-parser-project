from models.company_matcher import CompanyMatcher
from preprocessing.feature_extractor import ResumeFeatureExtractor

sample_resume = """
John Doe - Software Engineer
john@example.com

EXPERIENCE
Software Engineer at Tech Company (2020-2023)
- Python, Java, Machine Learning, TensorFlow, Docker, Kubernetes

EDUCATION
Master of Technology in Computer Science

SKILLS
Python, Java, JavaScript, React, Machine Learning, 
TensorFlow, Docker, Kubernetes, AWS, Git
"""

# Extract features
extractor = ResumeFeatureExtractor()
features = extractor.extract_all_features(sample_resume)

# Match with companies
matcher = CompanyMatcher()
matches = matcher.get_all_company_matches(features)

print("✓ Company Match Results:")
print(f"  Total companies: {len(matches)}")
print("\n  Top 5 Matches:")
for i, match in enumerate(matches[:5], 1):
    print(f"  {i}. {match['company']}: {match['probability']}% ({match['confidence']} confidence)")

print("\n✓ Company Matcher is working!")
