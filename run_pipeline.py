"""
Main pipeline script to run the complete workflow
"""
import sys
from pathlib import Path
import subprocess

def run_scraping():
    """Run job scraping"""
    print("\n" + "="*50)
    print("STEP 1: Running Job Scraping")
    print("="*50 + "\n")
    
    from scraping.job_scrapers.multi_scraper import JobScraper
    scraper = JobScraper()
    scraper.scrape_all_companies()

def download_resumes():
    """Download resume datasets"""
    print("\n" + "="*50)
    print("STEP 2: Downloading Resume Datasets")
    print("="*50 + "\n")
    
    from scraping.resume_scrapers.kaggle_datasets import ResumeDatasetDownloader
    downloader = ResumeDatasetDownloader()
    downloader.download_resume_dataset()
    downloader.download_ner_dataset()

def preprocess_data():
    """Clean and preprocess data"""
    print("\n" + "="*50)
    print("STEP 3: Preprocessing Data")
    print("="*50 + "\n")
    
    from preprocessing.data_cleaner import DataPreprocessor
    preprocessor = DataPreprocessor()
    
    from config import Config
    raw_files = list(Path(Config.RAW_DATA_DIR).glob("jobs_*.csv"))
    if raw_files:
        latest_file = max(raw_files, key=lambda x: x.stat().st_mtime)
        print(f"Processing {latest_file}")
        cleaned_df = preprocessor.clean_job_data(str(latest_file))
        preprocessor.create_company_profiles_from_data(
            f"{Config.PROCESSED_DATA_DIR}/jobs_cleaned.csv"
        )
    else:
        print("No raw data found! Run scraping first.")

def start_api():
    """Start FastAPI server"""
    print("\n" + "="*50)
    print("STEP 4: Starting API Server")
    print("="*50 + "\n")
    
    subprocess.run([
        "python", "-m", "uvicorn",
        "api.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
    ])

def start_frontend():
    """Start Streamlit frontend"""
    print("\n" + "="*50)
    print("STEP 5: Starting Frontend")
    print("="*50 + "\n")
    
    subprocess.run([
        "streamlit",
        "run",
        "frontend/app.py",
        "--server.port", "8501"
    ])

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Resume Parser Pipeline")
    parser.add_argument(
        '--step',
        choices=['scrape', 'download', 'preprocess', 'api', 'frontend', 'all'],
        default='all',
        help='Which step to run'
    )
    
    args = parser.parse_args()
    
    if args.step == 'scrape' or args.step == 'all':
        run_scraping()
    
    if args.step == 'download' or args.step == 'all':
        download_resumes()
    
    if args.step == 'preprocess' or args.step == 'all':
        preprocess_data()
    
    if args.step == 'api':
        start_api()
    
    if args.step == 'frontend':
        start_frontend()
    
    if args.step == 'all':
        print("\n" + "="*50)
        print("Data pipeline complete!")
        print("Now run: python run_pipeline.py --step api")
        print("Then in another terminal: python run_pipeline.py --step frontend")
        print("="*50 + "\n")
