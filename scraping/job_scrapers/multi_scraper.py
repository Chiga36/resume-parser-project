from jobspy import scrape_jobs
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import Config

class JobScraper:
    def __init__(self):
        self.config = Config()
        Path(self.config.RAW_DATA_DIR).mkdir(parents=True, exist_ok=True)
        
    def scrape_jobs_by_company(self, company: str, roles: list):
        """Scrape jobs for a specific company across multiple roles"""
        all_jobs = []
        
        for role in roles:
            try:
                print(f"Scraping {role} positions at {company}...")
                jobs = scrape_jobs(
                    site_name=self.config.SCRAPE_SITES,
                    search_term=f"{role}",
                    location=self.config.LOCATION,
                    results_wanted=self.config.MAX_JOBS_PER_COMPANY,
                    hours_old=self.config.HOURS_OLD,
                    country_indeed='India',
                    linkedin_fetch_description=True,
                    company_name=company
                )
                
                if jobs is not None and not jobs.empty:
                    jobs['target_company'] = company
                    jobs['target_role'] = role
                    all_jobs.append(jobs)
                    print(f"Found {len(jobs)} jobs")
                    
            except Exception as e:
                print(f"Error scraping {company} - {role}: {str(e)}")
                continue
        
        if all_jobs:
            return pd.concat(all_jobs, ignore_index=True)
        return pd.DataFrame()
    
    def scrape_all_companies(self):
        """Scrape jobs for all target companies"""
        all_company_jobs = []
        
        for company in self.config.TARGET_COMPANIES:
            jobs_df = self.scrape_jobs_by_company(company, self.config.TARGET_ROLES)
            if not jobs_df.empty:
                all_company_jobs.append(jobs_df)
        
        if all_company_jobs:
            final_df = pd.concat(all_company_jobs, ignore_index=True)
            
            # Save raw data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"{self.config.RAW_DATA_DIR}/jobs_{timestamp}.csv"
            final_df.to_csv(output_path, index=False)
            print(f"Saved {len(final_df)} jobs to {output_path}")
            
            return final_df
        
        return pd.DataFrame()
    
    def extract_job_requirements(self, job_description: str):
        """Extract key requirements from job description"""
        requirements = {
            'skills': [],
            'experience_years': None,
            'education': [],
            'certifications': []
        }
        
        if pd.isna(job_description):
            return requirements
        
        desc_lower = job_description.lower()
        
        # Common tech skills
        tech_skills = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue',
            'node.js', 'django', 'flask', 'fastapi', 'sql', 'mongodb',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'git',
            'machine learning', 'deep learning', 'tensorflow', 'pytorch',
            'nlp', 'computer vision', 'data analysis', 'pandas', 'numpy'
        ]
        
        for skill in tech_skills:
            if skill in desc_lower:
                requirements['skills'].append(skill)
        
        # Extract experience years
        import re
        exp_patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience',
            r'experience\s*(?:of)?\s*(\d+)\+?\s*(?:years?|yrs?)'
        ]
        for pattern in exp_patterns:
            match = re.search(pattern, desc_lower)
            if match:
                requirements['experience_years'] = int(match.group(1))
                break
        
        # Education keywords
        education_keywords = ['bachelor', 'master', 'phd', 'b.tech', 'm.tech', 'mba']
        for edu in education_keywords:
            if edu in desc_lower:
                requirements['education'].append(edu)
        
        return requirements

if __name__ == "__main__":
    scraper = JobScraper()
    scraper.scrape_all_companies()