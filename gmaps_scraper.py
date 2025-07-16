#!/usr/bin/env python3
"""
Google Maps Business Scraper for Web Development Prospects
Finds local businesses without websites for potential web development clients.
"""

import time
import csv
import json
import re
from urllib.parse import urlencode, urlparse
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class GoogleMapsScraper:
    def __init__(self, headless=True):
        self.setup_driver(headless)
        self.results = []
        
    def setup_driver(self, headless):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def search_businesses(self, query, location="Battle Creek, Michigan"):
        search_url = f"https://www.google.com/maps/search/{urlencode({'q': f'{query} {location}'})}"
        print(f"Searching: {query} in {location}")
        
        self.driver.get(search_url)
        time.sleep(3)
        
        # Wait for results to load
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[role='main']"))
            )
        except TimeoutException:
            print("Results didn't load properly")
            return []
        
        # Scroll to load more results
        self._scroll_results()
        
        # Extract business information
        businesses = self._extract_business_data()
        return businesses
    
    def _scroll_results(self):
        scrollable_div = self.driver.find_element(By.CSS_SELECTOR, "[role='main']")
        last_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
        
        while True:
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
            time.sleep(2)
            
            new_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
            if new_height == last_height:
                break
            last_height = new_height
    
    def _extract_business_data(self):
        businesses = []
        business_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-result-index]")
        
        for element in business_elements:
            try:
                business_data = self._extract_single_business(element)
                if business_data:
                    businesses.append(business_data)
            except Exception as e:
                print(f"Error extracting business data: {e}")
                continue
                
        return businesses
    
    def _extract_single_business(self, element):
        try:
            # Click on the business to get details
            element.click()
            time.sleep(1)
            
            # Extract business information from the sidebar
            name = self._safe_find_text("h1")
            rating = self._safe_find_text("[data-value='Rating']")
            address = self._safe_find_text("[data-item-id='address']")
            phone = self._safe_find_text("[data-item-id*='phone']")
            website = self._extract_website()
            
            if name:
                return {
                    'name': name,
                    'address': address,
                    'phone': phone,
                    'rating': rating,
                    'website': website,
                    'has_website': bool(website)
                }
                
        except Exception as e:
            print(f"Error extracting business: {e}")
            
        return None
    
    def _safe_find_text(self, selector):
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip()
        except NoSuchElementException:
            return ""
    
    def _extract_website(self):
        try:
            website_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='http']")
            for element in website_elements:
                href = element.get_attribute('href')
                if href and not any(domain in href for domain in ['google.com', 'maps.google.com', 'goo.gl']):
                    return href
        except Exception:
            pass
        return ""
    
    def filter_no_website(self, businesses):
        return [b for b in businesses if not b['has_website']]
    
    def save_to_csv(self, businesses, filename="prospects.csv"):
        if not businesses:
            print("No businesses to save")
            return
            
        fieldnames = ['name', 'address', 'phone', 'rating', 'website', 'has_website']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(businesses)
        
        print(f"Saved {len(businesses)} businesses to {filename}")
    
    def save_to_json(self, businesses, filename="prospects.json"):
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(businesses, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(businesses)} businesses to {filename}")
    
    def close(self):
        self.driver.quit()


def main():
    # Business categories to search for
    search_queries = [
        "restaurants",
        "auto repair shops",
        "hair salons",
        "plumbers",
        "electricians",
        "dentists",
        "law firms",
        "real estate agents",
        "contractors",
        "fitness centers",
        "retail stores",
        "medical practices"
    ]
    
    scraper = GoogleMapsScraper(headless=False)  # Set to True for headless mode
    all_businesses = []
    
    try:
        for query in search_queries:
            print(f"\n--- Searching for {query} ---")
            businesses = scraper.search_businesses(query)
            all_businesses.extend(businesses)
            
            # Add delay between searches to avoid rate limiting
            time.sleep(5)
        
        # Filter businesses without websites
        no_website_businesses = scraper.filter_no_website(all_businesses)
        
        print(f"\nFound {len(all_businesses)} total businesses")
        print(f"Found {len(no_website_businesses)} businesses without websites")
        
        # Save results
        if no_website_businesses:
            scraper.save_to_csv(no_website_businesses, "battle_creek_prospects.csv")
            scraper.save_to_json(no_website_businesses, "battle_creek_prospects.json")
            
            # Print summary
            print("\n--- PROSPECTS WITHOUT WEBSITES ---")
            for business in no_website_businesses[:10]:  # Show first 10
                print(f"• {business['name']} - {business['phone']} - {business['address']}")
        
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"Error during scraping: {e}")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()