from flask import Flask, request, jsonify, send_from_directory
import os
import sys

# Add parent directory to path so we can import from app.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app from the main app.py file
from app import app as flask_app

# For Vercel, we need to use the app directly
app = flask_app

# Create uploads folder if it doesn't exist
os.makedirs('uploads', exist_ok=True)

# Handle static files for Vercel
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# This is needed for Vercel serverless functions
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
