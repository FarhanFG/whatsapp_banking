import httpx
from config.settings import WHATSAPP_API_KEY, WHATSAPP_SOURCE_NUMBER, WHATSAPP_SRC_NAME

async def send_main_menu(destination, messages, user_name):
    """Send the main menu to the user"""
    print(f"Sending main menu to {destination}")
    url = 'https://api.gupshup.io/sm/api/v1/msg'
    
    title = messages["welcome_message"].format(user_name=user_name)
    body = messages["select_options"]
    global_button_title = "Options"
    
    # Get menu structure from messages file
    menu = messages["menu"]
    items = [
        {
            "title": section_data["title"],
            "subtitle": section_data["subtitle"],
            "options": [
                {"type": "text", "title": opt["title"], "postbackText": opt["postbackText"]}
                for opt in section_data["options"]
            ]
        }
        for section_name, section_data in menu.items()
    ]
    
    payload = {
        "channel": "whatsapp",
        "source": WHATSAPP_SOURCE_NUMBER,
        "destination": destination,
        "src.name": WHATSAPP_SRC_NAME,
        "message": {
            "type": "list",
            "title": title,
            "body": body,
            "msgid": "list1",
            "globalButtons": [{"type": "text", "title": global_button_title}],
            "items": items
        }
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "apikey": WHATSAPP_API_KEY
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, params=payload, headers=headers)
    
    print("Response from Gupshup API:", response.text)
    return response

async def send_language_menu(destination, messages):
    """Send the language selection menu to the user"""
    print("Sending language menu")
    url = 'https://api.gupshup.io/sm/api/v1/msg'
    
    lang_menu = messages["language_menu"]
    title = lang_menu["title"]
    body = lang_menu["body"]
    global_button_title = "Options"
    items = [
        {
            "title": lang_menu["languages"]["title"],
            "subtitle": lang_menu["languages"]["subtitle"],
            "options": lang_menu["languages"]["options"]
        }
    ]
    
    payload = {
        "channel": "whatsapp",
        "source": WHATSAPP_SOURCE_NUMBER,
        "destination": destination,
        "src.name": WHATSAPP_SRC_NAME,
        "message": {
            "type": "list",
            "title": title,
            "body": body,
            "msgid": "list1",
            "globalButtons": [{"type": "text", "title": global_button_title}],
            "items": items
        }
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "apikey": WHATSAPP_API_KEY
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, params=payload, headers=headers)
    
    print("Response from Gupshup API:", response.text)
    return response

async def send_settings_menu(destination, messages):
    """Send the settings menu to the user"""
    print("Sending settings menu")
    url = 'https://api.gupshup.io/sm/api/v1/msg'
    
    settings = messages["settings"]
    title = settings["title"]
    body = settings["body"]
    global_button_title = "Options"
    
    items = [
        {
            "title": settings["security"]["title"],
            "subtitle": settings["security"]["subtitle"],
            "options": settings["security"]["options"]
        }
    ]
    
    payload = {
        "channel": "whatsapp",
        "source": WHATSAPP_SOURCE_NUMBER,
        "destination": destination,
        "src.name": WHATSAPP_SRC_NAME,
        "message": {
            "type": "list",
            "title": title,
            "body": body,
            "msgid": "list1",
            "globalButtons": [{"type": "text", "title": global_button_title}],
            "items": items
        }
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "apikey": WHATSAPP_API_KEY
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, params=payload, headers=headers)
    
    print("Response from Gupshup API:", response.text)
    return response

async def send_bill_payment_menu(destination, messages):
    """Send the bill payment menu to the user"""
    print("Sending bill payment menu")
    url = 'https://api.gupshup.io/sm/api/v1/msg'
    
    bill_payment = messages["bill_payment"]
    title = bill_payment["title"]
    body = bill_payment["body"]
    global_button_title = "Options"
    
    items = [
        {
            "title": bill_payment["utility_bills"]["title"],
            "subtitle": bill_payment["utility_bills"]["subtitle"],
            "options": bill_payment["utility_bills"]["options"]
        },
        {
            "title": bill_payment["vehicle_bills"]["title"],
            "subtitle": bill_payment["vehicle_bills"]["subtitle"],
            "options": bill_payment["vehicle_bills"]["options"]
        }
    ]
    
    payload = {
        "channel": "whatsapp",
        "source": WHATSAPP_SOURCE_NUMBER,
        "destination": destination,
        "src.name": WHATSAPP_SRC_NAME,
        "message": {
            "type": "list",
            "title": title,
            "body": body,
            "msgid": "list1",
            "globalButtons": [{"type": "text", "title": global_button_title}],
            "items": items
        }
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "apikey": WHATSAPP_API_KEY
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, params=payload, headers=headers)
    
    print("Response from Gupshup API:", response.text)
    return response
