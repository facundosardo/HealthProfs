# 📝 HealthProfs Scraper  

This script extracts professional contact information from **HealthProfs**, specifically targeting acupuncturists, chiropractors, and massage therapists in a predefined list of Connecticut cities. It saves the data in two CSV files:  

---

## 📁 **Generated Files**  
- **healthprofs.csv:** Master database containing all collected professionals without duplicates.  
- **healthprofs_newprof.csv:** Contains only the newly discovered professionals in each run (empty if no new professionals are found).  

---

## ⚙️ **Requirements**  
- **Python 3.8+**  
- **Google Chrome**  
- **Selenium:**  
    ```bash
    pip install selenium webdriver-manager
    ```  

---

## 🚀 **How to Use**  
1. **Clone the repository or download the script.**  
2. **Install dependencies:**  
    ```bash
    pip install selenium webdriver-manager
    ```  
3. **Run the script:**  
    ```bash
    python healthprofs.py
    ```  

---

## 🌐 **Script Details**  
- Extracts names, cities, and websites of professionals.  
- Filters professionals by a specific list of Connecticut cities.  
- Avoids duplicate entries by comparing with the master file (`healthprofs.csv`).  
- If no new professionals are found, the `healthprofs_newprof.csv` file remains empty.  

---

## 🤖 **Customization**  
To change the list of target cities, edit the `TARGET_CITIES` list in the script.  

