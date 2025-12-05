from models.resume_validator import ResumeValidator

sample_resume = """
John Doe
Email: john.doe@example.com
Phone: +91-9876543210

EXPERIENCE
Software Engineer at Google (2020-2023)
- Developed web applications

EDUCATION
Bachelor of Technology in Computer Science (2016-2020)

SKILLS
Python, Java, React, Docker
"""

validator = ResumeValidator()
is_valid, details = validator.validate_text(sample_resume)

print("✓ Resume Validation Result:")
print(f"  Valid: {is_valid}")
print(f"  Confidence: {details['confidence']}")
print(f"  Sections Found: {details.get('sections_found', 0)}")
print(f"  Indicators Found: {details.get('indicators_found', 0)}")

print("\n✓ Resume Validator is working!")
