"""
Module for generating visualizations for resume analysis
"""
import json

def generate_skills_chart(analysis_result, match_result):
    """
    Generate data for skills chart visualization
    
    Args:
        analysis_result (dict): Analysis results from analyze_resume
        match_result (dict): Match results from calculate_match_score
        
    Returns:
        dict: Data for skills chart visualization
    """
    # Get skills from resume
    resume_skills = []
    for category, skills in analysis_result['skills'].items():
        resume_skills.extend(skills)
    
    # Get skills from job description (both found and missing)
    job_skills = match_result['skills_found'] + match_result['skills_missing']
    
    # Prepare data for skills chart
    skills_data = []
    
    for skill in job_skills:
        skills_data.append({
            'skill': skill,
            'in_resume': skill in resume_skills,
            'in_job': True
        })
    
    # Add skills from resume that are not in job description
    for skill in resume_skills:
        if skill not in job_skills:
            skills_data.append({
                'skill': skill,
                'in_resume': True,
                'in_job': False
            })
    
    # Group skills by category
    skills_by_category = {}
    
    for skill_data in skills_data:
        skill = skill_data['skill']
        
        # Find which category this skill belongs to
        for category, skill_list in analysis_result['skills'].items():
            if skill in skill_list:
                if category not in skills_by_category:
                    skills_by_category[category] = []
                skills_by_category[category].append(skill_data)
                break
        else:
            # If not found in any category, add to "other"
            if "other" not in skills_by_category:
                skills_by_category["other"] = []
            skills_by_category["other"].append(skill_data)
    
    return {
        'skills_data': skills_data,
        'skills_by_category': skills_by_category
    }

def generate_match_chart(match_result):
    """
    Generate data for match score chart visualization
    
    Args:
        match_result (dict): Match results from calculate_match_score
        
    Returns:
        dict: Data for match score chart visualization
    """
    return {
        'overall_match': match_result['match_percentage'],
        'skill_match': match_result['skill_match_percentage'],
        'content_match': match_result['tfidf_similarity'],
        'semantic_match': match_result['semantic_similarity']
    }
