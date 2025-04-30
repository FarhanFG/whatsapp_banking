import random
import string
import os

def generate_random_string(length=10):
    """Generate a random string of fixed length"""
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def read_lang_from_file():
    """Read language setting from file"""
    try:
        with open('LANG.txt', 'r') as file:
            lang = file.read().strip()
            return lang
    except FileNotFoundError:
        return "ENGLISH"  # Default language if the file doesn't exist

def write_lang_to_file(lang):
    """Write language setting to file"""
    try:
        with open('LANG.txt', 'w') as file:
            file.write(lang)
        return True
    except Exception as e:
        print(f"Error writing language to file: {e}")
        return False
