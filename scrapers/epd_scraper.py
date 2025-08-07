import pandas as pd
from ._core import perform_search_and_parse

def search_epd(epd_filters: dict, sex: str = 'B', active_status: str = 'A') -> pd.DataFrame:
    """Prepares and executes an EPD Search."""
    print(f"\nStarting EPD Search with filters: {epd_filters}...")
    base_params = {
        'search': 'Y', 'epd_search': 'Y', 'search_type': 'epd_search',
        'sex': sex, 'active': active_status,
        # Set all other possible EPD fields to empty strings
        'ced_min': '', 'ced_max': '', 'bw_min': '', 'bw_max': '', 'ww_min': '',
        'ww_max': '', 'yw_min': '', 'yw_max': '', 'milk_min': '', 'milk_max': '',
    }
    # Update the base parameters with the user-provided filters
    base_params.update(epd_filters)
    return perform_search_and_parse(base_params)