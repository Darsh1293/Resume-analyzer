# Resume Analyzer Web Application

A web-based application that analyzes resumes against job descriptions to provide match scores and improvement suggestions.

## Features

- Resume upload functionality (PDF/DOCX)
- Text extraction from resumes
- NLP-based analysis for skills, education, and work experience
- Match score calculation with job description using TF-IDF or BERT-based semantic similarity
- Visual insights: skill coverage, missing keywords, and personalized suggestions
- Clean and responsive web interface

## Technology Stack

- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Backend**: Python (Flask)
- **NLP Libraries**: spaCy, NLTK, scikit-learn, sentence-transformers
- **File Parsing**: pdfplumber, python-docx
- **Visualization**: Plotly

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Download required NLTK data:
   ```
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
   ```
4. Download spaCy model:
   ```
   python -m spacy download en_core_web_md
   ```
5. Run the application:
   ```
   python app.py
   ```

## Usage

1. Upload your resume (PDF or DOCX format)
2. Enter the job description
3. Click "Analyze" to see the match score and suggestions
