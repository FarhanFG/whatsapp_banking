import os
import random
import requests
from config.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
from db.repositories import store_otp, verify_otp

def check_authentication():
    """Check if the service is authenticated"""
    try:
        with open('pass.txt', 'r') as file:
            passcode = file.read().strip()
            return passcode == "4356"
    except FileNotFoundError:
        return False


def add_passcode():
    """Add authentication passcode"""
    try:
        with open('pass.txt', 'w') as file:
            file.write("4356")
        return {"message": "Passcode added successfully"}
    except Exception as e:
        return {"error": str(e)}

def remove_passcode():
    """Remove authentication passcode"""
    try:
        with open('pass.txt', 'w') as file:
            file.write("")
        return {"message": "Passcode removed successfully"}
    except Exception as e:
        return {"error": str(e)}

def generate_and_send_otp(phone_number):
    """Generate OTP and send via Twilio"""
    # Generate random 4-digit OTP
    otp = str(random.randint(1000, 9999))
    
    # Store OTP in database
    if store_otp(phone_number, otp):
        # Send OTP via Twilio
        url = f'https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json'
        auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        data = {
            'To': '+919035576651',  # This should be configurable
            'From': TWILIO_PHONE_NUMBER,
            'Body': f'OTP for Transaction: {otp}'
        }
        
        try:
            twilio_response = requests.post(url, data=data, auth=auth)
            return True, twilio_response.json()
        except Exception as e:
            print(f"Error sending OTP via Twilio: {e}")
            return False, str(e)
    
    return False, "Failed to store OTP"

def verify_user_otp(phone_number, otp):
    """Verify user-provided OTP"""
    return verify_otp(phone_number, otp)
