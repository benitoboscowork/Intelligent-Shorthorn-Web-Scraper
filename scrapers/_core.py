import requests
from bs4 import BeautifulSoup
import pandas as pd

def perform_search_and_parse(params: dict) -> pd.DataFrame:
    """Core function to send a request and parse the results table."""
    base_url = 'https://shorthorn.digitalbeef.com/index.php'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0...)'} # A standard User-Agent

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=20)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
        return pd.DataFrame()

    soup = BeautifulSoup(response.content, 'html.parser')

    

    results_table = soup.find('table', class_='table_color')

    if not results_table:
        return pd.DataFrame()

    headers = [th.get_text(strip=True) for th in results_table.find_all('th')]
    scraped_data = []
    
    table_rows = results_table.find_all('tr')
    if len(table_rows) > 1:
        for row in table_rows[1:]:
            cells = row.find_all('td')
            if len(cells) == len(headers):
                row_data = [cell.get_text(strip=True) for cell in cells]
                scraped_data.append(dict(zip(headers, row_data)))

    return pd.DataFrame(scraped_data)