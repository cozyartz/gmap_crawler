#!/bin/bash
# Script to run the Google Maps scraper

echo "Starting Google Maps scraper..."
source venv/bin/activate
python3 gmaps_scraper.py
echo "Scraping complete. Check the generated CSV and JSON files for results."