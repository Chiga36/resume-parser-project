from preprocessing.feature_extractor import ResumeFeatureExtractor

sample_resume = """
John Doe
john@example.com | +91-9876543210

EXPERIENCE
Software Engineer at Google (2020-2023)
- Developed applications using Python, React, and Docker
- Implemented machine learning models with TensorFlow

Full Stack Developer at Microsoft (2018-2020)
- Built cloud applications on Azure
- Used Node.js and MongoDB

EDUCATION
Bachelor of Technology in Computer Science (2014-2018)

SKILLS
Python, Java, JavaScript, React, Angular, Docker, Kubernetes, 
AWS, Machine Learning, TensorFlow, Git, SQL, MongoDB
"""

extractor = ResumeFeatureExtractor()
print("Loading spaCy model...")
features = extractor.extract_all_features(sample_resume)

print("✓ Extracted Features:")
print(f"  Skills: {features['skills'][:10]}... ({len(features['skills'])} total)")
print(f"  Experience: {features['experience']['total_years']} years")
print(f"  Positions: {features['experience']['positions'][:3]}")
print(f"  Education Level: {features['education']['highest_level']}")
print(f"  Word Count: {features['word_count']}")

print("\n✓ Feature Extractor with spaCy is working!")
