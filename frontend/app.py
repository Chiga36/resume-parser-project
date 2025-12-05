import streamlit as st
import requests
import json
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# API endpoint
API_URL = "http://localhost:8000"

def main():
    st.markdown('<h1 class="main-header">📄 AI Resume Analyzer</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Welcome to the AI-Powered Resume Analysis Platform
    
    Upload your resume to get:
    - ✅ **Resume Validation** - Check if your document is properly formatted
    - 🎯 **Company Match Predictions** - See your placement probability at top companies
    - 💡 **Personalized Recommendations** - Get actionable suggestions to improve your resume
    """)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF only)",
        type=['pdf'],
        help="Upload a PDF version of your resume for analysis"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Analyze button
        if st.button("🔍 Analyze Resume", type="primary", use_container_width=True):
            with st.spinner("Analyzing your resume... This may take a few seconds."):
                try:
                    # Send request to API
                    files = {'file': (uploaded_file.name, uploaded_file, 'application/pdf')}
                    response = requests.post(f"{API_URL}/api/analyze", files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        display_results(data)
                    elif response.status_code == 400:
                        error_data = response.json()
                        st.error("❌ Invalid Resume Detected")
                        display_validation_error(error_data)
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API server. Make sure it's running on port 8000.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

def display_validation_error(error_data):
    """Display validation errors"""
    validation = error_data.get('validation', {})
    
    st.markdown('<div class="error-box">', unsafe_allow_html=True)
    st.markdown(f"**Confidence Score:** {validation.get('confidence', 0)*100:.1f}%")
    st.markdown(f"**Reason:** {validation.get('message', 'Unknown error')}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    suggestions = validation.get('suggestions', [])
    if suggestions:
        st.markdown("### 📋 Suggestions to Fix Your Resume:")
        for i, suggestion in enumerate(suggestions, 1):
            st.markdown(f"{i}. {suggestion}")

def display_results(data):
    """Display analysis results"""
    
    # Validation status
    validation = data['validation']
    st.markdown('<div class="success-box">', unsafe_allow_html=True)
    st.markdown(f"### ✅ Valid Resume Detected")
    st.markdown(f"**Confidence:** {validation['confidence']*100:.1f}%")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview", 
        "🏢 Company Matches", 
        "💡 Recommendations",
        "🔍 Detailed Analysis"
    ])
    
    with tab1:
        display_overview(data)
    
    with tab2:
        display_company_matches(data)
    
    with tab3:
        display_recommendations(data)
    
    with tab4:
        display_detailed_analysis(data)

def display_overview(data):
    """Display overview metrics"""
    st.markdown("## 📊 Resume Overview")
    
    features = data['features']
    recommendations = data['recommendations']
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Overall Score",
            value=f"{recommendations['overall_score']:.1f}/100",
            delta="Good" if recommendations['overall_score'] > 70 else "Needs Improvement"
        )
    
    with col2:
        st.metric(
            label="Skills Detected",
            value=len(features['skills'])
        )
    
    with col3:
        st.metric(
            label="Experience",
            value=f"{features['experience_years']:.1f} years"
        )
    
    with col4:
        st.metric(
            label="Word Count",
            value=features['word_count']
        )
    
    # Top 3 companies
    st.markdown("### 🎯 Top 3 Company Matches")
    top_companies = data['top_3_companies']
    
    cols = st.columns(3)
    for i, company_data in enumerate(top_companies):
        with cols[i]:
            st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f"**{company_data['company']}**")
            st.markdown(f"### {company_data['probability']:.1f}%")
            st.markdown(f"*{company_data['confidence'].title()} Confidence*")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Skills visualization
    if features['skills']:
        st.markdown("### 🛠️ Detected Skills")
        skills_text = ", ".join(features['skills'][:15])
        st.info(skills_text)

def display_company_matches(data):
    """Display company match details"""
    st.markdown("## 🏢 Company Placement Predictions")
    
    company_matches = data['company_matches']
    
    if not company_matches:
        st.warning("No company profiles available.")
        return
    
    # Create bar chart
    companies = [m['company'] for m in company_matches[:10]]
    probabilities = [m['probability'] for m in company_matches[:10]]
    
    fig = go.Figure(data=[
        go.Bar(
            x=probabilities,
            y=companies,
            orientation='h',
            marker=dict(
                color=probabilities,
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Probability %")
            ),
            text=[f"{p:.1f}%" for p in probabilities],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Top 10 Company Match Probabilities",
        xaxis_title="Placement Probability (%)",
        yaxis_title="Company",
        height=500,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed breakdown
    st.markdown("### 📋 Detailed Company Analysis")
    
    selected_company = st.selectbox(
        "Select a company to see detailed breakdown:",
        [m['company'] for m in company_matches[:10]]
    )
    
    selected_data = next(m for m in company_matches if m['company'] == selected_company)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Match Factors")
        factors = selected_data['factors']
        
        fig_factors = go.Figure(data=[
            go.Bar(
                x=list(factors.values()),
                y=list(factors.keys()),
                orientation='h',
                marker=dict(color='#1f77b4')
            )
        ])
        fig_factors.update_layout(
            xaxis_title="Score (%)",
            yaxis_title="Factor",
            height=300,
            showlegend=False
        )
        st.plotly_chart(fig_factors, use_container_width=True)
    
    with col2:
        st.markdown("#### Experience Comparison")
        st.metric(
            label="Required Experience",
            value=f"{selected_data['required_experience']:.1f} years"
        )
        st.metric(
            label="Your Experience",
            value=f"{selected_data['candidate_experience']:.1f} years",
            delta=f"{selected_data['candidate_experience'] - selected_data['required_experience']:.1f} years"
        )
        st.metric(
            label="Confidence Level",
            value=selected_data['confidence'].title()
        )

def display_recommendations(data):
    """Display improvement recommendations"""
    st.markdown("## 💡 Personalized Recommendations")
    
    recommendations = data['recommendations']
    
    # Strengths
    if recommendations['strengths']:
        st.markdown("### ✅ Your Strengths")
        for strength in recommendations['strengths']:
            st.success(f"✓ {strength}")
    
    st.markdown("---")
    
    # Improvements
    st.markdown("### 🎯 Areas for Improvement")
    improvements = recommendations['improvements']
    
    if improvements:
        for imp in improvements:
            priority_color = "🔴" if imp['priority'] == 1 else "🟡"
            with st.expander(f"{priority_color} {imp['area']} - {imp['impact']} Impact"):
                st.markdown(f"**Suggestion:** {imp['suggestion']}")
    else:
        st.info("Great job! Your resume looks solid.")
    
    st.markdown("---")
    
    # Missing skills
    if recommendations['missing_skills']:
        st.markdown("### 🛠️ Recommended Skills to Add")
        st.markdown("Consider adding these in-demand skills:")
        
        skills_cols = st.columns(3)
        for i, skill in enumerate(recommendations['missing_skills'][:9]):
            with skills_cols[i % 3]:
                st.markdown(f"- {skill}")
    
    st.markdown("---")
    
    # Format suggestions
    st.markdown("### 📝 Formatting Tips")
    for suggestion in recommendations['format_suggestions'][:5]:
        st.info(f"💡 {suggestion}")

def display_detailed_analysis(data):
    """Display detailed analysis"""
    st.markdown("## 🔍 Detailed Technical Analysis")
    
    features = data['features']
    validation = data['validation']
    
    # Validation details
    st.markdown("### Validation Metrics")
    val_details = validation.get('details', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.json({
            "Sections Found": val_details.get('sections_found', []),
            "Has Contact Info": val_details.get('has_contact_info', False),
            "Text Length": val_details.get('text_length', 0)
        })
    
    with col2:
        contact = val_details.get('contact_details', {})
        st.json(contact)
    
    # Feature extraction
    st.markdown("### Extracted Features")
    st.json(features)

if __name__ == "__main__":
    main()
