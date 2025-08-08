import sys
# Import the pure scraping function from our scrapers package
from scrapers import search_animal
from pprint import pprint

def get_validated_input(prompt: str, valid_options: list) -> str:
    """A helper function to get validated user input."""
    while True:
        user_input = input(prompt).strip()
        # For options that are case-insensitive
        if user_input.lower() in [opt.lower() for opt in valid_options]:
            # Return the canonical version (e.g., 'B' not 'b')
            for opt in valid_options:
                if opt.lower() == user_input.lower():
                    return opt
        else:
            print(f"Invalid input. Please choose from: {', '.join(valid_options)}")

def handle_animal_search():
    json_file = search_animal()
    pprint(json_file, sort_dicts=False)
    # """Guides the user through an animal search and displays results."""
    # print("\n--- Animal Search ---")
    
    # # --- Collect user input with validation ---
    # sex = get_validated_input(
    #     "Search For (B/F/Both): ", 
    #     ['B', 'F', 'Both']
    # )
    # field = get_validated_input(
    #     "Search Field (name/reg_no/tattoo/eid): ", 
    #     ['name', 'reg_no', 'tattoo', 'eid']
    # )
    # value = input(f"Enter Search Value for '{field}' (use * for wildcard): ").strip()
    
    # # --- Call the scraper ---
    # df = search_animal(sex=sex, field=field, value=value)
    
    # # --- Handle the results ---
    # if df.empty:
    #     print("\n--- Search finished with no results found. ---")
    #     return

    # print(f"\n--- Success! Found {len(df)} results. ---")
    # print("First 5 rows:")
    # print(df.head())
    
    # # --- Ask to save the file ---
    # save_choice = input("\nSave these results to a CSV file? (y/n): ").strip().lower()
    # if save_choice == 'y':
    #     default_filename = f"animal_results_{field}_{value.replace('*', '')}.csv"
    #     filename = input(f"Enter filename (press Enter for default: '{default_filename}'): ").strip()
    #     if not filename:
    #         filename = default_filename
            
    #     try:
    #         df.to_csv(filename, index=False)
    #         print(f"Results saved to '{filename}'")
    #     except Exception as e:
    #         print(f"Could not save file: {e}")

def main_menu():
    """Displays the main menu and controls the program flow."""
    while True:
        print("\n=============================================")
        print(" Shorthorn DigitalBeef Scraper Main Menu")
        print("=============================================")
        print("1: Animal Search")
        print("2: Ranch Search (Not implemented yet)")
        print("3: EPD Search (Not implemented yet)")
        print("Q: Quit")
        
        choice = input("Please enter your choice: ").strip()
        
        if choice == '1':
            handle_animal_search()
            break
        elif choice.lower() == 'q':
            print("Exiting program. Goodbye!")
            sys.exit()
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main_menu()