"""
Module for analyzing resume content and calculating match scores
"""
import re
import nltk
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    import sys
    import subprocess
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_md"])
    nlp = spacy.load("en_core_web_md")

# Load sentence transformer model for semantic similarity
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Common skills dictionary for IT/Tech jobs
COMMON_SKILLS = {
    'programming_languages': [
        'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'go', 
        'rust', 'typescript', 'scala', 'perl', 'r', 'matlab', 'bash', 'shell', 'powershell'
    ],
    'web_development': [
        'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask',
        'spring', 'asp.net', 'jquery', 'bootstrap', 'tailwind', 'sass', 'less', 'webpack',
        'graphql', 'rest api', 'soap', 'xml', 'json'
    ],
    'databases': [
        'sql', 'mysql', 'postgresql', 'oracle', 'mongodb', 'cassandra', 'redis', 'elasticsearch',
        'dynamodb', 'firebase', 'neo4j', 'sqlite', 'mariadb', 'couchdb', 'hbase'
    ],
    'cloud_platforms': [
        'aws', 'azure', 'google cloud', 'gcp', 'heroku', 'digitalocean', 'linode', 'openstack',
        'cloudflare', 'vercel', 'netlify', 'lambda', 'ec2', 's3', 'rds'
    ],
    'devops': [
        'docker', 'kubernetes', 'jenkins', 'gitlab ci', 'github actions', 'travis ci', 'ansible',
        'terraform', 'puppet', 'chef', 'prometheus', 'grafana', 'elk stack', 'ci/cd'
    ],
    'data_science': [
        'machine learning', 'deep learning', 'ai', 'artificial intelligence', 'data mining',
        'pandas', 'numpy', 'scipy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras',
        'tableau', 'power bi', 'matplotlib', 'seaborn', 'plotly', 'nlp', 'computer vision'
    ],
    'soft_skills': [
        'communication', 'teamwork', 'leadership', 'problem solving', 'critical thinking',
        'time management', 'adaptability', 'creativity', 'project management', 'agile', 'scrum'
    ]
}

def analyze_resume(resume_text):
    """
    Analyze resume text to extract key information
    
    Args:
        resume_text (str): Text extracted from the resume
        
    Returns:
        dict: Analysis results containing skills, education, experience, etc.
    """
    # Preprocess text
    resume_text = preprocess_text(resume_text)
    
    # Process with spaCy
    doc = nlp(resume_text)
    
    # Extract skills
    skills = extract_skills(doc, resume_text)
    
    # Extract education
    education = extract_education(doc, resume_text)
    
    # Extract work experience
    experience = extract_experience(doc, resume_text)
    
    # Return analysis results
    return {
        'skills': skills,
        'education': education,
        'experience': experience,
        'full_text': resume_text
    }

