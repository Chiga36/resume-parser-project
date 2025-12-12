import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Scraping settings
    MAX_JOBS_PER_COMPANY = 50
    SCRAPE_SITES = ["indeed", "linkedin"]
    LOCATION = "India"
    HOURS_OLD = 720  # 30 days
    
    # Model paths
    SPACY_MODEL = "en_core_web_sm"
    DATA_DIR = "data"
    RAW_DATA_DIR = f"{DATA_DIR}/raw"
    PROCESSED_DATA_DIR = f"{DATA_DIR}/processed"
    RESUMES_DIR = f"{DATA_DIR}/resumes"
    COMPANY_PROFILES_DIR = f"{DATA_DIR}/company_profiles"
    # Add these lines to Config class
    # Metrics settings
    METRICS_DIR = f"{DATA_DIR}/metrics"
    METRICS_RETENTION_DAYS = 30
    ENABLE_PERFORMANCE_TRACKING = True

    
    # API settings
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    
    # Kaggle credentials (optional)
    KAGGLE_USERNAME = os.getenv("KAGGLE_USERNAME")
    KAGGLE_KEY = os.getenv("KAGGLE_KEY")
    
    # Company list for scraping
    TARGET_COMPANIES = [
        "Google", "Microsoft", "Amazon", "Apple", "Meta",
        "TCS", "Infosys", "Wipro", "Cognizant", "HCL",
        "Accenture", "Deloitte", "IBM", "Oracle"
    ]
    
    TARGET_ROLES = [
        "Software Engineer", "Data Scientist", "Full Stack Developer",
        "ML Engineer", "DevOps Engineer", "Backend Developer"
    ]
