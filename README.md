# HealthProfs Scraper

This script extracts professional contact information from HealthProfs, specifically for professionals located in a set list of Connecticut cities. It collects names, cities, and website links for acupuncturists, chiropractors, and massage therapists, and stores this data in two separate CSV files:

- healthprofs.csv: The master database, containing all collected professionals without duplicates.

- healthprofs_newprof.csv: A file that only includes newly discovered professionals in each run.

Features

* Extracts professional names, cities, and website URLs.

* Avoids duplicate entries across multiple script executions.

* Limits data collection to specific Connecticut cities.

* Differentiates between previously collected and new professionals.

* Easy to extend and maintain.

Prerequisites

Make sure you have the following Python packages installed:

(pip install selenium webdriver-manager)

Usage

Simply run the script:

(python healthprofs.py)

Make sure to place the script in the same directory as your CSV files or specify their paths accordingly. The script will automatically manage the creation of both CSV files if they don't already exist.

Customization

If you want to change the list of target cities, simply update the cities_of_interest list in the script to reflect your preferred locations.

Notes

- The script opens multiple browser tabs for each professional profile, so make sure to have a stable internet connection.

- Only professionals with websites are recorded in the CSV files.

License

Feel free to use and modify this script as needed.
