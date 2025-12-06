import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error, r2_score
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import Config
from preprocessing.feature_extractor import ResumeFeatureExtractor

class ModelTrainer:
    def __init__(self):
        self.config = Config()
        self.models_dir = Path("trained_models")
        self.models_dir.mkdir(exist_ok=True)
        self.feature_extractor = ResumeFeatureExtractor()
        
    def load_resume_dataset(self):
        """Load resume dataset from Kaggle"""
        resume_path = Path(self.config.RESUMES_DIR) / "Resume" / "Resume.csv"
        
        if not resume_path.exists():
            # Try alternate path
            resume_path = Path(self.config.RESUMES_DIR) / "Resume.csv"
        
        if not resume_path.exists():
            print("Resume dataset not found. Run: python run_pipeline.py --step download")
            return None
        
        df = pd.read_csv(resume_path)
        print(f"Loaded {len(df)} resumes")
        return df
    
    def extract_features_from_text(self, text):
        """Extract numerical features from resume text"""
        features = self.feature_extractor.extract_all_features(text)
        
        return {
            'skill_count': len(features['skills']),
            'experience_years': features['experience']['total_years'],
            'education_level': features['education']['highest_level'],
            'word_count': features['word_count'],
            'text_length': features['text_length'],
            'has_projects': 1 if 'project' in text.lower() else 0,
            'has_certifications': 1 if 'certification' in text.lower() or 'certified' in text.lower() else 0
        }
    
    def train_resume_classifier(self):
        """Train Model 1: Resume Quality Classifier"""
        print("\n" + "="*60)
        print("MODEL 1: Training Resume Quality Classifier")
        print("="*60)
        
        df = self.load_resume_dataset()
        if df is None:
            return
        
        # Extract features
        print("Extracting features...")
        features_list = []
        labels = []
        
        for idx, row in df.iterrows():
            if idx % 100 == 0:
                print(f"Processing resume {idx}/{len(df)}...")
            
            try:
                resume_text = str(row['Resume_str']) if 'Resume_str' in row else str(row['Resume'])
                features = self.extract_features_from_text(resume_text)
                
                # Create quality label based on features
                score = (
                    features['skill_count'] * 3 +
                    features['experience_years'] * 5 +
                    features['education_level'] * 4 +
                    features['has_projects'] * 5
                )
                
                if score >= 40:
                    label = 'Good'
                elif score >= 20:
                    label = 'Average'
                else:
                    label = 'Poor'
                
                features_list.append(list(features.values()))
                labels.append(label)
            except:
                continue
        
        # Prepare data
        X = np.array(features_list)
        y = np.array(labels)
        
        # Encode labels
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42
        )
        
        # Train model
        print("Training Random Forest Classifier...")
        model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n✅ Model trained successfully!")
        print(f"Accuracy: {accuracy:.2%}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=le.classes_))
        
        # Save model
        model_path = self.models_dir / "resume_classifier.pkl"
        encoder_path = self.models_dir / "label_encoder.pkl"
        
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        with open(encoder_path, 'wb') as f:
            pickle.dump(le, f)
        
        print(f"✅ Model saved to: {model_path}")
        
        return model, le
    
    def train_placement_predictor(self):
        """Train Model 2: Company Placement Probability Predictor"""
        print("\n" + "="*60)
        print("MODEL 2: Training Placement Probability Predictor")
        print("="*60)
        
        # Load cleaned job data
        jobs_path = Path(self.config.PROCESSED_DATA_DIR) / "jobs_cleaned.csv"
        
        if not jobs_path.exists():
            print("Cleaned job data not found. Run: python run_pipeline.py --step preprocess")
            return
        
        df_jobs = pd.read_csv(jobs_path)
        df_resumes = self.load_resume_dataset()
        
        if df_resumes is None:
            return
        
        print("Creating training dataset...")
        
        # Create synthetic training data
        X_train = []
        y_train = []
        
        # Sample resumes and match with companies
        for idx in range(min(500, len(df_resumes))):
            if idx % 50 == 0:
                print(f"Processing {idx}/500...")
            
            try:
                resume_text = str(df_resumes.iloc[idx]['Resume_str']) if 'Resume_str' in df_resumes.columns else str(df_resumes.iloc[idx]['Resume'])
                features = self.extract_features_from_text(resume_text)
                
                # Simulate different companies
                for company_exp_req in [0, 2, 3, 5]:
                    feature_vector = [
                        features['skill_count'],
                        features['experience_years'],
                        features['education_level'],
                        features['word_count'] / 1000,
                        company_exp_req,  # Company's required experience
                        features['has_projects'],
                        features['has_certifications']
                    ]
                    
                    # Calculate synthetic probability
                    skill_match = min(features['skill_count'] / 15, 1.0) * 40
                    exp_match = (1.0 if features['experience_years'] >= company_exp_req else 0.6) * 30
                    edu_match = min(features['education_level'] / 5, 1.0) * 20
                    complete_match = min(features['word_count'] / 800, 1.0) * 10
                    
                    probability = skill_match + exp_match + edu_match + complete_match
                    
                    X_train.append(feature_vector)
                    y_train.append(probability)
            except:
                continue
        
        X_train = np.array(X_train)
        y_train = np.array(y_train)
        
        # Split data
        X_train_split, X_test, y_train_split, y_test = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42
        )
        
        # Train Gradient Boosting model
        print("Training Gradient Boosting Regressor...")
        model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        model.fit(X_train_split, y_train_split)
        
        # Evaluate
        y_pred = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        print(f"\n✅ Model trained successfully!")
        print(f"RMSE: {rmse:.2f}")
        print(f"R² Score: {r2:.2%}")
        
        # Save model
        model_path = self.models_dir / "placement_predictor.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        print(f"✅ Model saved to: {model_path}")
        
        return model
    
    def train_skill_recommender(self):
        """Train Model 3: Skill Co-occurrence Matrix for Recommendations"""
        print("\n" + "="*60)
        print("MODEL 3: Training Skill Recommendation System")
        print("="*60)
        
        df = self.load_resume_dataset()
        if df is None:
            return
        
        # Extract all skills from resumes
        print("Extracting skills from all resumes...")
        all_skills = []
        
        for idx, row in df.iterrows():
            if idx % 100 == 0:
                print(f"Processing resume {idx}/{len(df)}...")
            
            try:
                resume_text = str(row['Resume_str']) if 'Resume_str' in row else str(row['Resume'])
                features = self.feature_extractor.extract_all_features(resume_text)
                all_skills.append(set(features['skills']))
            except:
                continue
        
        # Create skill co-occurrence matrix
        unique_skills = set()
        for skills in all_skills:
            unique_skills.update(skills)
        
        unique_skills = list(unique_skills)
        skill_matrix = np.zeros((len(unique_skills), len(unique_skills)))
        
        print("Building co-occurrence matrix...")
        for skills in all_skills:
            skill_list = list(skills)
            for i, skill1 in enumerate(skill_list):
                idx1 = unique_skills.index(skill1)
                for skill2 in skill_list[i+1:]:
                    idx2 = unique_skills.index(skill2)
                    skill_matrix[idx1][idx2] += 1
                    skill_matrix[idx2][idx1] += 1
        
        # Save skill recommender
        recommender_data = {
            'skills': unique_skills,
            'matrix': skill_matrix
        }
        
        model_path = self.models_dir / "skill_recommender.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(recommender_data, f)
        
        print(f"\n✅ Skill recommender trained!")
        print(f"Total unique skills: {len(unique_skills)}")
        print(f"✅ Model saved to: {model_path}")
        
        return recommender_data
    
    def train_all_models(self):
        """Train all models"""
        print("\n" + "="*70)
        print("STARTING ML MODEL TRAINING PIPELINE")
        print("="*70)
        
        # Train all models
        self.train_resume_classifier()
        self.train_placement_predictor()
        self.train_skill_recommender()
        
        print("\n" + "="*70)
        print("✅ ALL MODELS TRAINED SUCCESSFULLY!")
        print("="*70)
        print(f"\nModels saved in: {self.models_dir}/")
        print("Models:")
        print("  1. resume_classifier.pkl")
        print("  2. label_encoder.pkl")
        print("  3. placement_predictor.pkl")
        print("  4. skill_recommender.pkl")

if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.train_all_models()
