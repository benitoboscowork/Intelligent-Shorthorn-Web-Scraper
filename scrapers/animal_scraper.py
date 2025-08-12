from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import questionary
from rich.console import Console
from rich.table import Table
import time

TIMEOUT = 300

def wait_for_conditions(driver, timeout = TIMEOUT):
    """
    Waits until either of two conditions are met on the page when user search from their input:

    1) An element <tr id="tr_0"> appears (If there are results)
    2) The <div id="dvSearchResults"> text equals "No Results" (if there's no results)
 
    Returns:
        1 if first condition matched (element found)
        0 if second condition matched ("No Results" text found)

    Raises:
        TimeoutError if neither condition is met within timeout (most likely because of user's internet connection)
    """
    start_time = time.time()

    while True:
        # Check condition 1
        try:
            driver.find_element(By.XPATH, "//tr[@id='tr_0']")
            return 1
        except:
            pass

        # Check condition 2
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        dv_search_results = soup.find('div', id='dvSearchResults')
        if dv_search_results and dv_search_results.get_text(separator=' ', strip=True).lower() == "no results":
            return 0

        # Timeout check
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Timeout of {timeout} seconds exceeded. Check your internet connections or find a better input filter")


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
        # Open the website
        driver.get("https://shorthorn.digitalbeef.com/")
        wait = WebDriverWait(driver, TIMEOUT)
        
        # User input SEX Choice
        LABEL_TO_SEARCH_SEX = { #key,value because different label id (animal_search_sex) just divided by number (1 for Bulls, 2 for Females, 3 for Both)
            "1: Bulls": 1, 
            "2: Females": 2, 
            "3: Both": 3
        }
        choice_sex_search = questionary.select(
            "Please enter you SEX choice: ",
            choices=list(LABEL_TO_SEARCH_SEX.keys())
        ).ask()
       
       # User input FIELD Choice
        LABEL_TO_SEARCH_FIELD = { #key,value because different label id (animal_search_fld) just divided by number (1 for Reg, 2 for Tattoo, 3 for Name, 4 for EID)
            "1: Reg": 1, 
            "2: Tattoo": 2, 
            "3: Name": 3,
            "4: EID": 4 
        }
        choice_field_search = questionary.select(
            "Please enter you FIELD choice: ",
            choices=list(LABEL_TO_SEARCH_FIELD.keys())
        ).ask()

        # User input Search VALUE
        bool_text = True
        while bool_text:
            print("\n=============================================")
            print(" Search Value (use an asterix (*) as a wildcard)")
            print("=============================================")

            choice_text = input("Please enter your input text: ").strip()
            if choice_text:
                bool_text = False


        # Select radio button with id 
        sex_radio = wait.until(EC.element_to_be_clickable((By.ID, f"animal_search_sex{LABEL_TO_SEARCH_SEX[choice_sex_search]}")))
        sex_radio.click()

        # Select radio button with id
        fld_radio = wait.until(EC.element_to_be_clickable((By.ID, f"animal_search_fld{LABEL_TO_SEARCH_FIELD[choice_field_search]}")))
        fld_radio.click()

        # Fill text box with Value Search
        text_box = wait.until(EC.presence_of_element_located((By.ID, "animal_search_val")))
        text_box.clear()
        text_box.send_keys(f"{choice_text}")

        # Click the search button with id "btnAnimalSubmit"
        submit_button = wait.until(EC.element_to_be_clickable((By.ID, "btnAnimalSubmit")))
        submit_button.click()

        # Wait for the results to load after submitting search (either failed or success)
        results_bool = wait_for_conditions(driver, TIMEOUT)

        if results_bool == 0: # If no results from the user's input
            print("\033[31mNo Results!.\033[0m")
        elif results_bool == 1:
            wait.until(EC.presence_of_element_located((By.XPATH, "//tr[@id='tr_0']")))

            # Starting to Scrape the result
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            console = Console(record=True, width=2000)
            
            # Get the id of the table
            results_div = soup.find("div", id="dvSearchResults")
            table_animal_results = results_div.find("table").find("table")
            
            # Try to scrape table title from how many Animals Matched The Criteria
            tr_title = table_animal_results.find_all('tr')[0]            
            table_title = tr_title.get_text(separator=' ', strip=True)

            # We're using Table from Rich Package to make the print table result better than default print() python
            table = Table(
                title=f"\n[bold green]{table_title}[/bold green]",
                show_header=True,
                header_style="bold magenta",
            )

            # Now try to scrape the column's name from the table
            tr_value = table_animal_results.find_all('tr')[1]
            for i in range (4): #4 because the table has 4 columns
                column_name = tr_value.find_all('td')[i].get_text(separator=' ', strip = True)
                
                table.add_column(column_name, justify="left", style="cyan", no_wrap=True) #Add the column's name into the table
                
            # Now try to scrape the row's value from the table
            data_rows = soup.select("tr[id^='tr_']")
            for row in data_rows:
                cells = row.find_all('td')
                row_val_list = []
                for row_index in range (len(cells)):
                    rval = cells[row_index].get_text(separator=' ', strip = True)
                    row_val_list.append(rval)
                table.add_row(*row_val_list)
                table.add_row(end_section=True)

            console.print(table)

    except Exception as e:
        print("An error occurred:", e)