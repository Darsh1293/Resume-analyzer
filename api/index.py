from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import sys
import re
import json
from collections import Counter
from werkzeug.utils import secure_filename
import nltk
import importlib.util

# Set up NLTK data path for Vercel
nltk_data_path = os.path.join('/tmp', 'nltk_data')
os.makedirs(nltk_data_path, exist_ok=True)
nltk.data.path.append(nltk_data_path)

# Download necessary NLTK data to the temp directory
try:
    nltk.download('punkt', download_dir=nltk_data_path)
    nltk.download('stopwords', download_dir=nltk_data_path)
except Exception as e:
    print(f"Error downloading NLTK data: {e}")

# Create a new Flask app for Vercel with proper template path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir = os.path.join(root_dir, 'templates')
static_dir = os.path.join(root_dir, 'static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Set up configuration
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx'}

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Import the resume parser module
try:
    # Add the project root to the path
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root_dir)
    
    # Import the resume parser
    from resume_analyzer.parser import extract_text_from_resume
except Exception as e:
    print(f"Error importing resume_analyzer: {e}")
    
    # Define a fallback function if import fails
    def extract_text_from_resume(file_path):
        return f"Error extracting text: {str(e)}"

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Common skills dictionary for IT/Tech jobs
COMMON_SKILLS = {
    'programming_languages': [
        'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'go'
    ],
    'web_development': [
        'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask',
        'spring', 'asp.net', 'jquery', 'bootstrap'
    ],
    'databases': [
        'sql', 'mysql', 'postgresql', 'oracle', 'mongodb', 'cassandra', 'redis', 'elasticsearch'
    ],
    'cloud_platforms': [
        'aws', 'azure', 'google cloud', 'gcp', 'heroku', 'digitalocean'
    ],
    'devops': [
        'docker', 'kubernetes', 'jenkins', 'gitlab ci', 'github actions', 'ci/cd'
    ],
    'data_science': [
        'machine learning', 'deep learning', 'ai', 'artificial intelligence', 'data mining',
        'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch'
    ],
    'soft_skills': [
        'communication', 'teamwork', 'leadership', 'problem solving', 'critical thinking',
        'time management', 'adaptability', 'creativity', 'project management', 'agile', 'scrum'
    ]
}

def extract_skills(text):
    """Extract skills from text"""
    skills = {category: [] for category in COMMON_SKILLS}
    
    # Find skills in text
    for category, skill_list in COMMON_SKILLS.items():
        for skill in skill_list:
            # Check for exact matches (with word boundaries)
            if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
                if skill not in skills[category]:
                    skills[category].append(skill)
    
    # Return skills with counts
    result = {}
    for category, skill_list in skills.items():
        if skill_list:  # Only include categories with found skills
            result[category] = skill_list
    
    return result

def calculate_match_score(resume_text, job_description):
    """Calculate match score between resume and job description"""
    # Preprocess texts
    resume_text = resume_text.lower()
    job_description = job_description.lower()
    
    # Extract skills
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)
    
    # Flatten skills
    resume_skills_flat = []
    for category, skills in resume_skills.items():
        resume_skills_flat.extend(skills)
    
    job_skills_flat = []
    for category, skills in job_skills.items():
        job_skills_flat.extend(skills)
    
    # Find matching and missing skills
    skills_found = [skill for skill in job_skills_flat if skill in resume_skills_flat]
    skills_missing = [skill for skill in job_skills_flat if skill not in resume_skills_flat]
    
    # Calculate skill match percentage
    skill_match_percentage = 0
    if job_skills_flat:
        skill_match_percentage = (len(skills_found) / len(job_skills_flat)) * 100
    
    # Simple word overlap similarity
    resume_words = set(re.findall(r'\b\w+\b', resume_text))
    job_words = set(re.findall(r'\b\w+\b', job_description))
    
    # Remove common English stopwords
    try:
        stopwords = set(nltk.corpus.stopwords.words('english'))
        resume_words = resume_words - stopwords
        job_words = job_words - stopwords
    except Exception as e:
        print(f"Error with stopwords: {e}")
        # Continue without stopwords if there's an error
    
    # Calculate Jaccard similarity (intersection over union)
    intersection = len(resume_words.intersection(job_words))
    union = len(resume_words.union(job_words))
    
    content_similarity = 0
    if union > 0:
        content_similarity = (intersection / union) * 100
    
    # Combine scores (weighted average)
    match_percentage = (0.7 * skill_match_percentage) + (0.3 * content_similarity)
    match_percentage = min(100, max(0, match_percentage))  # Ensure between 0-100
    
    # Generate suggestions
    suggestions = []
    if skills_missing:
        suggestions.append(f"Consider adding these missing skills to your resume: {', '.join(skills_missing[:5])}")
        if len(skills_missing) > 5:
            suggestions.append(f"...and {len(skills_missing) - 5} more skills")
    
    # Prepare chart data
    skills_chart_data = {
        'skills_data': [
            {'skill': skill, 'in_resume': True, 'in_job': skill in job_skills_flat} 
            for skill in resume_skills_flat
        ] + [
            {'skill': skill, 'in_resume': False, 'in_job': True} 
            for skill in skills_missing
        ]
    }
    
    match_chart_data = {
        'overall_match': round(match_percentage, 1),
        'skill_match': round(skill_match_percentage, 1),
        'content_match': round(content_similarity, 1)
    }
    
    return {
        'match_percentage': round(match_percentage, 1),
        'skills_found': skills_found,
        'skills_missing': skills_missing,
        'suggestions': suggestions,
        'skills_chart': skills_chart_data,
        'match_chart': match_chart_data
    }

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['resume']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Please upload PDF or DOCX files only.'}), 400
    
    job_description = request.form.get('job_description', '')
    if not job_description:
        return jsonify({'error': 'Job description is required'}), 400
    
    try:
        # Save the file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract text from resume
        resume_text = extract_text_from_resume(filepath)
        
        # Calculate match score
        result = calculate_match_score(resume_text, job_description)
        
        # Clean up the file
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Handle static files for Vercel
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(static_dir, path)

# This is needed for local development
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
