import os
from pathlib import Path
from dotenv import load_dotenv
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

# Load .env BEFORE importing kaggle
load_dotenv()

# Set Kaggle credentials from .env
os.environ['KAGGLE_USERNAME'] = os.getenv('KAGGLE_USERNAME', '')
os.environ['KAGGLE_KEY'] = os.getenv('KAGGLE_KEY', '')

# NOW import kaggle after setting env vars
import kaggle

from config import Config

class ResumeDatasetDownloader:
    def __init__(self):
        self.config = Config()
        Path(self.config.RESUMES_DIR).mkdir(parents=True, exist_ok=True)
    
    def download_resume_dataset(self):
        """Download resume datasets from Kaggle"""
        datasets = [
            'gauravduttakiit/resume-dataset',
            'snehaanbhawal/resume-dataset',
        ]
        
        for dataset in datasets:
            try:
                print(f"Downloading {dataset}...")
                kaggle.api.dataset_download_files(
                    dataset,
                    path=self.config.RESUMES_DIR,
                    unzip=True
                )
                print(f"✅ Successfully downloaded {dataset}")
            except Exception as e:
                print(f"❌ Error downloading {dataset}: {str(e)}")
    
    def download_ner_dataset(self):
        """Download NER training dataset for resume parsing"""
        try:
            print("Downloading NER dataset...")
            kaggle.api.dataset_download_files(
                'dataturks/resume-entities-for-ner',
                path=f"{self.config.RESUMES_DIR}/ner",
                unzip=True
            )
            print("✅ Successfully downloaded NER dataset")
        except Exception as e:
            print(f"❌ Error downloading NER dataset: {str(e)}")

if __name__ == "__main__":
    downloader = ResumeDatasetDownloader()
    downloader.download_resume_dataset()
    downloader.download_ner_dataset()
