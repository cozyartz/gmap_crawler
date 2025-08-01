#!/usr/bin/env python3
"""
Simplified Google Maps Business Scraper
Uses a more reliable approach to find businesses without websites.
"""

import time
import csv
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class SimpleScraper:
    def __init__(self):
        self.setup_driver()
        
    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def scrape_category(self, category):
        print(f"\nSearching for: {category}")
        
        # Use direct Google Maps search
        url = f"https://www.google.com/maps/search/{category}+Battle+Creek+Michigan"
        self.driver.get(url)
        
        # Wait and let page load
        time.sleep(5)
        
        businesses = []
        
        try:
            # Look for business listings
            WebDriverWait(self.driver, 10).until(
                lambda d: d.find_elements(By.CSS_SELECTOR, "div[role='article'], .hfpxzc, .Nv2PK")
            )
            
            # Scroll to load more results
            for i in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Find all business elements
            business_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[role='article'], .hfpxzc")
            print(f"Found {len(business_elements)} potential businesses")
            
            for i, element in enumerate(business_elements[:20]):  # Limit to first 20
                try:
                    # Click on business
                    self.driver.execute_script("arguments[0].click();", element)
                    time.sleep(2)
                    
                    # Extract data
                    business = self.extract_business_info()
                    if business and business['name']:
                        businesses.append(business)
                        print(f"  {i+1}. {business['name']} - Website: {'Yes' if business['website'] else 'No'}")
                        
                except Exception as e:
                    print(f"  Error with business {i+1}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error loading businesses: {e}")
            
        return businesses
    
    def extract_business_info(self):
        try:
            # Try multiple selectors for name
            name = ""
            for selector in ["h1", "[data-attrid='title']", ".x3AX1-LfntMc-header-title-title"]:
                try:
                    name_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    name = name_elem.text.strip()
                    if name:
                        break
                except:
                    continue
            
            # Extract address
            address = ""
            for selector in ["[data-item-id='address'] .Io6YTe", ".Io6YTe"]:
                try:
                    addr_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    address = addr_elem.text.strip()
                    if address and "Battle Creek" in address:
                        break
                except:
                    continue
            
            # Extract phone
            phone = ""
            for selector in ["[data-item-id*='phone'] .Io6YTe", "[aria-label*='Phone']"]:
                try:
                    phone_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    phone = phone_elem.text.strip()
                    if phone:
                        break
                except:
                    continue
            
            # Check for website
            website = ""
            try:
                website_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='http']")
                for link in website_links:
                    href = link.get_attribute('href')
                    if href and not any(x in href for x in ['google.com', 'maps.google', 'goo.gl', 'facebook.com']):
                        website = href
                        break
            except:
                pass
            
            if name:
                return {
                    'name': name,
                    'address': address,
                    'phone': phone,
                    'website': website,
                    'has_website': bool(website),
                    'category': 'Unknown'
                }
                
        except Exception as e:
            print(f"Error extracting business info: {e}")
            
        return None
    
    def save_results(self, businesses, filename_base="battle_creek_prospects"):
        if not businesses:
            print("No businesses found to save")
            return
            
        # Filter businesses without websites
        no_website = [b for b in businesses if not b['has_website']]
        
        print(f"\nTotal businesses found: {len(businesses)}")
        print(f"Businesses without websites: {len(no_website)}")
        
        if no_website:
            # Save CSV
            with open(f"{filename_base}.csv", 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['name', 'address', 'phone', 'website', 'has_website', 'category'])
                writer.writeheader()
                writer.writerows(no_website)
            
            # Save JSON
            with open(f"{filename_base}.json", 'w', encoding='utf-8') as f:
                json.dump(no_website, f, indent=2, ensure_ascii=False)
            
            print(f"\nProspects saved to {filename_base}.csv and {filename_base}.json")
            
            # Show first few prospects
            print("\n--- TOP PROSPECTS (NO WEBSITE) ---")
            for i, biz in enumerate(no_website[:10]):
                print(f"{i+1}. {biz['name']}")
                if biz['phone']:
                    print(f"   Phone: {biz['phone']}")
                if biz['address']:
                    print(f"   Address: {biz['address']}")
                print()
        
        return no_website
    
    def close(self):
        self.driver.quit()


def main():
    categories = [
        "restaurants",
        "hair salons", 
        "auto repair",
        "plumbers",
        "dentists",
        "contractors"
    ]
    
    scraper = SimpleScraper()
    all_businesses = []
    
    try:
        for category in categories:
            businesses = scraper.scrape_category(category)
            all_businesses.extend(businesses)
            time.sleep(3)  # Delay between categories
        
        scraper.save_results(all_businesses)
        
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()