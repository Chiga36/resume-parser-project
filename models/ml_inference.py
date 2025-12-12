import pickle
import numpy as np
from pathlib import Path
from typing import Dict, List
from models.performance_tracker import performance_tracker
import time

class MLModelInference:
    """Use trained ML models for predictions"""
    
    def __init__(self):
        self.models_dir = Path("trained_models")
        self.load_models()
    
    def load_models(self):
        """Load all trained models"""
        try:
            with open(self.models_dir / "resume_classifier.pkl", 'rb') as f:
                self.resume_classifier = pickle.load(f)
            
            with open(self.models_dir / "label_encoder.pkl", 'rb') as f:
                self.label_encoder = pickle.load(f)
            
            with open(self.models_dir / "placement_predictor.pkl", 'rb') as f:
                self.placement_predictor = pickle.load(f)
            
            with open(self.models_dir / "skill_recommender.pkl", 'rb') as f:
                self.skill_recommender = pickle.load(f)
            
            print("✅ All ML models loaded successfully")
        except Exception as e:
            print(f"⚠️ Error loading models: {e}")
            self.resume_classifier = None
            self.placement_predictor = None
            self.skill_recommender = None
    
    def predict_resume_quality(self, features: Dict) -> Dict:
        """Predict resume quality using trained classifier"""
        start_time = time.time()
        
        if self.resume_classifier is None:
            return {"quality": "Unknown", "confidence": 0.0}
        
        # Prepare feature vector
        feature_vector = np.array([[
            features.get('skill_count', 0),
            features.get('experience_years', 0),
            features.get('education_level', 0),
            features.get('word_count', 0),
            features.get('text_length', 0),
            features.get('has_projects', 0),
            features.get('has_certifications', 0)
        ]])
        
        # Predict
        prediction = self.resume_classifier.predict(feature_vector)[0]
        probabilities = self.resume_classifier.predict_proba(feature_vector)[0]
        
        quality = self.label_encoder.inverse_transform([prediction])[0]
        confidence = float(max(probabilities))
        
        # Track performance
        prediction_time = time.time() - start_time
        performance_tracker.track_ml_prediction(
            'resume_classifier', 
            confidence, 
            prediction_time
        )
        
        return {
            "quality": quality,
            "confidence": confidence,
            "probabilities": {
                label: float(prob)
                for label, prob in zip(self.label_encoder.classes_, probabilities)
            }
        }
    
    def predict_placement_probability(self, features: Dict, company_exp_required: float) -> float:
        """Predict placement probability using trained model"""
        start_time = time.time()
        
        if self.placement_predictor is None:
            return 0.0
        
        # Prepare feature vector
        feature_vector = np.array([[
            features.get('skill_count', 0),
            features.get('experience_years', 0),
            features.get('education_level', 0),
            features.get('word_count', 0) / 1000,
            company_exp_required,
            features.get('has_projects', 0),
            features.get('has_certifications', 0)
        ]])
        
        # Predict
        probability = self.placement_predictor.predict(feature_vector)[0]
        probability = float(np.clip(probability, 0, 100))
        
        # Track performance
        prediction_time = time.time() - start_time
        performance_tracker.track_ml_prediction(
            'placement_predictor', 
            probability / 100, 
            prediction_time
        )
        
        # Clip to 0-100 range
        return probability
    
    def recommend_skills(self, current_skills: List[str], top_n: int = 5) -> List[str]:
        """Recommend skills based on co-occurrence"""
        if self.skill_recommender is None:
            return []
        
        skill_list = self.skill_recommender['skills']
        matrix = self.skill_recommender['matrix']
        
        # Find indices of current skills
        current_indices = []
        for skill in current_skills:
            skill_lower = skill.lower()
            for i, s in enumerate(skill_list):
                if s.lower() == skill_lower:
                    current_indices.append(i)
                    break
        
        if not current_indices:
            return []
        
        # Calculate recommendation scores
        scores = np.zeros(len(skill_list))
        for idx in current_indices:
            scores += matrix[idx]
        
        # Remove current skills
        for idx in current_indices:
            scores[idx] = 0
        
        # Get top N recommendations
        top_indices = np.argsort(scores)[::-1][:top_n]
        recommended = [skill_list[i] for i in top_indices if scores[i] > 0]
        
        return recommended

if __name__ == "__main__":
    # Test the models
    ml = MLModelInference()
    
    test_features = {
        'skill_count': 12,
        'experience_years': 3.5,
        'education_level': 3,
        'word_count': 650,
        'text_length': 3500,
        'has_projects': 1,
        'has_certifications': 1
    }
    
    print("\n=== Testing ML Models ===")
    
    # Test resume quality
    quality = ml.predict_resume_quality(test_features)
    print(f"\nResume Quality: {quality['quality']} (Confidence: {quality['confidence']:.2%})")
    
    # Test placement probability
    prob = ml.predict_placement_probability(test_features, company_exp_required=3.0)
    print(f"Placement Probability: {prob:.1f}%")
    
    # Test skill recommendations
    current_skills = ['python', 'javascript', 'react']
    recommendations = ml.recommend_skills(current_skills, top_n=5)
    print(f"Recommended Skills: {recommendations}")
