import re
from typing import Dict, Tuple
from preprocessing.pdf_parser import PDFParser

class ResumeValidator:
    """Validates if uploaded PDF is a resume or random document"""
    
    def __init__(self):
        # Key sections that should appear in a resume
        self.resume_sections = [
            'experience', 'education', 'skills', 'work experience',
            'employment', 'qualification', 'projects', 'internship',
            'objective', 'summary', 'achievements', 'certifications'
        ]
        
        # Resume-specific patterns
        self.resume_indicators = [
            r'\b(email|e-mail)\b',
            r'\b(phone|mobile|contact)\b',
            r'\b(linkedin|github)\b',
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email pattern
            r'\b(bachelor|master|phd|b\.tech|m\.tech|mba)\b',
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\b',
            r'\b(19|20)\d{2}\s*[-–]\s*(19|20)\d{2}|present\b'  # Date ranges
        ]
    
    def validate_resume(self, pdf_path: str) -> Tuple[bool, Dict]:
        """
        Validate if PDF is a resume
        Returns: (is_valid, details)
        """
        # Extract text
        text = PDFParser.extract_text(pdf_path)
        
        if not text or len(text) < 200:
            return False, {
                'is_valid': False,
                'reason': 'Document is too short or text extraction failed',
                'confidence': 0.0,
                'suggestions': ['Please upload a PDF with readable text', 'Ensure the resume is at least one page']
            }
        
        text_lower = text.lower()
        
        # Check for resume sections
        sections_found = 0
        found_section_names = []
        for section in self.resume_sections:
            if section in text_lower:
                sections_found += 1
                found_section_names.append(section)
        
        # Check for resume indicators
        indicators_found = 0
        for pattern in self.resume_indicators:
            if re.search(pattern, text_lower):
                indicators_found += 1
        
        # Calculate confidence score
        section_score = min(sections_found / 3, 1.0) * 0.6  # Max 60%
        indicator_score = min(indicators_found / 4, 1.0) * 0.4  # Max 40%
        confidence = section_score + indicator_score
        
        # Check for contact information
        contact_info = PDFParser.extract_contact_info(text)
        has_contact = any(contact_info.values())
        
        # Validation logic
        is_valid = (
            sections_found >= 2 and
            indicators_found >= 3 and
            has_contact
        )
        
        details = {
            'is_valid': is_valid,
            'confidence': round(confidence, 2),
            'sections_found': found_section_names,
            'has_contact_info': has_contact,
            'contact_details': contact_info,
            'text_length': len(text),
            'word_count': len(text.split())
        }
        
        if not is_valid:
            suggestions = []
            if sections_found < 2:
                suggestions.append('Add standard resume sections like Education, Experience, Skills')
            if not has_contact:
                suggestions.append('Include contact information (email, phone)')
            if indicators_found < 3:
                suggestions.append('Structure document with dates, job titles, and qualifications')
            
            details['reason'] = 'Document does not appear to be a valid resume'
            details['suggestions'] = suggestions
        
        return is_valid, details
    
    def validate_text(self, text: str) -> Tuple[bool, Dict]:
        """Validate text directly without PDF"""
        if not text or len(text) < 200:
            return False, {
                'is_valid': False,
                'reason': 'Text is too short',
                'confidence': 0.0
            }
        
        text_lower = text.lower()
        sections_found = sum(1 for section in self.resume_sections if section in text_lower)
        indicators_found = sum(1 for pattern in self.resume_indicators if re.search(pattern, text_lower))
        
        confidence = (min(sections_found / 3, 1.0) * 0.6 + min(indicators_found / 4, 1.0) * 0.4)
        is_valid = sections_found >= 2 and indicators_found >= 3
        
        return is_valid, {
            'is_valid': is_valid,
            'confidence': round(confidence, 2),
            'sections_found': sections_found,
            'indicators_found': indicators_found
        }
