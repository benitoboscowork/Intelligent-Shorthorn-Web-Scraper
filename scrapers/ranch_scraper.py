import pandas as pd
from ._core import perform_search_and_parse

def search_ranch(ranch_name: str, name_op: str = 'ct') -> pd.DataFrame:
    """Prepares and executes a Ranch Search."""
    print(f"\nSearching for ranches where name '{name_op}' '{ranch_name}'...")
    params = {
        'search': 'Y',
        'ranch_search': 'Y',
        'ranch_name': ranch_name,
        'name_op': name_op
    }
    return perform_search_and_parse(params)