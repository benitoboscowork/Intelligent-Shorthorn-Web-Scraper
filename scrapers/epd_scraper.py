from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import questionary
import re
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.text import Text
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

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
        try:
            if dv_search_results and dv_search_results.find('table').find_all('tr')[4].get_text(separator=' ', strip=True).lower() == "no matching records found":
                return 0
        except:
            pass
        # Timeout check
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Timeout of {timeout} seconds exceeded. Check your internet connections or find a better input filter")


def search_epd():
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
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # User choose parameter that they want to input
        select_elem = soup.find("form", id="epd_search").find('table').find_all('tr', valign='middle')
        LABEL_TO_PARAMETER = {}
        for i in range (len(select_elem)):
            parameter = select_elem[i].get_text(separator = ' ', strip = True)
            order = i
            LABEL_TO_PARAMETER[parameter] = i

        while True:
            parameter_labels_to_set = questionary.checkbox(
                "Select the criteria/parameter you want to set (use spacebar to select, enter to confirm):",
                choices=list(LABEL_TO_PARAMETER.keys())
            ).ask()

            if len(parameter_labels_to_set)>0:  # Non-empty list means at least one selected
                break
            else:
                print("\033[31mYou must select at least one option. Please try again.\033[0m")


        # User giving input to the parameter that they choose
        for label in parameter_labels_to_set:
            order = LABEL_TO_PARAMETER[label]
            all_inputs = select_elem[order].find_all("input")
            # Input radio from the website is for sorting, not free string input that given by user. We will handle the radio button later
            inputs_without_radio = [inp for inp in all_inputs if inp.get("type") != "radio"]
            input_temp= []

            print(f"\n--- Setting values for: {label} ---")
            min_val = questionary.text(f"  Enter Min for {label}:").ask()
            max_val = questionary.text(f"  Enter Max for {label}:").ask()
            acc_val = questionary.text(f"  Enter Acc for {label}:").ask()
            input_temp.extend([min_val, max_val, acc_val])
        
            # Fill the website text box by user's input
            for j in range (len(inputs_without_radio)):
                text_box = driver.find_element("xpath", ".//form[@id='epd_search']").find_element("tag name", "table").find_elements("xpath", ".//tr[@valign='middle']")[order].find_elements("tag name", "input")[j]
                #text_box = wait.until(EC.presence_of_element_located((By.XPATH, ".//tr[@valign='middle']")))
                text_box.clear()
                text_box.send_keys(input_temp[j])

        # Handle radio button by ask the user which parameter (that they already choose) that will get sort (if they want)
        sort_choices = ['None'] + parameter_labels_to_set
        sort_choice = questionary.select(
            "\nWhich parameter to sort by?",
            choices=sort_choices
        ).ask()
        
        # Mimic to push the button in the website based on user's choice
        if sort_choice and sort_choice != 'None':
            order = LABEL_TO_PARAMETER[sort_choice]
            sort_button = driver.find_element("xpath", ".//form[@id='epd_search']").find_element("tag name", "table").find_elements("xpath", ".//tr[@valign='middle']")[order].find_element("xpath", ".//input[@type='radio']")
            sort_button.click()


        # User choose which animal type they want as filter
        ANIMAL_TYPES = {}
        bulls_button = driver.find_element("xpath", ".//form[@id='epd_search']").find_element("xpath", ".//font[@id='asr2']").text
        female_button = driver.find_element("xpath", ".//form[@id='epd_search']").find_element("xpath", ".//font[@id='asr3']").text
        both_button = driver.find_element("xpath", ".//form[@id='epd_search']").find_element("xpath", ".//font[@id='asr1']").text

        ANIMAL_TYPES[bulls_button] = 0
        ANIMAL_TYPES[female_button] = 1
        ANIMAL_TYPES[both_button] = 2
        
        type_choice = questionary.select(
            "Which animal type?",
            choices=ANIMAL_TYPES,
        ).ask()
        
        # Mimic to push the button in the website based on user's choice
        choice_type = ANIMAL_TYPES[type_choice]
        choice_button = driver.find_element("xpath", ".//form[@id='epd_search']").find_elements("xpath", f".//input[@name='search_sex']")[choice_type]
        choice_button.click()
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@onclick='doSearch_Epd();']")))
        submit_button.click()

        # Wait for the results to load after submitting search (either failed or success)
        results_bool = wait_for_conditions(driver, TIMEOUT)
        
        if results_bool == 0: # If no results from the user's input
            print("\033[31mNo Results!.\033[0m")

        elif results_bool == 1:
            # Crawl Table Results
            animals = []
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            animal_rows = soup.find("div", id="dvSearchResults").find_all('tr', id=re.compile(r'^tr_'))


            for row in animal_rows:
                cells = row.find_all('td', recursive=False)
                info_cell = cells[0]
                info_parts = [part.get_text(strip=True) for part in info_cell.find_all('td')]
                info_parts = [part for part in info_parts if part]
                data_columns = []
                for data_cell in cells[2:]:
                    values = [val.get_text(strip=True) for val in data_cell.find_all('td')]
                    values.extend([''] * (4 - len(values)))
                    data_columns.append(values)

                animals.append({
                    "info": info_parts,
                    "data_columns": data_columns,
                })


            def display_data_in_cli(parsed_data: list[dict]):
                """
                Displays the structured data in a multi-line format using Rich.
                """
                console = Console(record=True, width=2000)
                table = Table(
                    title="\n[bold green]EPD SEARCH RESULTS[/bold green]",
                    show_header=True,
                    header_style="bold magenta",
                )

                # Add column
                table.add_column("Reg # \\ Tattoo \\ Name", justify="left", style="cyan", no_wrap=True)
                table.add_column(" ", justify="right") # Column for labels

                HEADERS = [ 
                "CED", "BW", "WW", "YW", "MK", "TM", "CEM", "ST",
                "YG", "CW", "REA", "FAT", "MB", "$CEZ", "$BMI", "$CPI", "$F"
                ]

                # Add a column from the parameters that are shown on the site
                for header in HEADERS:
                    table.add_column(header, justify="center", no_wrap=True)

                labels = Text("EPD:\n+/-chg:\nACC:\nRank:", style="bold")

                # Add the values from the scrapping result
                for animal in parsed_data:
                    reg_num = f"[bold]{animal['info'][0]}[/bold]"
                    info_text = "\n".join([reg_num] + animal['info'][1:])
                    data_cells = ["\n".join(col) for col in animal['data_columns']]
                    row_style = ""
                    table.add_row(info_text, labels, *data_cells, style=row_style)
                    table.add_row(end_section=True)

                console.print(table)

            display_data_in_cli(animals)


    except Exception as e:
        print("An error occurred:", e)