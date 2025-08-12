import sys
# Import the pure scraping function from our scrapers package
from scrapers import search_animal,search_ranch,search_epd
from pprint import pprint
import questionary



# def get_validated_input(prompt: str, valid_options: list) -> str:
#     """A helper function to get validated user input."""
#     while True:
#         user_input = input(prompt).strip()
#         # For options that are case-insensitive
#         if user_input.lower() in [opt.lower() for opt in valid_options]:
#             # Return the canonical version (e.g., 'B' not 'b')
#             for opt in valid_options:
#                 if opt.lower() == user_input.lower():
#                     return opt
#         else:
#             print(f"Invalid input. Please choose from: {', '.join(valid_options)}")

def handle_animal_search():
    json_file = search_animal()
    #pprint(json_file, sort_dicts=False)

def handle_ranch_search():
    json_file = search_ranch()
    #pprint(json_file, sort_dicts=False)

def handle_epd_search():
    json_file = search_epd()
    pprint(json_file, sort_dicts=False)

def main_menu():
    """Displays the main menu and controls the program flow."""
    
    while True:
        LABEL_TO_SEARCH = ["1: Animal Search", "2: Ranch Search", "3: EPD Search", "4. Exit Program"]

        choice_search = questionary.select(
            "Select the choice you want to set (use spacebar to select, enter to confirm):",
            choices=LABEL_TO_SEARCH
        ).ask()

        if choice_search == '1: Animal Search':
            handle_animal_search()
        elif choice_search == '2: Ranch Search':
            handle_ranch_search()
        elif choice_search == '3: EPD Search':
            handle_epd_search()
        elif choice_search == '4. Exit Program':
            print("Exiting program. Goodbye!")
            sys.exit()
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main_menu()