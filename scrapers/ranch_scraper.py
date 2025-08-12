from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import questionary
from selenium.webdriver.chrome.service import Service
from rich.console import Console
from rich.table import Table


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
            raise TimeoutError(f"Timeout of {timeout} seconds exceeded waiting for conditions.")


chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

print("Setting up Chrome driver...")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
print("Driver setup complete.")

def search_ranch():
    try:    
        # Open the website
        driver.get("https://shorthorn.digitalbeef.com/")
        wait = WebDriverWait(driver, TIMEOUT)

        # User input Ranch Search Method
        LABEL_TO_RANCH_SEARCH_METHOD = ["Specific registered animals or herds", "General searches by geographic or entity information"]
        
        choice_method_search = questionary.select(
            "Please enter you SEX choice: ",
            choices=LABEL_TO_RANCH_SEARCH_METHOD
        ).ask()

        # Case if choose Specific Registered Method
        if choice_method_search == "Specific registered animals or herds":
            # User input Ranch Search Method Choice
            LABEL_TO_SPECIFIC_SEARCH_CHOICE = ["Herd Prefix", "Member ID"]
            
            # Need to make sure the user must at least check 1 box (either choose herd prefix, member ID, or both)
            while True:
                choice_method_specific_search = questionary.checkbox(
                    "Select the method specific search you want to set (use spacebar to select, enter to confirm):",
                    choices=LABEL_TO_SPECIFIC_SEARCH_CHOICE,
                ).ask()

                if len(choice_method_specific_search)>0:  # Non-empty list means at least one selected
                    break
                else:
                    print("\033[31mYou must select at least one option. Please try again.\033[0m")

            if "Herd Prefix" in choice_method_specific_search:
                text_herd = input("Please enter your input Herd Prefix: ").strip()
                text_box = wait.until(EC.presence_of_element_located((By.ID, "ranch_search_prefix")))
                text_box.clear()
                text_box.send_keys(f"{text_herd}")

            if "Member ID" in choice_method_specific_search:
                text_memberid = input("Please enter your input Member ID: ").strip()
                text_box = wait.until(EC.presence_of_element_located((By.ID, "ranch_search_id")))
                text_box.clear()
                text_box.send_keys(f"{text_memberid}")

            submit_button = wait.until(EC.element_to_be_clickable((By.NAME, "btnsubmit")))
            submit_button.click()

            results_bool = wait_for_conditions(driver, TIMEOUT)
            # # Wait for the results to load after submitting search
            # wait.until(EC.presence_of_element_located((By.XPATH, "//tr[@id='tr_0']")))

        else:
            text_name = input("Please enter your input Name (use an asterix (*) as a wildcard): ").strip()
            text_box = wait.until(EC.presence_of_element_located((By.NAME, "ranch_search_val")))
            text_box.clear()
            text_box.send_keys(f"{text_name}")
            
            text_city = input("Please enter your input City (might be null): ").strip()
            text_box = wait.until(EC.presence_of_element_located((By.NAME, "ranch_search_city")))
            text_box.clear()
            text_box.send_keys(f"{text_city}")
            
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            select_elem = soup.find("select", id="search-member-location")
            options = select_elem.find_all("option")

            option_list = []
            key_val = {}
            for option in options:
                value = option.get("value")
                text = option.text.strip()
                key_val[text] = value
                option_list.append(text)
            
            choices = option_list
            selected_location = questionary.select(
                "Which Search Location would you like to choose?",
                choices=choices,
                use_indicator=True  # Adds a nice arrow '»' to the selected item
            ).ask()

            selected_location = key_val[selected_location]
            submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, f"//*[@value='{selected_location}']")))
            submit_button.click()
            submit_button = wait.until(EC.element_to_be_clickable((By.NAME, "btnsubmit")))
            submit_button.click()

            # Wait for the results to load after submitting search
            results_bool = wait_for_conditions(driver, TIMEOUT)
        if results_bool == 0:
            print("\033[31mNo Results!.\033[0m")
        elif results_bool == 1:            
            wait.until(EC.presence_of_element_located((By.XPATH, "//tr[@id='tr_0']")))

            # Starting to Scrape the result
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            console = Console(record=True, width=2000)
            
            # Get the id of the table
            results_div = soup.find("div", id="dvSearchResults")
            table_ranch_results = results_div.find("table").find("table")
        
            # Try to scrape table title from how many Profiles Matched the Criteria
            tr_title = table_ranch_results.find_all('tr')[0]            
            table_title = tr_title.get_text(separator=' ', strip=True)

            # We're using Table from Rich Package to make the print table result better than default print() python
            table = Table(
                title=f"\n[bold green]{table_title}[/bold green]",
                show_header=True,
                header_style="bold magenta",
            )

            # Now try to scrape the column's name from the table
            tr_value = table_ranch_results.find_all('tr')[1]
            tr_value = tr_value.find_all('td')
            for i in range (len(tr_value)): #4 because the table has 4 columns
                column_name = tr_value[i].get_text(separator=' ', strip = True)
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