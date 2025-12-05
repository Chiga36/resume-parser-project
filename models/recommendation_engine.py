from typing import Dict, List

class RecommendationEngine:
    """Generate recommendations to improve resume"""
    
    def __init__(self):
        self.skill_categories = {
            'languages': ['Python', 'Java', 'JavaScript', 'C++', 'Go', 'TypeScript'],
            'frameworks': ['React', 'Django', 'FastAPI', 'Node.js', 'Spring Boot'],
            'cloud': ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes'],
            'databases': ['SQL', 'PostgreSQL', 'MongoDB', 'Redis'],
            'tools': ['Git', 'CI/CD', 'Jira', 'Jenkins']
        }
    
    def analyze_resume(self, resume_features: Dict, company_matches: List[Dict]) -> Dict:
        """Generate comprehensive recommendations"""
        
        recommendations = {
            'overall_score': 0,
            'strengths': [],
            'improvements': [],
            'missing_skills': [],
            'format_suggestions': [],
            'priority': 'high'
        }
        
        # Calculate overall score
        skills_count = len(resume_features.get('skills', []))
        experience_years = resume_features.get('experience', {}).get('total_years', 0)
        education_level = resume_features.get('education', {}).get('highest_level', 0)
        word_count = resume_features.get('word_count', 0)
        
        overall_score = min(
            (skills_count / 15) * 30 +
            (min(experience_years / 5, 1.0)) * 30 +
            (education_level / 5) * 20 +
            (min(word_count / 800, 1.0)) * 20,
            100
        )
        
        recommendations['overall_score'] = round(overall_score, 1)
        
        # Identify strengths
        if skills_count >= 10:
            recommendations['strengths'].append(f"Strong technical skill set with {skills_count} identified skills")
        
        if experience_years >= 3:
            recommendations['strengths'].append(f"Solid work experience of {experience_years} years")
        
        if education_level >= 4:
            recommendations['strengths'].append("Advanced education qualification")
        
        # Generate improvement suggestions
        if skills_count < 8:
            recommendations['improvements'].append({
                'area': 'Technical Skills',
                'suggestion': 'Add more technical skills relevant to your target role',
                'impact': 'High',
                'priority': 1
            })
        
        if experience_years < 2:
            recommendations['improvements'].append({
                'area': 'Experience',
                'suggestion': 'Highlight internships, projects, or freelance work to demonstrate practical experience',
                'impact': 'High',
                'priority': 1
            })
        
        if word_count < 500:
            recommendations['improvements'].append({
                'area': 'Resume Length',
                'suggestion': 'Expand your resume with more details about achievements and responsibilities',
                'impact': 'Medium',
                'priority': 2
            })
        
        # Find missing skills based on top company matches
        if company_matches:
            current_skills = set([s.lower() for s in resume_features.get('skills', [])])
            
            suggested_skills = set()
            for category, skills in self.skill_categories.items():
                for skill in skills:
                    if skill.lower() not in current_skills:
                        suggested_skills.add(skill)
            
            recommendations['missing_skills'] = list(suggested_skills)[:10]
        
        # Format suggestions
        if not resume_features.get('skills'):
            recommendations['format_suggestions'].append(
                "Add a dedicated 'Skills' section to highlight your technical expertise"
            )
        
        if experience_years == 0:
            recommendations['format_suggestions'].append(
                "Include an 'Experience' section with relevant projects, internships, or volunteer work"
            )
        
        recommendations['format_suggestions'].extend([
            "Use action verbs (developed, implemented, led) to describe accomplishments",
            "Quantify achievements with metrics (e.g., 'Improved performance by 30%')",
            "Keep formatting consistent throughout the document",
            "Ensure contact information is clearly visible at the top"
        ])
        
        return recommendations
