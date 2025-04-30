from db.repositories import get_user_balance, update_user_balance

def process_payment(phone_number, amount):
    """Process a payment for the user"""
    current_balance = get_user_balance(phone_number)
    
    if current_balance is None:
        return False, "User not found"
    
    if current_balance < amount:
        return False, "Insufficient balance"
    
    # Calculate new balance
    new_balance = current_balance - amount
    
    # Update balance in database
    if update_user_balance(phone_number, new_balance):
        return True, new_balance
    
    return False, "Failed to update balance"

def check_outstanding_amount(check_number):
    """Check outstanding amount for a check number"""
    # In a real application, this would query a database
    # For this example, we'll return a fixed amount
    return 3000.0
