import spacy
import re
from typing import Dict, List
from config import Config

class ResumeFeatureExtractor:
    def __init__(self):
        self.config = Config()
        try:
            self.nlp = spacy.load(self.config.SPACY_MODEL)
        except:
            print(f"Downloading spaCy model: {self.config.SPACY_MODEL}")
            import os
            os.system(f"python -m spacy download {self.config.SPACY_MODEL}")
            self.nlp = spacy.load(self.config.SPACY_MODEL)
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from resume"""
        skills_database = {
            'languages': ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'go', 'rust', 'php', 'swift', 'kotlin', 'typescript'],
            'frameworks': ['django', 'flask', 'fastapi', 'react', 'angular', 'vue', 'node.js', 'express', 'spring', 'asp.net'],
            'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra', 'dynamodb', 'oracle'],
            'cloud': ['aws', 'azure', 'gcp', 'heroku', 'digitalocean'],
            'devops': ['docker', 'kubernetes', 'jenkins', 'gitlab ci', 'github actions', 'terraform', 'ansible'],
            'ml_ai': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'nlp', 'computer vision', 'opencv'],
            'data': ['pandas', 'numpy', 'matplotlib', 'seaborn', 'tableau', 'power bi', 'spark', 'hadoop'],
            'tools': ['git', 'jira', 'confluence', 'postman', 'vs code', 'jupyter']
        }
        
        found_skills = []
        text_lower = text.lower()
        
        for category, skills in skills_database.items():
            for skill in skills:
                if skill in text_lower:
                    found_skills.append(skill)
        
        return list(set(found_skills))
    
    def extract_experience(self, text: str) -> Dict:
        """Extract work experience details"""
        experience = {
            'total_years': 0,
            'positions': []
        }
        
        # Extract year ranges
        year_pattern = r'(20\d{2}|19\d{2})\s*[-–]\s*(20\d{2}|19\d{2}|present|current)'
        matches = re.findall(year_pattern, text.lower())
        
        total_months = 0
        for start, end in matches:
            try:
                start_year = int(start)
                end_year = 2025 if 'present' in end or 'current' in end else int(end)
                total_months += (end_year - start_year) * 12
            except:
                continue
        
        experience['total_years'] = round(total_months / 12, 1)
        
        # Extract job titles
        job_titles = ['engineer', 'developer', 'analyst', 'scientist', 'manager', 'consultant', 'architect', 'designer']
        doc = self.nlp(text)
        
        for sent in doc.sents:
            sent_lower = sent.text.lower()
            for title in job_titles:
                if title in sent_lower:
                    experience['positions'].append(sent.text.strip()[:100])
                    break
        
        return experience
    
    def extract_education(self, text: str) -> List[Dict]:
        """Extract education details"""
        education = []
        
        degrees = {
            'phd': 5,
            'ph.d': 5,
            'doctorate': 5,
            'master': 4,
            'm.tech': 4,
            'mtech': 4,
            'm.s': 4,
            'mba': 4,
            'bachelor': 3,
            'b.tech': 3,
            'btech': 3,
            'b.e': 3,
            'b.s': 3,
            'diploma': 2
        }
        
        text_lower = text.lower()
        highest_level = 0
        
        for degree, level in degrees.items():
            if degree in text_lower:
                education.append({
                    'degree': degree,
                    'level': level
                })
                highest_level = max(highest_level, level)
        
        return {
            'degrees': education,
            'highest_level': highest_level
        }
    
    def extract_all_features(self, text: str) -> Dict:
        """Extract all features from resume"""
        return {
            'skills': self.extract_skills(text),
            'experience': self.extract_experience(text),
            'education': self.extract_education(text),
            'text_length': len(text),
            'word_count': len(text.split())
        }
