import requests
from config.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER

def send_sms_notification(phone_number, message):
    """Send SMS notification via Twilio"""
    url = f'https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json'
    auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    data = {
        'To': phone_number,
        'From': TWILIO_PHONE_NUMBER,
        'Body': message
    }
    
    try:
        response = requests.post(url, data=data, auth=auth)
        return True, response.json()
    except Exception as e:
        print(f"Error sending SMS notification: {e}")
        return False, str(e)
