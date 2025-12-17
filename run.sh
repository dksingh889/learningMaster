#!/bin/bash

# Script to set up and run the blog

echo "Setting up PHP Help Club Blog..."

# Activate virtual environment
source myenv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run scraper
echo "Scraping blog content..."
python scraper.py

# Import posts
echo "Importing posts to database..."
python import_posts.py

# Run the application
echo "Starting Flask application..."
echo "Blog will be available at http://localhost:5000"
python app.py

