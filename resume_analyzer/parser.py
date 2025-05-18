"""
Module for extracting text from resume files (PDF and DOCX)
"""
import os
import pdfplumber
from docx import Document

def extract_text_from_resume(file_path):
    """
    Extract text from a resume file (PDF or DOCX)
    
    Args:
        file_path (str): Path to the resume file
        
    Returns:
        str: Extracted text from the resume
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension == '.docx':
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
    """
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    return text

def extract_text_from_docx(docx_path):
    """
    Extract text from a DOCX file
    
    Args:
        docx_path (str): Path to the DOCX file
        
    Returns:
        str: Extracted text from the DOCX
    """
    try:
        doc = Document(docx_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from DOCX: {str(e)}")
