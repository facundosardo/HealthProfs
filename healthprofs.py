import os
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# List of target cities to filter professionals
TARGET_CITIES = [
    "Bethel", "Bridgeport", "Brookfield", "Danbury", "Darien", "Easton",
    "Fairfield", "Greenwich", "Monroe", "New Canaan", "Newtown", "Norwalk",
    "Redding", "Ridgefield", "Shelton", "Sherman", "Stamford", "Stratford",
    "Trumbull", "Weston", "Westport", "Wilton", "New Fairfield"
]

MASTER_FILE = 'healthprofs.csv'
NEW_PROS_FILE = 'healthprofs_newprof.csv'

# Load existing professionals from master CSV to avoid duplicates
existing_professionals = set()
if os.path.exists(MASTER_FILE):
    with open(MASTER_FILE, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            existing_professionals.add(f"{row[0]},{row[1]}")
else:
    # Initialize master CSV with headers if not present
    with open(MASTER_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "City", "Website Link"])

# Initialize new professionals CSV with headers
with open(NEW_PROS_FILE, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Name", "City", "Website Link"])

def extract_professionals(profession_name, location_name):
    """
    Extract professionals data for a given profession and location.

    Args:
        profession_name (str): Profession name to click on the page (e.g. "Acupuncturists")
        location_name (str): Location link text to filter (e.g. "Connecticut")
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 15)

    try:
        # Open the main members page
        driver.get("https://www.healthprofs.com/us/members")

        # Click on the profession link (by visible text)
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{profession_name}')]"))).click()
        time.sleep(2)

        # Click on the location link (by visible text)
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{location_name}')]"))).click()
        time.sleep(2)

        while True:
            # Find all professional result rows on the page
            professionals = driver.find_elements(By.XPATH, '//div[contains(@class, "results-row")]')
            for professional in professionals:
                try:
                    # Extract full name: try splitting into first and last name, fallback to entire name
                    try:
                        first_name = professional.find_element(By.XPATH, ".//span[@class='multi-word']").text.strip()
                        last_name = professional.find_element(By.XPATH, ".//span[@class='last-word']").text.strip()
                        name = f"{first_name} {last_name}"
                    except:
                        name = professional.find_element(By.XPATH, ".//div[contains(@class, 'results-row-heading-container')]//a").text.strip()

                    # Extract city from address
                    try:
                        city_element = professional.find_element(By.XPATH, './/span[@class="address"]/a')
                        city = city_element.text.strip().split(",")[0]
                    except:
                        continue  # Skip if city is not found

                    unique_key = f"{name},{city}"

                    # Filter out professionals not in target cities or already extracted
                    if city not in TARGET_CITIES or unique_key in existing_professionals:
                        continue

                    # Extract profile URL and open in new tab
                    profile_url = professional.find_element(By.XPATH, './/a').get_attribute("href")
                    driver.execute_script("window.open(arguments[0]);", profile_url)
                    driver.switch_to.window(driver.window_handles[1])
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                    # Try to find personal website link
                    website_url = ""
                    possible_xpaths = [
                        '//a[@data-x="website-link"]',
                        '//a[contains(text(), "Website")]',
                        '//a[contains(text(), "My website")]',
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

                    # Close the profile tab and switch back to main results
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                    # Save professional to CSV files
                    with open(MASTER_FILE, mode='a', newline='', encoding='utf-8') as f_master:
                        writer_master = csv.writer(f_master)
                        writer_master.writerow([name, city, website_url])
                    existing_professionals.add(unique_key)

                    with open(NEW_PROS_FILE, mode='a', newline='', encoding='utf-8') as f_new:
                        writer_new = csv.writer(f_new)
                        writer_new.writerow([name, city, website_url])

                    print(f"Saved: {name} | {city} | Website: {website_url if website_url else '(no website)'}")
                    time.sleep(1)  # Be polite, avoid hammering server

                except Exception as e:
                    print(f"Error processing professional {name if 'name' in locals() else 'unknown'}: {e}")
                    continue

            # Pagination - navigate to next page if exists
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
        print(f"Error extracting for {profession_name}: {e}")

    finally:
        driver.quit()


if __name__ == "__main__":
    # Extract each profession sequentially
    extract_professionals("Acupuncturists", "Connecticut")
    extract_professionals("Chiropractors", "Connecticut")
    extract_professionals("Massage Therapists", "Connecticut")

    print("Extraction completed.")
