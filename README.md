# AI-Powered Resume Parser & Company Matcher

GenAI project for resume analysis with company placement predictions.

## Features

- ✅ Resume validation using NLP
- 🎯 Company matching using TF-IDF & Cosine Similarity
- 💡 Personalized recommendations
- 📊 Interactive Streamlit dashboard
- 🔄 FastAPI backend

## Tech Stack

- **Backend:** FastAPI, Python 3.13
- **Frontend:** Streamlit
- **NLP:** spaCy, scikit-learn
- **PDF Processing:** PyMuPDF, pdfplumber
- **ML:** TF-IDF, Cosine Similarity (current), Deep Learning (planned)

## Installation

Install dependencies
pip install -r requirements.txt

Download spaCy model
python -m spacy download en_core_web_sm

Create mock data
python create_mock_data.py

text

## Usage

Terminal 1: Start API
python -m uvicorn api.main:app --reload

Terminal 2: Start Frontend
streamlit run frontend/app.py

text

Visit: http://localhost:8501

## Project Structure

resume-parser-project/
├── api/ # FastAPI backend
├── frontend/ # Streamlit UI
├── models/ # ML models & algorithms
├── preprocessing/ # PDF parsing & feature extraction
├── scraping/ # Web scrapers (planned)
├── data/ # Data storage
└── tests/ # Unit tests

text

## Roadmap

### Phase 1: Current (v1.0) ✅
- Rule-based resume validation
- TF-IDF similarity matching
- Mock company data

### Phase 2: Planned (v2.0)
- [ ] Real web scraping (Indeed, LinkedIn)
- [ ] Train classification model (Random Forest/XGBoost)
- [ ] Fine-tune spaCy NER for resumes
- [ ] LLM integration (Gemini/GPT)