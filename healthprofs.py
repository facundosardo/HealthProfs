import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

# List of cities of interest
cities_of_interest = [
    "Bethel", "Bridgeport", "Brookfield", "Danbury", "Darien", "Easton",
    "Fairfield", "Greenwich", "Monroe", "New Canaan", "Newtown", "Norwalk",
    "Redding", "Ridgefield", "Shelton", "Sherman", "Stamford", "Stratford",
    "Trumbull", "Weston", "Westport", "Wilton", "New Fairfield"
]

# Browser configuration
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# CSV files
master_file = 'healthprofs.csv'
new_pros_file = 'healthprofs_newprof.csv'

# Create CSV files if they don't exist and load existing professionals
existing_professionals = set()
if os.path.exists(master_file):
    with open(master_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            existing_professionals.add(f"{row[0]},{row[1]}")
else:
    with open(master_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "City", "Website Link"])

# Create file for new professionals
with open(new_pros_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Name", "City", "Website Link"])

# Function to navigate to specific category
categories = [
    ("Find an Acupuncturist", "Acupuncturists in Connecticut"),
    ("Find a Chiropractor", "Chiropractors in Connecticut"),
    ("Find a Massage Therapist", "Massage Therapists in Connecticut")
]

def extract_professionals(main_title, state_title):
    try:
        # Navigate to main category
        driver.get("https://www.healthprofs.com/us/members")
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'//a[@title="{main_title}"]'))).click()
        time.sleep(2)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'//a[@title="{state_title}"]'))).click()
        time.sleep(2)

        while True:
            professionals = driver.find_elements(By.XPATH, '//div[contains(@class, "results-row")]')
            for professional in professionals:
                try:
                    # Extract full name
                    try:
                        first_name = professional.find_element(By.XPATH, ".//span[@class='multi-word']").text.strip()
                        last_name = professional.find_element(By.XPATH, ".//span[@class='last-word']").text.strip()
                        name = f"{first_name} {last_name}"
                    except:
                        name = professional.find_element(By.XPATH, ".//div[contains(@class, 'results-row-heading-container')]//a").text.strip()

                    # Extract city
                    try:
                        city_element = professional.find_element(By.XPATH, './/span[@class="address"]/a')
                        city = city_element.text.strip().split(",")[0]  # Only clean city name
                    except:
                        continue  # Skip if no city is found

                    # Check if city is of interest and not already registered
                    unique_key = f"{name},{city}"
                    if city not in cities_of_interest or unique_key in existing_professionals:
                        continue

                    # Find website link
                    profile_url = professional.find_element(By.XPATH, './/a').get_attribute("href")
                    driver.execute_script("window.open(arguments[0]);", profile_url)
                    driver.switch_to.window(driver.window_handles[1])
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                    website_url = None
                    possible_xpaths = [
                        '//a[@data-x="website-link"]',
                        '//a[contains(text(), "Website")]','//a[contains(text(), "My website")]',
                        '//a[contains(text(), "My Website")]',
                        '//a[contains(@href, "website-redirect")]',
                    ]

                    for xpath in possible_xpaths:
                        try:
                            link = driver.find_element(By.XPATH, xpath)
                            website_url = link.get_attribute("href")
                            if website_url:
                                break
                        except:
                            continue

                    # Save to both files
                    if website_url:
                        with open(master_file, mode='a', newline='', encoding='utf-8') as file:
                            writer = csv.writer(file)
                            writer.writerow([name, city, website_url])
                        existing_professionals.add(unique_key)

                        with open(new_pros_file, mode='a', newline='', encoding='utf-8') as file:
                            writer = csv.writer(file)
                            writer.writerow([name, city, website_url])

                        print(f"{name} | {city} | Link saved: {website_url}")

                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    time.sleep(1)

                except Exception as e:
                    print(f"Error processing professional {name if 'name' in locals() else 'unknown'}: {e}")
                    continue

            try:
                next_button = driver.find_element(By.XPATH, '//div[@class="pagination-controls-end"]/a')
                next_page_url = next_button.get_attribute("href")
                if next_page_url:
                    driver.get(next_page_url)
                    time.sleep(3)
                else:
                    print("No more pages to load.")
                    break
            except:
                print("No more pages to load.")
                break
    except Exception as e:
        print(f"Error extracting for {main_title}: {e}")

for main_title, state_title in categories:
    extract_professionals(main_title, state_title)

print("Extraction completed.")
driver.quit()
