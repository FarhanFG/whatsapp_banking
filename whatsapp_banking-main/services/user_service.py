from db.repositories import (
    get_user_name, get_user_language, update_user_language,
    get_user_balance, update_user_balance
)
from language.loader import load_messages

# Global messages cache
MESSAGES = {}

def get_user_info(phone_number):
    """Get user information including name and language"""
    name = get_user_name(phone_number)
    language = get_user_language(phone_number)
    return {
        "name": name,
        "language": language
    }

def change_user_language(phone_number, new_language):
    """Change user's language preference"""
    success = update_user_language(phone_number, new_language)
    if success:
        # Reload messages in new language
        reload_messages_for_user(phone_number)
        return True
    return False

def get_user_account_balance(phone_number):
    """Get user's account balance"""
    return get_user_balance(phone_number)

def update_account_balance(phone_number, new_balance):
    """Update user's account balance"""
    return update_user_balance(phone_number, new_balance)

def reload_messages_for_user(phone_number):
    """Reload messages based on user's language preference"""
    global MESSAGES
    language = get_user_language(phone_number)
    MESSAGES = load_messages(language)
    return MESSAGES

def get_messages():
    """Get the current messages"""
    return MESSAGES
