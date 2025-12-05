import fitz  # PyMuPDF
import pdfplumber
import re
from pathlib import Path

class PDFParser:
    @staticmethod
    def extract_text_pymupdf(pdf_path: str) -> str:
        """Extract text using PyMuPDF"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text.strip()
        except Exception as e:
            print(f"Error extracting with PyMuPDF: {str(e)}")
            return ""
    
    @staticmethod
    def extract_text_pdfplumber(pdf_path: str) -> str:
        """Extract text using pdfplumber (better for tables)"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error extracting with pdfplumber: {str(e)}")
            return ""
    
    @staticmethod
    def extract_text(pdf_path: str) -> str:
        """Extract text with fallback"""
        text = PDFParser.extract_text_pymupdf(pdf_path)
        if not text or len(text) < 100:
            text = PDFParser.extract_text_pdfplumber(pdf_path)
        return text
    
    @staticmethod
    def extract_contact_info(text: str) -> dict:
        """Extract contact information"""
        contact = {
            'email': None,
            'phone': None,
            'linkedin': None,
            'github': None
        }
        
        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact['email'] = email_match.group(0)
        
        # Phone
        phone_pattern = r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,5}[-\s\.]?[0-9]{1,5}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact['phone'] = phone_match.group(0)
        
        # LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_match = re.search(linkedin_pattern, text.lower())
        if linkedin_match:
            contact['linkedin'] = linkedin_match.group(0)
        
        # GitHub
        github_pattern = r'github\.com/[\w-]+'
        github_match = re.search(github_pattern, text.lower())
        if github_match:
            contact['github'] = github_match.group(0)
        
        return contact
