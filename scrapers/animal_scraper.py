import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
from pprint import pprint

def search_animal():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    

    print("Setting up Chrome driver...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    print("Driver setup complete.")

    try:
        # Step 1: Open the website
        driver.get("https://shorthorn.digitalbeef.com/")

        wait = WebDriverWait(driver, 10)
        bool_sex = True
        bool_field = True
        bool_text = True
        while bool_sex:
            print("\n=============================================")
            print(" Search For")
            print("=============================================")
            print("1: Bulls")
            print("2: Females")
            print("3: Both")
            
            choice_sex = input("Please enter your choice: ").strip()
            if choice_sex == "1" or choice_sex == "2" or choice_sex == "3":
                bool_sex = False
            else:
                print("Invalid choice, please try again.")


        while bool_field:
            print("\n=============================================")
            print(" Search For")
            print("=============================================")
            print("1: Reg")
            print("2: Tattoo")
            print("3: Name")
            print("4: EID")
            
            choice_field= input("Please enter your choice: ").strip()
            if choice_field == "1" or choice_field == "2" or choice_field == "3" or choice_field == "4":
                bool_field = False
            else:
                print("Invalid choice, please try again.")

        while bool_text:
            print("\n=============================================")
            print(" Search Value (use an asterix (*) as a wildcard)")
            print("=============================================")

            choice_text = input("Please enter your input text: ").strip()
            if choice_text:
                bool_text = False

        # Step 2: Select radio button with id "animal_search_sex1"
        sex_radio = wait.until(EC.element_to_be_clickable((By.ID, f"animal_search_sex{choice_sex}")))
        sex_radio.click()

        # Step 3: Select radio button with id "animal_search_fld1"
        fld_radio = wait.until(EC.element_to_be_clickable((By.ID, f"animal_search_fld{choice_field}")))
        fld_radio.click()

        # Step 4: Fill text box with id "animal_search_val" with "Cat"
        text_box = wait.until(EC.presence_of_element_located((By.ID, "animal_search_val")))
        text_box.clear()
        text_box.send_keys(f"{choice_text}")

        # Step 5: Click the search button with id "btnAnimalSubmit"
        submit_button = wait.until(EC.element_to_be_clickable((By.ID, "btnAnimalSubmit")))
        submit_button.click()

        # Wait for the results to load after submitting search
        time.sleep(5)  # Or better use explicit wait

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        results_div = soup.find("div", id="dvSearchResults")

        if not results_div:
            print("Could not find the results div.")
        else:
            # Assuming there's a table inside this div
            table = results_div.find("table").find("table")
            if not table:
                print("No table found inside the results div.")
            else:
                column_names = []
                tr_temp = table.find_all('tr')[0]
                text = tr_temp.get_text(separator=' ', strip=True)
                print(f"{text}")
                tr = table.find_all('tr')[1]
                for i in range (4):
                    td = tr.find_all('td')[i].get_text(separator=' ', strip = True)
                    column_names.append(td)
                data_rows = soup.select("tr[id^='tr_']")
                data_as_lists = []
                for row in data_rows:
                # Find all table cells (td) in the current row
                    cells = row.find_all('td')
                    
                    # Ensure the row has the expected number of columns (4)
                    if len(cells) == 4:
                        # Extract text from each cell, stripping leading/trailing whitespace
                        # The .get_text(strip=True) method is great for cleaning up the `&nbsp;` and newlines
                        reg_num = cells[0].get_text(strip=True)
                        prefix_tattoo = cells[1].get_text(strip=True)
                        name = cells[2].get_text(strip=True)
                        birthdate = cells[3].get_text(strip=True)
                        
                        row_data = [reg_num, prefix_tattoo, name, birthdate]
                        data_as_lists.append(row_data)
                    else:
                        print("Something Wrong!!!!")

                        
            final_json_structure = {
                "header": column_names,
                "data": data_as_lists
            }
        return final_json_structure

    except Exception as e:
        print("An error occurred:", e)