def preprocess_text(text):
    """
    Preprocess text by removing extra whitespace, converting to lowercase, etc.
    
    Args:
        text (str): Raw text
        
    Returns:
        str: Preprocessed text
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters
    text = re.sub(r'[^\w\s]', ' ', text)
    
    return text.strip()

def extract_skills(doc, text):
    """
    Extract skills from resume text
    
    Args:
        doc (spacy.Doc): spaCy document
        text (str): Preprocessed resume text
        
    Returns:
        dict: Dictionary of skills by category
    """
    skills = {category: [] for category in COMMON_SKILLS}
    
    # Flatten the skills list
    all_skills = []
    for category, skill_list in COMMON_SKILLS.items():
        all_skills.extend(skill_list)
    
    # Find skills in text
    for skill in all_skills:
        # Check for exact matches (with word boundaries)
        if re.search(r'\\b' + re.escape(skill) + r'\\b', text):
            # Find which category this skill belongs to
            for category, skill_list in COMMON_SKILLS.items():
                if skill in skill_list and skill not in skills[category]:
                    skills[category].append(skill)
    
    # Return skills with counts
    result = {}
    for category, skill_list in skills.items():
        if skill_list:  # Only include categories with found skills
            result[category] = skill_list
    
    return result

def extract_education(doc, text):
    """
    Extract education information from resume text
    
    Args:
        doc (spacy.Doc): spaCy document
        text (str): Preprocessed resume text
        
    Returns:
        list: List of education entries
    """
    # Common education keywords
    education_keywords = [
        'bachelor', 'master', 'phd', 'doctorate', 'degree', 'diploma', 'certification',
        'university', 'college', 'school', 'institute', 'academy', 'education'
    ]
    
    # Find education section
    education_section = ""
    lines = text.split('\n')
    in_education_section = False
    
    for line in lines:
        # Check if this line could be an education section header
        if any(keyword in line for keyword in ['education', 'academic', 'qualification']):
            in_education_section = True
            education_section += line + "\n"
        # If we're in the education section, add the line
        elif in_education_section:
            # Check if we've moved to a new section
            if any(keyword in line for keyword in ['experience', 'skills', 'projects', 'certifications']):
                in_education_section = False
            else:
                education_section += line + "\n"
    
    # If no clear education section was found, look for education keywords throughout the text
    if not education_section:
        for line in lines:
            if any(keyword in line for keyword in education_keywords):
                education_section += line + "\n"
    
    # Extract degree information
    degrees = []
    if education_section:
        # Split into potential degree entries
        entries = re.split(r'\n+', education_section)
        for entry in entries:
            if any(keyword in entry for keyword in education_keywords):
                degrees.append(entry.strip())
    
    return degrees

def extract_experience(doc, text):
    """
    Extract work experience information from resume text
    
    Args:
        doc (spacy.Doc): spaCy document
        text (str): Preprocessed resume text
        
    Returns:
        list: List of work experience entries
    """
    # Common experience section keywords
    experience_keywords = [
        'experience', 'employment', 'work', 'job', 'career', 'professional'
    ]
    
    # Find experience section
    experience_section = ""
    lines = text.split('\n')
    in_experience_section = False
    
    for line in lines:
        # Check if this line could be an experience section header
        if any(keyword in line for keyword in experience_keywords):
            in_experience_section = True
            experience_section += line + "\n"
        # If we're in the experience section, add the line
        elif in_experience_section:
            # Check if we've moved to a new section
            if any(keyword in line for keyword in ['education', 'skills', 'projects', 'certifications']):
                in_experience_section = False
            else:
                experience_section += line + "\n"
    
    # Extract job information
    jobs = []
    if experience_section:
        # Look for date patterns to separate job entries
        date_pattern = r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|may|june|july|august|september|october|november|december)[\s\-]+(20\d{2}|19\d{2})'
        job_entries = re.split(date_pattern, experience_section, flags=re.IGNORECASE)
        
        # Clean up and combine entries
        for i in range(0, len(job_entries), 3):
            if i+2 < len(job_entries):
                # Combine month, year, and job description
                job = job_entries[i] + job_entries[i+1] + " " + job_entries[i+2]
                jobs.append(job.strip())
            elif i < len(job_entries):
                # Just add the remaining text
                jobs.append(job_entries[i].strip())
    
    return jobs

def calculate_match_score(resume_analysis, job_description):
    """
    Calculate match score between resume and job description
    
    Args:
        resume_analysis (dict): Analysis results from analyze_resume
        job_description (str): Job description text
        
    Returns:
        dict: Match results including score, matching skills, missing skills, and suggestions
    """
    # Preprocess job description
    job_description = preprocess_text(job_description)
    
    # Process job description with spaCy
    job_doc = nlp(job_description)
    
    # Extract skills from job description
    job_skills = extract_skills(job_doc, job_description)
    
    # Flatten job skills
    job_skills_flat = []
    for category, skills in job_skills.items():
        job_skills_flat.extend(skills)
    
    # Flatten resume skills
    resume_skills_flat = []
    for category, skills in resume_analysis['skills'].items():
        resume_skills_flat.extend(skills)
    
    # Find matching and missing skills
    skills_found = [skill for skill in job_skills_flat if skill in resume_skills_flat]
    skills_missing = [skill for skill in job_skills_flat if skill not in resume_skills_flat]
    
    # Calculate skill match percentage
    skill_match_percentage = 0
    if job_skills_flat:
        skill_match_percentage = (len(skills_found) / len(job_skills_flat)) * 100
    
    # Calculate semantic similarity between resume and job description
    resume_text = resume_analysis['full_text']
    
    # TF-IDF vectorization and cosine similarity
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = tfidf_vectorizer.fit_transform([resume_text, job_description])
        tfidf_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0] * 100
    except:
        tfidf_similarity = 0
    
    # Semantic similarity using sentence transformers
    try:
        # Split texts into chunks to handle long texts
        resume_chunks = [resume_text[i:i+512] for i in range(0, len(resume_text), 512)]
        job_chunks = [job_description[i:i+512] for i in range(0, len(job_description), 512)]
        
        # Get embeddings
        resume_embeddings = model.encode(resume_chunks)
        job_embeddings = model.encode(job_chunks)
        
        # Average embeddings
        resume_embedding = np.mean(resume_embeddings, axis=0)
        job_embedding = np.mean(job_embeddings, axis=0)
        
        # Calculate cosine similarity
        semantic_similarity = cosine_similarity(
            [resume_embedding], 
            [job_embedding]
        )[0][0] * 100
    except:
        semantic_similarity = 0
    
    # Combine scores (weighted average)
    match_percentage = (0.4 * skill_match_percentage) + (0.3 * tfidf_similarity) + (0.3 * semantic_similarity)
    match_percentage = min(100, max(0, match_percentage))  # Ensure between 0-100
    
    # Generate suggestions
    suggestions = generate_suggestions(skills_missing, resume_analysis, job_description)
    
    return {
        'match_percentage': round(match_percentage, 1),
        'skill_match_percentage': round(skill_match_percentage, 1),
        'tfidf_similarity': round(tfidf_similarity, 1),
        'semantic_similarity': round(semantic_similarity, 1),
        'skills_found': skills_found,
        'skills_missing': skills_missing,
        'suggestions': suggestions
    }

def generate_suggestions(missing_skills, resume_analysis, job_description):
    """
    Generate improvement suggestions based on missing skills and other factors
    
    Args:
        missing_skills (list): Skills missing from the resume
        resume_analysis (dict): Analysis results from analyze_resume
        job_description (str): Job description text
        
    Returns:
        list: List of suggestions for improving the resume
    """
    suggestions = []
    
    # Suggest adding missing skills
    if missing_skills:
        suggestions.append(f"Consider adding these missing skills to your resume: {', '.join(missing_skills[:5])}")
        if len(missing_skills) > 5:
            suggestions.append(f"...and {len(missing_skills) - 5} more skills")
    
    # Check education section
    if not resume_analysis['education']:
        suggestions.append("Add your educational background to strengthen your resume")
    
    # Check experience section
    if not resume_analysis['experience']:
        suggestions.append("Include your work experience with detailed responsibilities")
    
    # Check for keywords in job description that might be missing from resume
    job_keywords = extract_important_keywords(job_description)
    resume_text = resume_analysis['full_text']
    
    missing_keywords = []
    for keyword in job_keywords:
        if keyword.lower() not in resume_text.lower():
            missing_keywords.append(keyword)
    
    if missing_keywords:
        suggestions.append(f"Consider adding these keywords from the job description: {', '.join(missing_keywords[:5])}")
        if len(missing_keywords) > 5:
            suggestions.append(f"...and {len(missing_keywords) - 5} more keywords")
    
    return suggestions

def extract_important_keywords(text):
    """
    Extract important keywords from text using TF-IDF
    
    Args:
        text (str): Text to extract keywords from
        
    Returns:
        list: List of important keywords
    """
    # Process with spaCy
    doc = nlp(text)
    
    # Extract nouns and proper nouns
    keywords = []
    for token in doc:
        if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop and len(token.text) > 2:
            keywords.append(token.text)
    
    return keywords
