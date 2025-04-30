import requests
import httpx
from config.settings import WHATSAPP_API_KEY, WHATSAPP_SOURCE_NUMBER, WHATSAPP_SRC_NAME

def send_text_message(message, destination_number):
    """Send a simple text message via WhatsApp"""
    url = 'https://api.gupshup.io/wa/api/v1/msg'
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'apikey': WHATSAPP_API_KEY
    }
    
    payload = {
        'channel': 'whatsapp',
        'source': WHATSAPP_SOURCE_NUMBER,
        'destination': destination_number,
        'message': f'{{"type": "text", "text": "{message}", "previewUrl": false}}',
        'src.name': WHATSAPP_SRC_NAME
    }
    
    response = requests.post(url, headers=headers, data=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        return f"Failed to send message: {response.status_code}, {response.text}"

def send_link_message(destination_number, link, preview=True):
    """Send a message with a link"""
    url = 'https://api.gupshup.io/wa/api/v1/msg'
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'apikey': WHATSAPP_API_KEY
    }
    
    payload = {
        'channel': 'whatsapp',
        'source': WHATSAPP_SOURCE_NUMBER,
        'destination': destination_number,
        'message': f'{{"type": "text", "text": "{link}", "previewUrl": {str(preview).lower()}}}',
        'src.name': WHATSAPP_SRC_NAME
    }
    
    response = requests.post(url, headers=headers, data=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        return f"Failed to send message: {response.status_code}, {response.text}"

def send_quick_reply_message(destination, message_body, footer, header, button_title, tracking_text):
    """Send a message with quick reply button"""
    url = 'https://api.gupshup.io/wa/api/v1/msg'
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded',
        'apikey': WHATSAPP_API_KEY,
    }
    payload = {
        'channel': 'whatsapp',
        'source': WHATSAPP_SOURCE_NUMBER,
        'destination': destination,
        'message': f'{{"type":"quick_reply","content":{{"type":"text","text":"{message_body}","caption":"{footer}","header":"{header}"}},"options":[{{"title":"{button_title}","postbackText":"{tracking_text}"}}]}}',
        'src.name': WHATSAPP_SRC_NAME
    }

    response = requests.post(url, headers=headers, data=payload)
    return response
