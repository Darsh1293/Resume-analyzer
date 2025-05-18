"""
Script to download and set up required NLTK and spaCy data
"""
import nltk
import subprocess
import sys

def main():
    print("Setting up NLP resources...")
    
    # Download NLTK data
    print("Downloading NLTK data...")
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    
    # Download spaCy model
    print("Downloading spaCy model...")
    try:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_md"])
    except Exception as e:
        print(f"Error downloading spaCy model: {str(e)}")
        print("You can manually download it later with: python -m spacy download en_core_web_md")
    
    print("Setup complete!")

if __name__ == "__main__":
    main()
