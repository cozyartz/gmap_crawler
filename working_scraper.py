#!/usr/bin/env python3
"""
Working Google Maps Scraper
Uses a step-by-step approach to reliably extract business data
"""

import time
import csv
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WorkingScraper:
    def __init__(self):
        self.setup_driver()
        
    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        
    def scrape_businesses(self, search_term, max_results=15):
        print(f"\nSearching: {search_term}")
        
        # Navigate to Google Maps
        url = f"https://www.google.com/maps/search/{search_term.replace(' ', '+')}"
        self.driver.get(url)
        time.sleep(4)
        
        businesses = []
        
        try:
            # Wait for search results
            WebDriverWait(self.driver, 10).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, "[data-result-index]")) > 0 or
                         len(d.find_elements(By.CSS_SELECTOR, ".hfpxzc")) > 0
            )
            
            # Get business elements (try multiple selectors)
            business_elements = []
            for selector in ["[data-result-index]", ".hfpxzc", "div[role='article']"]:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    business_elements = elements
                    break
            
            print(f"Found {len(business_elements)} business elements")
            
            # Process each business
            for i, element in enumerate(business_elements[:max_results]):
                if i >= max_results:
                    break
                    
                try:
                    print(f"Processing business {i+1}...")
                    
                    # Click on business
                    self.driver.execute_script("arguments[0].click();", element)
                    time.sleep(2)
                    
                    # Extract business details
                    business = self.extract_business_details()
                    
                    if business and business.get('name'):
                        businesses.append(business)
                        website_status = "✓ Has website" if business.get('website') else "✗ No website"
                        print(f"  {business['name']} - {website_status}")
                    else:
                        print(f"  Could not extract details for business {i+1}")
                        
                except Exception as e:
                    print(f"  Error processing business {i+1}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error during search: {e}")
            
        return businesses
    
    def extract_business_details(self):
        business = {
            'name': '',
            'address': '',
            'phone': '',
            'website': '',
            'has_website': False
        }
        
        try:
            # Extract business name - try multiple approaches
            name_selectors = [
                "h1[data-attrid='title']",
                "h1.x3AX1-LfntMc-header-title-title",
                "h1",
                "[data-attrid='title']",
                ".x3AX1-LfntMc-header-title-title"
            ]
            
            for selector in name_selectors:
                try:
                    name_element = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    name = name_element.text.strip()
                    if name and len(name) > 1:
                        business['name'] = name
                        break
                except:
                    continue
            
            # Extract address
            address_selectors = [
                "[data-item-id='address'] .Io6YTe",
                ".Io6YTe",
                "[data-value='Address']"
            ]
            
            for selector in address_selectors:
                try:
                    addr_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    address = addr_element.text.strip()
                    if address and ("Battle Creek" in address or "Michigan" in address):
                        business['address'] = address
                        break
                except:
                    continue
            
            # Extract phone
            phone_selectors = [
                "[data-item-id*='phone'] .Io6YTe",
                "[aria-label*='Phone']",
                "[data-value*='phone']"
            ]
            
            for selector in phone_selectors:
                try:
                    phone_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    phone = phone_element.text.strip()
                    if phone and any(char.isdigit() for char in phone):
                        business['phone'] = phone
                        break
                except:
                    continue
            
            # Check for website
            try:
                # Look for website links
                links = self.driver.find_elements(By.CSS_SELECTOR, "a[href^='http']")
                for link in links:
                    href = link.get_attribute('href')
                    # Filter out Google/Maps links
                    excluded_domains = ['google.com', 'maps.google', 'goo.gl', 'plus.google', 'facebook.com/maps']
                    if href and not any(domain in href for domain in excluded_domains):
                        # Check if it's actually a website link (not just any external link)
                        link_text = link.text.lower()
                        if any(word in link_text for word in ['website', 'visit', 'www', '.com']) or href.startswith('http'):
                            business['website'] = href
                            business['has_website'] = True
                            break
            except:
                pass
            
        except Exception as e:
            print(f"    Error extracting details: {e}")
            
        return business if business['name'] else None
    
    def save_results(self, all_businesses, filename="battle_creek_businesses"):
        # Filter for businesses without websites
        no_website = [b for b in all_businesses if not b['has_website']]
        
        print(f"\n{'='*50}")
        print(f"SCRAPING RESULTS")
        print(f"{'='*50}")
        print(f"Total businesses found: {len(all_businesses)}")
        print(f"Businesses WITH websites: {len(all_businesses) - len(no_website)}")
        print(f"Businesses WITHOUT websites: {len(no_website)}")
        
        if all_businesses:
            # Save all businesses
            with open(f"{filename}_all.csv", 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['name', 'address', 'phone', 'website', 'has_website'])
                writer.writeheader()
                writer.writerows(all_businesses)
            
            # Save prospects (no website)
            if no_website:
                with open(f"{filename}_prospects.csv", 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['name', 'address', 'phone', 'website', 'has_website'])
                    writer.writeheader()
                    writer.writerows(no_website)
                
                with open(f"{filename}_prospects.json", 'w', encoding='utf-8') as f:
                    json.dump(no_website, f, indent=2, ensure_ascii=False)
                
                print(f"\n🎯 PROSPECTS (NO WEBSITE):")
                print(f"Saved to: {filename}_prospects.csv")
                print(f"Saved to: {filename}_prospects.json")
                
                print(f"\n📋 TOP PROSPECTS:")
                for i, biz in enumerate(no_website[:10], 1):
                    print(f"{i:2d}. {biz['name']}")
                    if biz['phone']:
                        print(f"     📞 {biz['phone']}")
                    if biz['address']:
                        print(f"     📍 {biz['address']}")
                    print()
            
            print(f"\n✅ All results saved to {filename}_all.csv")
            
        return no_website
    
    def close(self):
        self.driver.quit()


def main():
    searches = [
        "restaurants Battle Creek Michigan",
        "hair salons Battle Creek Michigan",
        "auto repair Battle Creek Michigan", 
        "plumbers Battle Creek Michigan",
        "dentists Battle Creek Michigan"
    ]
    
    scraper = WorkingScraper()
    all_businesses = []
    
    try:
        for search in searches:
            businesses = scraper.scrape_businesses(search, max_results=10)
            all_businesses.extend(businesses)
            time.sleep(3)  # Delay between searches
        
        prospects = scraper.save_results(all_businesses)
        
        if prospects:
            print(f"\n🚀 Ready to contact {len(prospects)} prospects!")
            print("Use the CSV file to import into your CRM or contact management system.")
        else:
            print("\n📝 All businesses found have websites. Try different search terms or areas.")
            
    except KeyboardInterrupt:
        print("\n\nStopped by user - saving current results...")
        scraper.save_results(all_businesses)
    except Exception as e:
        print(f"\nError during scraping: {e}")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()