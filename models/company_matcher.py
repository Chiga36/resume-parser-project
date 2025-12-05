import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List
import json
from pathlib import Path
from config import Config

class CompanyMatcher:
    """Match resumes with companies and calculate placement probability"""
    
    def __init__(self):
        self.config = Config()
        self.vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
        self.company_profiles = {}
        self.load_company_profiles()
    
    def load_company_profiles(self):
        """Load preprocessed company profiles"""
        profile_path = Path(self.config.COMPANY_PROFILES_DIR) / "company_profiles.json"
        
        if profile_path.exists():
            with open(profile_path, 'r') as f:
                self.company_profiles = json.load(f)
        else:
            print("Company profiles not found. Run data preprocessing first.")
    
    def create_company_profiles(self, jobs_df: pd.DataFrame):
        """Create company profiles from scraped job data"""
        profiles = {}
        
        for company in jobs_df['target_company'].unique():
            company_jobs = jobs_df[jobs_df['target_company'] == company]
            
            # Aggregate all job descriptions
            all_descriptions = ' '.join(company_jobs['description'].dropna().tolist())
            
            # Extract common requirements
            experience_levels = []
            
            for _, job in company_jobs.iterrows():
                if pd.notna(job.get('description')):
                    desc_lower = job['description'].lower()
                    
                    # Experience extraction
                    import re
                    exp_match = re.search(r'(\d+)\+?\s*(?:years?|yrs?)', desc_lower)
                    if exp_match:
                        experience_levels.append(int(exp_match.group(1)))
            
            profiles[company] = {
                'company_name': company,
                'job_count': len(company_jobs),
                'description_text': all_descriptions,
                'avg_experience_required': np.mean(experience_levels) if experience_levels else 2,
                'min_experience': np.min(experience_levels) if experience_levels else 0,
                'max_experience': np.max(experience_levels) if experience_levels else 5
            }
        
        # Save profiles
        Path(self.config.COMPANY_PROFILES_DIR).mkdir(parents=True, exist_ok=True)
        with open(Path(self.config.COMPANY_PROFILES_DIR) / "company_profiles.json", 'w') as f:
            json.dump(profiles, f, indent=2)
        
        self.company_profiles = profiles
        return profiles
    
    def calculate_match_score(self, resume_features: Dict, company_name: str) -> float:
        """Calculate match score between resume and company using cosine similarity"""
        
        if company_name not in self.company_profiles:
            return 0.0
        
        company_profile = self.company_profiles[company_name]
        
        # Create text representations
        resume_text = ' '.join(resume_features.get('skills', [])) + ' ' + \
                      ' '.join([pos[:100] for pos in resume_features.get('experience', {}).get('positions', [])])
        
        company_text = company_profile['description_text']
        
        if not resume_text or not company_text:
            return 0.0
        
        # Calculate TF-IDF and cosine similarity
        try:
            tfidf_matrix = self.vectorizer.fit_transform([resume_text, company_text])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except:
            return 0.0
    
    def calculate_placement_probability(self, resume_features: Dict, company_name: str) -> Dict:
        """Calculate comprehensive placement probability"""
        
        if company_name not in self.company_profiles:
            return {
                'company': company_name,
                'probability': 0.0,
                'factors': {},
                'message': 'Company profile not found'
            }
        
        company_profile = self.company_profiles[company_name]
        
        # Factor 1: Skills match (40% weight)
        skills_score = self.calculate_match_score(resume_features, company_name)
        
        # Factor 2: Experience match (30% weight)
        resume_exp = resume_features.get('experience', {}).get('total_years', 0)
        required_exp = company_profile.get('avg_experience_required', 2)
        
        if resume_exp >= required_exp:
            experience_score = 1.0
        elif resume_exp >= required_exp * 0.7:
            experience_score = 0.8
        elif resume_exp >= required_exp * 0.5:
            experience_score = 0.6
        else:
            experience_score = 0.3
        
        # Factor 3: Education level (20% weight)
        education_level = resume_features.get('education', {}).get('highest_level', 0)
        education_score = min(education_level / 5.0, 1.0)  # Normalize to max PhD level
        
        # Factor 4: Resume completeness (10% weight)
        completeness_score = min(
            (len(resume_features.get('skills', [])) / 10) * 0.5 +
            (min(resume_features.get('text_length', 0) / 2000, 1.0)) * 0.5,
            1.0
        )
        
        # Weighted final score
        final_probability = (
            skills_score * 0.4 +
            experience_score * 0.3 +
            education_score * 0.2 +
            completeness_score * 0.1
        )
        
        # Convert to percentage
        percentage = round(final_probability * 100, 1)
        
        return {
            'company': company_name,
            'probability': percentage,
            'factors': {
                'skills_match': round(skills_score * 100, 1),
                'experience_match': round(experience_score * 100, 1),
                'education_match': round(education_score * 100, 1),
                'completeness': round(completeness_score * 100, 1)
            },
            'required_experience': required_exp,
            'candidate_experience': resume_exp,
            'confidence': 'high' if percentage > 70 else 'medium' if percentage > 40 else 'low'
        }
    
    def get_all_company_matches(self, resume_features: Dict) -> List[Dict]:
        """Get placement probability for all companies"""
        results = []
        
        for company_name in self.company_profiles.keys():
            match_result = self.calculate_placement_probability(resume_features, company_name)
            results.append(match_result)
        
        # Sort by probability
        results.sort(key=lambda x: x['probability'], reverse=True)
        
        return results
