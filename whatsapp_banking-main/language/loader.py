
import json
import os

def get_language_file_path(language):
    """Get the path to a language file"""
    file_mapping = {
        'ENGLISH': 'english.txt',
        'HINDI': 'hindi.txt',
        'KANNADA': 'kannada.txt',
        'MARATHI': 'marathi.txt'
    }
    
    filename = file_mapping.get(language, 'english.txt')
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'files', filename)
    
    # Print debug information
    print(f"Looking for language file at: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
    
    return file_path

def load_messages(language):
    """Load messages in the specified language"""
    try:
        filepath = get_language_file_path(language)
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            print(f"Successfully loaded language file with keys: {list(data.keys())}")
            return data
    except FileNotFoundError:
        print(f"Error: {filepath} not found, falling back to english.txt")
        try:
            english_path = get_language_file_path('ENGLISH')
            with open(english_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                print(f"Successfully loaded fallback language file with keys: {list(data.keys())}")
                return data
        except FileNotFoundError:
            print("Error: english.txt not found")
            # Return a basic structure with required keys
            return {
                "welcome_message": "Dear {user_name}, Welcome to National Co-operative Bank",
                "select_options": "Please Select the Options",
                "menu": {
                    "account_services": {
                        "title": "Account Services",
                        "subtitle": "please select the option below",
                        "options": [
                            {"title": "Balance", "postbackText": "BALENG"}
                        ]
                    }
                },
                "messages": {
                    "balance": "Your balance is {balance}"
                }
            }
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {filepath}")
        return {
            "welcome_message": "Dear {user_name}, Welcome to National Co-operative Bank",
            "select_options": "Please Select the Options",
            "menu": {},
            "messages": {}
        }
