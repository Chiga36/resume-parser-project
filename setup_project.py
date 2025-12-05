from pathlib import Path

# Create all directories
dirs = [
    'api', 'frontend', 'models', 'preprocessing', 'scraping', 'tests',
    'scraping/job_scrapers', 'scraping/resume_scrapers',
    'data/raw', 'data/processed', 'data/resumes', 'data/company_profiles',
    'uploads'
]

for dir_path in dirs:
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    print(f"✓ Created {dir_path}/")

# Create __init__.py files
init_files = [
    'api/__init__.py',
    'frontend/__init__.py',
    'models/__init__.py',
    'preprocessing/__init__.py',
    'scraping/__init__.py',
    'tests/__init__.py',
    'scraping/job_scrapers/__init__.py',
    'scraping/resume_scrapers/__init__.py'
]

for init_file in init_files:
    Path(init_file).touch()
    print(f"✓ Created {init_file}")

print("\n✅ Project structure created successfully!")
print("\nYour project structure:")
print("resume-parser-project/")
print("├── api/")
print("├── frontend/")
print("├── models/")
print("├── preprocessing/")
print("├── scraping/")
print("│   ├── job_scrapers/")
print("│   └── resume_scrapers/")
print("├── data/")
print("│   ├── raw/")
print("│   ├── processed/")
print("│   ├── resumes/")
print("│   └── company_profiles/")
print("└── uploads/")
