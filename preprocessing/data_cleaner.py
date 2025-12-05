import pandas as pd
import json
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import Config
from models.company_matcher import CompanyMatcher

class DataPreprocessor:
    def __init__(self):
        self.config = Config()
    
    def clean_job_data(self, input_csv: str):
        """Clean and preprocess scraped job data"""
        print(f"Loading job data from {input_csv}...")
        df = pd.read_csv(input_csv)
        
        print(f"Original data: {len(df)} rows")
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['title', 'company', 'description'])
        
        # Remove rows with missing descriptions
        df = df.dropna(subset=['description'])
        
        # Clean text
        df['description'] = df['description'].str.replace('\n', ' ')
        df['description'] = df['description'].str.replace('\r', ' ')
        df['description'] = df['description'].str.strip()
        
        # Filter out very short descriptions
        df = df[df['description'].str.len() > 100]
        
        print(f"Cleaned data: {len(df)} rows")
        
        # Save cleaned data
        output_path = f"{self.config.PROCESSED_DATA_DIR}/jobs_cleaned.csv"
        Path(self.config.PROCESSED_DATA_DIR).mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Saved cleaned data to {output_path}")
        
        return df
    
    def create_company_profiles_from_data(self, cleaned_csv: str):
        """Create company profiles from cleaned job data"""
        df = pd.read_csv(cleaned_csv)
        
        matcher = CompanyMatcher()
        profiles = matcher.create_company_profiles(df)
        
        print(f"Created profiles for {len(profiles)} companies")
        return profiles

if __name__ == "__main__":
    preprocessor = DataPreprocessor()
    
    # Find the latest raw data file
    raw_files = list(Path(Config.RAW_DATA_DIR).glob("jobs_*.csv"))
    if raw_files:
        latest_file = max(raw_files, key=lambda x: x.stat().st_mtime)
        print(f"Processing {latest_file}")
        
        # Clean data
        cleaned_df = preprocessor.clean_job_data(str(latest_file))
        
        # Create company profiles
        profiles = preprocessor.create_company_profiles_from_data(
            f"{Config.PROCESSED_DATA_DIR}/jobs_cleaned.csv"
        )
    else:
        print("No raw data files found. Run scraping first.")
