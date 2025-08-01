#!/usr/bin/env python3
"""
Manual Google Maps Scraper - Interactive approach
Helps you manually identify businesses without websites
"""

import time
import csv
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


class ManualScraper:
    def __init__(self):
        self.setup_driver()
        self.prospects = []
        
    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        
    def start_search(self, category="restaurants Battle Creek Michigan"):
        print(f"\nOpening Google Maps search for: {category}")
        url = f"https://www.google.com/maps/search/{category.replace(' ', '+')}"
        self.driver.get(url)
        time.sleep(3)
        
    def interactive_session(self):
        print("\n" + "="*60)
        print("INTERACTIVE GOOGLE MAPS SCRAPER")
        print("="*60)
        print("This will open Google Maps where you can:")
        print("1. Browse businesses manually")
        print("2. Click on businesses to check for websites")
        print("3. Enter prospect details when you find businesses without websites")
        print("4. Type 'done' when finished")
        print("="*60)
        
        categories = [
            "restaurants Battle Creek Michigan",
            "hair salons Battle Creek Michigan", 
            "auto repair Battle Creek Michigan",
            "plumbers Battle Creek Michigan",
            "dentists Battle Creek Michigan",
            "contractors Battle Creek Michigan"
        ]
        
        for category in categories:
            self.start_search(category)
            
            print(f"\nNow searching: {category}")
            print("Browse the map results and look for businesses without websites.")
            print("When you find a prospect, press Enter to add them...")
            
            while True:
                user_input = input("\nPress Enter to add a prospect, or type 'next' for next category, 'done' to finish: ").strip().lower()
                
                if user_input == 'done':
                    return
                elif user_input == 'next':
                    break
                else:
                    # Add a prospect
                    self.add_prospect()
    
    def add_prospect(self):
        print("\n--- Adding New Prospect ---")
        name = input("Business name: ").strip()
        if not name:
            print("Skipping - no name provided")
            return
            
        phone = input("Phone number (optional): ").strip()
        address = input("Address (optional): ").strip()
        category = input("Business type (e.g., restaurant, salon): ").strip()
        notes = input("Notes (optional): ").strip()
        
        prospect = {
            'name': name,
            'phone': phone,
            'address': address,
            'category': category,
            'notes': notes,
            'website': '',
            'has_website': False
        }
        
        self.prospects.append(prospect)
        print(f"✓ Added: {name}")
        print(f"Total prospects: {len(self.prospects)}")
    
    def save_prospects(self):
        if not self.prospects:
            print("No prospects to save")
            return
            
        filename = "battle_creek_manual_prospects"
        
        # Save CSV
        with open(f"{filename}.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'phone', 'address', 'category', 'notes', 'website', 'has_website'])
            writer.writeheader()
            writer.writerows(self.prospects)
        
        # Save JSON
        with open(f"{filename}.json", 'w', encoding='utf-8') as f:
            json.dump(self.prospects, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Saved {len(self.prospects)} prospects to {filename}.csv and {filename}.json")
        
        # Display summary
        print("\n--- YOUR PROSPECTS ---")
        for i, prospect in enumerate(self.prospects, 1):
            print(f"{i}. {prospect['name']}")
            if prospect['phone']:
                print(f"   Phone: {prospect['phone']}")
            if prospect['address']:
                print(f"   Address: {prospect['address']}")
            if prospect['category']:
                print(f"   Type: {prospect['category']}")
            if prospect['notes']:
                print(f"   Notes: {prospect['notes']}")
            print()
    
    def close(self):
        self.driver.quit()


def main():
    scraper = ManualScraper()
    
    try:
        scraper.interactive_session()
        scraper.save_prospects()
    except KeyboardInterrupt:
        print("\n\nSession interrupted - saving current prospects...")
        scraper.save_prospects()
    finally:
        scraper.close()


if __name__ == "__main__":
    main()