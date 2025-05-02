from fastapi import FastAPI, Response, Request
import httpx
import uvicorn
import requests
import asyncio
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

# Database connection string using environment variables
XDATABASE_URL = f"postgresql://{os.getenv('CR_DB_USER')}:{os.getenv('CR_DB_PASSWORD')}@{os.getenv('CR_DB_HOST')}:{os.getenv('CR_DB_PORT', '5432')}/{os.getenv('CR_DB_NAME')}"

# Create the SQLAlchemy engine and sessionmaker for PostgreSQL
engine = create_engine(XDATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
class CRRbiNotification(Base):
    __tablename__ = "cr_rbi_notifications"
    
    id = Column(Integer, primary_key=True, index=True)  # Primary key
    guid = Column(Text, nullable=False)                 # GUID column
    title = Column(Text, nullable=False)                # Title column
    link = Column(Text, nullable=False)                 # Link column
    description = Column(Text, nullable=True)           # Description column
    paragraph = Column(Text, nullable=True)             # Paragraph column
    pub_date = Column(DateTime, nullable=True)          # Publication date column

# Optionally create the table if it doesn't exist (for development use only)
Base.metadata.create_all(bind=engine)

# Database connection
def get_db_connection():
   
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

# Create users table if it doesn't exist
def create_users_table():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Create table with language column and latest_otp
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            phone_number VARCHAR(15) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            language VARCHAR(50) DEFAULT 'ENGLISH',
            latest_otp VARCHAR(4)
        )
    """)
    
    # First, try to insert the user
    cur.execute("""
        INSERT INTO users (phone_number, name, language)
        VALUES ('919035576651', 'Farhan', 'ENGLISH')
        ON CONFLICT (phone_number) DO UPDATE 
        SET language = 'ENGLISH'
    """)
    
    conn.commit()
    cur.close()
    conn.close()

# Get user name from phone number
def langupdate(phone_number, new_lang):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Try with the original phone number
        cur.execute("UPDATE users SET language = %s WHERE phone_number = %s", (new_lang, phone_number))
        
        if cur.rowcount == 0 and phone_number.startswith('91'):
            # Try without the '91' prefix
            phone_without_91 = phone_number[2:]
            cur.execute("UPDATE users SET language = %s WHERE phone_number = %s", (new_lang, phone_without_91))
            
        elif cur.rowcount == 0 and not phone_number.startswith('91'):
            # Try with '91' prefix
            phone_with_91 = '91' + phone_number
            cur.execute("UPDATE users SET language = %s WHERE phone_number = %s", (new_lang, phone_with_91))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating language: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def get_user_name(phone_number):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Try with the original phone number
    cur.execute("SELECT name FROM users WHERE phone_number = %s", (phone_number,))
    result = cur.fetchone()
    
    if not result and phone_number.startswith('91'):
        # Try without the '91' prefix
        phone_without_91 = phone_number[2:]
        cur.execute("SELECT name FROM users WHERE phone_number = %s", (phone_without_91,))
        result = cur.fetchone()
    
    elif not result and not phone_number.startswith('91'):
        # Try with '91' prefix
        phone_with_91 = '91' + phone_number
        cur.execute("SELECT name FROM users WHERE phone_number = %s", (phone_with_91,))
        result = cur.fetchone()
    
    cur.close()
    conn.close()
    return result['name'] if result else "User"

# Load messages and menu options
def get_user_language(phone_number):
    """Get user's language preference from database"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Try with original phone number
        cur.execute("SELECT language FROM users WHERE phone_number = %s", (phone_number,))
        result = cur.fetchone()
        
        if not result and phone_number.startswith('91'):
            # Try without '91' prefix
            phone_without_91 = phone_number[2:]
            cur.execute("SELECT language FROM users WHERE phone_number = %s", (phone_without_91,))
            result = cur.fetchone()
        
        elif not result and not phone_number.startswith('91'):
            # Try with '91' prefix
            phone_with_91 = '91' + phone_number
            cur.execute("SELECT language FROM users WHERE phone_number = %s", (phone_with_91,))
            result = cur.fetchone()
        
        return result[0] if result else 'ENGLISH'
    except Exception as e:
        print(f"Error getting user language: {e}")
        return 'ENGLISH'
    finally:
        cur.close()
        conn.close()

def load_messages(phone_number):
    """Load messages in user's preferred language"""
    language = get_user_language(phone_number)
    file_mapping = {
        'ENGLISH': 'english.txt',
        'HINDI': 'hindi.txt',
        'KANNADA': 'kannada.txt',
        'MARATHI': 'marathi.txt'
    }
    
    try:
        filename = file_mapping.get(language, 'english.txt')
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {filename} not found, falling back to english.txt")
        try:
            with open('english.txt', 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print("Error: english.txt not found")
            return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {filename}")
        return {}

# Initialize with English messages
MESSAGES = {}

def reload_messages_for_user(phone_number):
    """Reload messages based on user's language preference"""
    global MESSAGES
    MESSAGES = load_messages(phone_number)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create tables on startup
create_users_table()

def read_lang_from_file():
    global LANG
    try:
        with open('LANG.txt', 'r') as file:
            LANG = file.read().strip()  # Read the contents of the file and remove any surrounding whitespace
    except FileNotFoundError:
        LANG = "ENGLISH"  # Default language if the file doesn't exist

def send_whatsapp_message(message, destination_number):
    url = 'https://api.gupshup.io/wa/api/v1/msg'
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'apikey': os.getenv('WHATSAPP_API_KEY')
    }
    
    payload = {
        'channel': 'whatsapp',
        'source': os.getenv('WHATSAPP_SOURCE'),
        'destination': destination_number,
        'message': f'{{"type": "text", "text": "{message}", "previewUrl": false}}',
        'src.name': os.getenv('WHATSAPP_SRC_NAME')
    }
    
    response = requests.post(url, headers=headers, data=payload)
    
    if response.status_code == 200:
        return response.json()  # Success: return the response in JSON format
    else:
        return f"Failed to send message: {response.status_code}, {response.text}"

async def ten(Dest):
    print("Executing Function")
    url = 'https://api.gupshup.io/sm/api/v1/msg'
    
    lang_menu = MESSAGES["language_menu"]
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
        "source": os.getenv('WHATSAPP_SOURCE'),
        "destination": Dest,
        "src.name": os.getenv('WHATSAPP_SRC_NAME'),
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
        "apikey": os.getenv('WHATSAPP_API_KEY')
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, params=payload, headers=headers)
    
        print("Response from Gupshup API:", response.text)  

def send_whatsapp_message_lan(destination, message_body, footer, header, button_title, tracking_text, src_name):
    url = 'https://api.gupshup.io/wa/api/v1/msg'
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded',
        'apikey': os.getenv('WHATSAPP_API_KEY'),
    }
    payload = {
        'channel': 'whatsapp',
        'source': os.getenv('WHATSAPP_SOURCE'),
        'destination': destination,
        'message': f'{{"type":"quick_reply","content":{{"type":"text","text":"{message_body}","caption":"{footer}","header":"{header}"}},"options":[{{"title":"{button_title}","postbackText":"{tracking_text}"}}]}}',
        'src.name': src_name
    }

    response = requests.post(url, headers=headers, data=payload)
    
    return response    

def send_whatsapp_message_attach(message, destination_number):
    url = 'https://api.gupshup.io/wa/api/v1/msg'
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'apikey': os.getenv('WHATSAPP_API_KEY')
    }
    
    payload = {
        'channel': 'whatsapp',
        'source': os.getenv('WHATSAPP_SOURCE'),
        'destination': destination_number,
        'message': f'{{"type": "text", "text": "https://plum-stephie-67.tiiny.site/", "previewUrl": true}}',
        'src.name': os.getenv('WHATSAPP_SRC_NAME')
    }
    
    response = requests.post(url, headers=headers, data=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        return f"Failed to send message: {response.status_code}, {response.text}"

def send_whatsapp_message_attach_2(message, destination_number):
    url = 'https://api.gupshup.io/wa/api/v1/msg'
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'apikey': os.getenv('WHATSAPP_API_KEY')
    }
    
    payload = {
        'channel': 'whatsapp',
        'source': os.getenv('WHATSAPP_SOURCE'),
        'destination': destination_number,
        'message': f'{{"type": "text", "text": "https://pdfupload.io/docs/5319d0fb", "previewUrl": true}}',
        'src.name': os.getenv('WHATSAPP_SRC_NAME')
    }
    
    response = requests.post(url, headers=headers, data=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        return f"Failed to send message: {response.status_code}, {response.text}"
    
def send_whatsapp_message_attach_1(message, destination_number):
    url = 'https://api.gupshup.io/wa/api/v1/msg'
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'apikey': os.getenv('WHATSAPP_API_KEY')
    }
    
    payload = {
        'channel': 'whatsapp',
        'source': os.getenv('WHATSAPP_SOURCE'),
        'destination': destination_number,
        'message': f'{{"type": "text", "text": "https://pdfupload.io/docs/5b8e8d41", "previewUrl": true}}',
        'src.name': os.getenv('WHATSAPP_SRC_NAME')
    }
    
    response = requests.post(url, headers=headers, data=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        return f"Failed to send message: {response.status_code}, {response.text}"

def send_whatsapp_message_pay(message, destination_number):
    url = 'https://api.gupshup.io/wa/api/v1/msg'
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'apikey': os.getenv('WHATSAPP_API_KEY')
    }
    
    payload = {
        'channel': 'whatsapp',
        'source': os.getenv('WHATSAPP_SOURCE'),
        'destination': destination_number,
        'message': f'{{"type": "text", "text": "https://rzp.io/rzp/6tAlEUab", "previewUrl": true}}',
        'src.name': os.getenv('WHATSAPP_SRC_NAME')  
    }
    
    response = requests.post(url, headers=headers, data=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        return f"Failed to send message: {response.status_code}, {response.text}"
    

def send_whatsapp_message_reset(message, destination_number):
    url = 'https://api.gupshup.io/wa/api/v1/msg'
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'apikey': os.getenv('WHATSAPP_API_KEY')
    }
    
    payload = {
        'channel': 'whatsapp',
        'source': os.getenv('WHATSAPP_SOURCE'),
        'destination': destination_number,
        'message': f'{{"type": "text", "text": "https://secure-pin-reset.vercel.app", "previewUrl": true}}',
        'src.name': os.getenv('WHATSAPP_SRC_NAME')  
    }
    
    response = requests.post(url, headers=headers, data=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        return f"Failed to send message: {response.status_code}, {response.text}"

async def ben(Dest):
    print("Executing Function")
    print(f"Phone number received: {Dest}")
    url = 'https://api.gupshup.io/sm/api/v1/msg'
    
    # Get user name from database
    user_name = get_user_name(Dest)
    
    # If user not found, send registration message
    if user_name == "User":
        message = MESSAGES["messages"]["registration"]
        response = send_whatsapp_message(message, Dest)
        print("Registration message sent:", response)
        return
    
    # Continue with menu for registered users
    title = MESSAGES["welcome_message"].format(user_name=user_name)
    body = MESSAGES["select_options"]
    global_button_title = "Options"
    
    # Get menu structure from messages file
    menu = MESSAGES["menu"]
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
        "source": os.getenv('WHATSAPP_SOURCE'),
        "destination": Dest,
        "src.name": os.getenv('WHATSAPP_SRC_NAME'),
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
        "apikey": os.getenv('WHATSAPP_API_KEY')
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, params=payload, headers=headers)
    
    print("Response from Gupshup API:", response.text)
async def setting(Dest):
    print("Executing Function")
    url = 'https://api.gupshup.io/sm/api/v1/msg'
    
    settings = MESSAGES["settings"]
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
        "source": os.getenv('WHATSAPP_SOURCE'), 
        "destination": Dest,
        "src.name": os.getenv('WHATSAPP_SRC_NAME'),
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
        "apikey": os.getenv('WHATSAPP_API_KEY')
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, params=payload, headers=headers)
    
    print("Response from Gupshup API:", response.text)

async def billu(Dest):
    print("Executing Function")
    url = 'https://api.gupshup.io/sm/api/v1/msg'
    
    bill_payment = MESSAGES["bill_payment"]
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
        "source": os.getenv('WHATSAPP_SOURCE'),
        "destination": Dest,
        "src.name": os.getenv('WHATSAPP_SRC_NAME'),
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
        "apikey": "ioy3vumnhkwcvnttsaz8p4t1flnuheyk"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, params=payload, headers=headers)
    
    print("Response from Gupshup API:", response.text)

async def benny(Dest):
    print("Executing Function")
    url = 'https://api.gupshup.io/sm/api/v1/msg'
    
    # Get menu structure from messages file
    menu = MESSAGES["menu"]
    title = "Thank you"  # This could also be moved to language files
    body = MESSAGES["select_options"]
    global_button_title = "Options"
    
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
        "source": os.getenv('WHATSAPP_SOURCE'),
        "destination": Dest,
        "src.name": os.getenv('WHATSAPP_SRC_NAME'),
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
        "apikey": os.getenv('WHATSAPP_API_KEY')
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, params=payload, headers=headers)
    
    print("Response from Gupshup API:", response.text)

def check_authentication():
    try:
        with open('pass.txt', 'r') as file:
            passcode = file.read().strip()
            return passcode == "4356"
    except FileNotFoundError:
        return False

@app.get("/add-passcode")
async def add_passcode():
    try:
        with open('pass.txt', 'w') as file:
            file.write("4356")
        return {"message": "Passcode added successfully"}
    except Exception as e:
        return {"error": str(e)}

# New API endpoint to get language counts


@app.get("/remove-passcode")
async def remove_passcode():
    try:
        with open('pass.txt', 'w') as file:
            file.write("")
        return {"message": "Passcode removed successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/hello")
def read_hello():
    return {"message": "Hello"}

@app.post("/hello")
async def read_root(request: Request):
    data = await request.json()
    print("Incoming Request:", data)
    
    # Get the user's phone number and load appropriate language messages
    Dest = data["payload"]["source"]
    reload_messages_for_user(Dest)
    print(f"Loaded messages for language: {get_user_language(Dest)}")

    # Check authentication
    if not check_authentication():
        message = "Authentication failed. Service is currently unavailable."
        response = send_whatsapp_message(message, Dest)
        return Response(content="Authentication failed", status_code=401)
    
    if "Hi" in str(data):
        Dest = data["payload"]["source"]
        await ben(Dest)
        print("Function ben() executed for destination:", Dest)
        return Response(content="Message sent", status_code=200)
    
    elif "BALENG" in str(data):
        Dest = data["payload"]["source"]
        
        # Get balance from database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT balance FROM users WHERE phone_number = %s", (Dest,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result:
            balance = result[0]
            message = MESSAGES["messages"]["balance"].format(balance=balance)
        else:
            message = MESSAGES["messages"]["balance_error"]
            
        destination_number = Dest
        response = send_whatsapp_message(message, destination_number)
        print(response)
        await benny(Dest)

    elif "USER002" in str(data):
        Dest = data["payload"]["source"]
        message = MESSAGES["messages"]["recent_transactions"]
        destination_number = Dest
        response = send_whatsapp_message_attach(message, destination_number)
        print(response)
        await benny(Dest)

    elif "BILLS" in str(data):
        Dest = data["payload"]["source"]
        message = MESSAGES["messages"]["account_statement"]
        destination_number = Dest
        response = send_whatsapp_message_attach_1(message, destination_number)
        print(response)
        await benny(Dest)

    elif "DEL" in str(data):
        Dest = data["payload"]["source"]
        message = MESSAGES["messages"]["emi_payment"]
        destination_number = Dest
        response = send_whatsapp_message_pay(message, destination_number)
        print(response)
        await benny(Dest)

    elif "RESETPIN" in str(data):
        Dest = data["payload"]["source"]
        message = MESSAGES["messages"]["password_reset"]
        destination_number = Dest
        response = send_whatsapp_message_reset(message, destination_number)
        print(response)
        await benny(Dest)

    elif any(code in str(data) for code in ["ELEC", "WATER", "FAST"]):
        Dest = data["payload"]["source"]
        message = MESSAGES["messages"]["enter_bill"]
        destination_number = Dest
        response = send_whatsapp_message(message, destination_number)
        print(response)
        return Response(content="Message sent", status_code=200)
        a#wait benny(Dest)

    elif "ADD" in str(data):
        Dest = data["payload"]["source"]
        message = MESSAGES["messages"]["loan_statement"]
        destination_number = Dest
        response = send_whatsapp_message_attach_2(message, destination_number)
        print(response)
        await benny(Dest)

    elif "WLANG" in str(data)  :
        Dest = data["payload"]["source"]
        await ten(Dest)

    elif "DooDu" in str(data):
        Dest = data["payload"]["source"]
        message = MESSAGES["messages"]["fd_scheme"]
        message_body = MESSAGES["messages"]["fd_nominee"]
        button_title = 'Apply'
        footer = '8.5 %'
        header = ''
        tracking_text = 'traackindg123'
        src_name = 'Demofinovate'
        
        destination_number = Dest
        response = send_whatsapp_message(message, destination_number)
        print("WhatsApp message sent:", response)
        
        try:
            response = send_whatsapp_message_lan(destination_number, message_body, footer, header, button_title, tracking_text, src_name)
            print("Additional message sent:", response)
            # Wait for 3 seconds before showing the menu
            await asyncio.sleep(3)
            await benny(Dest)
        except Exception as e:
            print("Error sending additional message:", e)

    elif "PR" in str(data):
        Dest = data["payload"]["source"]
        message = MESSAGES["messages"]["request_sent"]
        destination_number = Dest
        response = send_whatsapp_message(message, destination_number)
        print("WhatsApp message sent:", response)
        await benny(Dest)
    

    elif "TILLS" in str(data):
        Dest = data["payload"]["source"]
        message = MESSAGES["messages"]["request_sent"]
        destination_number = Dest
        response = send_whatsapp_message(message, destination_number)
        print("WhatsApp message sent:", response)
        await benny(Dest)
    elif "DANK" in str(data):
        Dest = data["payload"]["source"]
        await billu(Dest)
        
    elif "SETWET" in str(data):
        Dest = data["payload"]["source"]
        await setting(Dest)
        return Response(content="Message sent", status_code=200)  # Add return statement

    elif "PERCIS" in str(data):
        Dest = data["payload"]["source"]
        message = MESSAGES["messages"]["enter_cheque"]
        destination_number = Dest
        response = send_whatsapp_message(message, destination_number)
        print("WhatsApp message sent:", response)
    elif "FREEZE" in str(data):
        Dest = data["payload"]["source"]
        message = MESSAGES["messages"]["request_sent"]
        destination_number = Dest
        response = send_whatsapp_message(message, destination_number)
        print("WhatsApp message sent:", response)
       
        # Make API call to remove passcode
        try:
            import requests
            api_response = requests.get('http://13.126.242.31:8000/remove-passcode')
            print("Passcode removal response:", api_response.json())
        except Exception as e:
            print("Error removing passcode:", str(e))
        #await benny(Dest)

    elif any(code in str(data) for code in ["tracking123", "xcd123", "dtsi", "vlsi"]):
        Dest = data["payload"]["source"]
        
        # Set language and message based on code
        if "tracking123" in str(data):
            new_lang = "HINDI"
        elif "xcd123" in str(data):
            new_lang = "ENGLISH"
        elif "dtsi" in str(data):
            new_lang = "KANNADA"
        elif "vlsi" in str(data):
            new_lang = "MARATHI"
            
        # Update language in database
        if langupdate(Dest, new_lang):
            # Reload messages in new language
            reload_messages_for_user(Dest)
            # Get success message in the new language
            message = MESSAGES["messages"]["language_changed"][new_lang]
            response = send_whatsapp_message(message, Dest)
        else:
            # Send error message
            error_message = MESSAGES["messages"]["language_update_error"]
            response = send_whatsapp_message(error_message, Dest)
            
        await benny(Dest)
    # Replace the text input handler in your app.py file with this code
    elif data["payload"]["type"] == "text":
        text = data["payload"]["payload"]["text"]
        Dest = data["payload"]["source"]

    print(f"Received text message: '{text}' from {Dest}")

    # Check for 12-digit number with Stop/ISSUE
    if any(word.lower() in text.lower() for word in ["stop", "issue"]):
        numbers = [num for num in text.split() if num.isdigit() and len(num) == 12]
        if numbers:
            message = MESSAGES["messages"]["request_sent"]
            response = send_whatsapp_message(message, Dest)
            print("WhatsApp message sent:", response)
            await benny(Dest)
            return Response(content="Message sent", status_code=200)

    # Handle numeric inputs
    if text.isdigit():
        print(f"Processing numeric input: {text}")
        
        # For bill numbers (any numeric input that's not 4 digits)
        if len(text) != 4:
            print("Processing as bill number")
            
            # Send outstanding amount message
            message = MESSAGES["messages"]["outstanding_amount"]
            response = send_whatsapp_message(message, Dest)
            print(f"Outstanding amount message sent: {response}")
            
            # Generate and store OTP
            import random
            otp = str(random.randint(1000, 9999))
            print(f"Generated OTP: {otp}")
            
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE users 
                SET latest_otp = %s 
                WHERE phone_number = %s
            """, (otp, Dest))
            
            if cur.rowcount == 0:
                # Try alternative phone formats if update failed
                if Dest.startswith('91'):
                    phone_without_91 = Dest[2:]
                    cur.execute("""
                        UPDATE users 
                        SET latest_otp = %s 
                        WHERE phone_number = %s
                    """, (otp, phone_without_91))
                else:
                    phone_with_91 = '91' + Dest
                    cur.execute("""
                        UPDATE users 
                        SET latest_otp = %s 
                        WHERE phone_number = %s
                    """, (otp, phone_with_91))
            
            conn.commit()
            cur.close()
            conn.close()
            print(f"OTP stored in database for user {Dest}")
            
            # Send OTP directly via WhatsApp instead of Twilio
            otp_message = f"Your OTP for bill payment is: {otp}"
            otp_response = send_whatsapp_message(otp_message, Dest)
            print(f"OTP message sent via WhatsApp: {otp_response}")
            
            return Response(content="Message sent", status_code=200)
        
        # For 4-digit OTP verification
        elif len(text) == 4:
            print("Processing as OTP verification")
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Try to find the user with the original phone number
            cur.execute("SELECT latest_otp, balance FROM users WHERE phone_number = %s", (Dest,))
            result = cur.fetchone()
            
            # If not found, try alternative phone formats
            if not result:
                if Dest.startswith('91'):
                    phone_without_91 = Dest[2:]
                    cur.execute("SELECT latest_otp, balance FROM users WHERE phone_number = %s", (phone_without_91,))
                    result = cur.fetchone()
                else:
                    phone_with_91 = '91' + Dest
                    cur.execute("SELECT latest_otp, balance FROM users WHERE phone_number = %s", (phone_with_91,))
                    result = cur.fetchone()
            
            print(f"Database result for OTP verification: {result}")
            
            if result and result[0] == text:
                stored_otp, current_balance = result[0], result[1] or 5000  # Default to 5000 if balance is None
                
                if current_balance >= 597:  # Use the actual amount from the message
                    new_balance = current_balance - 597
                    cur.execute("""
                        UPDATE users 
                        SET balance = %s, latest_otp = NULL 
                        WHERE phone_number = %s
                    """, (new_balance, Dest))
                    conn.commit()
                    message = MESSAGES["messages"]["payment_success"].format(new_balance=new_balance)
                else:
                    message = MESSAGES["messages"]["insufficient_balance"]
            else:
                message = MESSAGES["messages"]["invalid_otp"]
            
            cur.close()
            conn.close()
            response = send_whatsapp_message(message, Dest)
            print("Response message sent:", response)
            
            # Show the main menu after OTP verification
            await benny(Dest)
            return Response(content="Message sent", status_code=200)
    
    # If no special patterns match, show main menu
    await ben(Dest)
    return Response(content="Message sent", status_code=200)

    # # Check for 12-digit number with Stop/ISSUE or 4/6 digit numbers
    # elif data["payload"]["type"] == "text":
    #     text = data["payload"]["payload"]["text"]
    #     Dest = data["payload"]["source"]

    #     # Check for 12-digit number with Stop/ISSUE
    #     if any(word.lower() in text.lower() for word in ["stop", "issue"]):
    #         numbers = [num for num in text.split() if num.isdigit() and len(num) == 12]
    #         if numbers:
    #             message = MESSAGES["messages"]["request_sent"]
    #             response = send_whatsapp_message(message, Dest)
    #             print("WhatsApp message sent:", response)
    #             await benny(Dest)
    #             return Response(content="Message sent", status_code=200)

    #     # Handle numeric inputs (4 or 6 digits)
    #     if text.isdigit():
    #         if len(text) == 6:
    #             # Handle 6-digit check number
    #             message = MESSAGES["messages"]["outstanding_amount"]
    #             response = send_whatsapp_message(message, Dest)
    #             print("WhatsApp message sent:", response)
                
    #             # Generate and store OTP
    #             import random
    #             otp = str(random.randint(1000, 9999))
    #             conn = get_db_connection()
    #             cur = conn.cursor()
    #             cur.execute("""
    #                 UPDATE users 
    #                 SET latest_otp = %s 
    #                 WHERE phone_number = %s
    #             """, (otp, Dest))
    #             conn.commit()
    #             cur.close()
    #             conn.close()
                
    #             # Send OTP via Twilio
    #             import requests
    #             url = 'https://api.twilio.com/2010-04-01/Accounts/{os.getenv("TWILIO_ACCOUNT_SID")}/Messages.json'
    #             auth = (os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
    #             data = {
    #                 'To': f'{+Dest}',
    #                 'From': os.getenv('TWILIO_PHONE_NUMBER'),
    #                 'Body': f'OTP for Transaction: {otp}'
    #             }
    #             twilio_response = requests.post(url, data=data, auth=auth)
    #             print("Twilio Response:", twilio_response.json())
    #             return Response(content="Message sent", status_code=200)
            
    #         elif len(text) == 4:
    #             # Handle 4-digit OTP verification
    #             conn = get_db_connection()
    #             cur = conn.cursor()
    #             cur.execute("SELECT latest_otp, balance FROM users WHERE phone_number = %s", (Dest,))
    #             result = cur.fetchone()
                
    #             if result and result[0] == text:
    #                 stored_otp, current_balance = result[0], result[1]
    #                 if current_balance >= 3000:
    #                     new_balance = current_balance - 3000
    #                     cur.execute("""
    #                         UPDATE users 
    #                         SET balance = %s, latest_otp = NULL 
    #                         WHERE phone_number = %s
    #                     """, (new_balance, Dest))
    #                     conn.commit()
    #                     message = MESSAGES["messages"]["payment_success"].format(new_balance=new_balance)
    #                 else:
    #                     message = MESSAGES["messages"]["insufficient_balance"]
    #             else:
    #                 message = MESSAGES["messages"]["invalid_otp"]
                
    #             cur.close()
    #             conn.close()
    #             response = send_whatsapp_message(message, Dest)
    #             print("Response message sent:", response)
    #             return Response(content="Message sent", status_code=200)

        # If no special patterns match, show main menu
    #     await ben(Dest)
    #     return Response(content="Message sent", status_code=200)
    # else:
    #     Dest = data["payload"]["source"]
    #     await ben(Dest)
    #     print("Function ben() executed for destination:", Dest)
    #     return Response(content="Message sent", status_code=200)

# Service Request model from new.py
class ServiceRequest(BaseModel):
    title: str
    icon: str
    description: str

# Services data from new.py
services = {
    "finchat": {
        "id": 1,
        "title": "FinChat - Banking Hub",
        "icon": "https://finchat.Demofinovate.com/assets/images/icons/finchat.png",
        "description":"Welcome to the FinChat Banking Hub! This is where you can find all the latest news, updates, and resources related to banking and finance. Whether you're a financial professional or just interested in learning more about the industry, you've come to the right place. Stay tuned for the latest news and insights from the world of banking and finance.",
        "link": "/dashboard-whatsapp"
    },
    "kyc": {
        "id": 2,
        "title": "KYC Connect",
        "icon": "https://finchat.Demofinovate.com/assets/images/icons/kyc.png",
        "description": "Streamline your KYC process with secure, real-time document collection and verification via WhatsApp.",
        "link": "/kyc-connect"
    },
    "coop-pulse": {
        "id": 3,
        "title": "Co-op Pulse",
        "icon": "https://finchat.Demofinovate.com/assets/images/icons/coop-pulse.png",
        "description": "Engage with cooperative bank members using interactive sessions, updates, and voting through WhatsApp.",
        "link": "/co-op-pulse"

    },
    "customer-support": {
        "id": 4,
        "title": "Customer Support Chat",
        "icon": "https://finchat.Demofinovate.com/assets/images/icons/customer-support.png",
        "description": "Enhance customer experience with instant assistance for banking queries, issue resolution, and AI-powered navigation via WhatsApp.",
        "link": "/customer-support"
    },
    "notify": {
        "id": 5,
        "title": "Notify",
        "icon": "https://finchat.Demofinovate.com/assets/images/icons/notify.png",
        "description": "Stay informed with real-time updates, alerts, and notifications via WhatsApp.",
        "link": "/notification"

    }
}

# Service endpoints from new.py

# Dependency to provide a database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint to read all notifications
@app.get("/notifications/")
def read_notifications(db: Session = Depends(get_db)):
    notifications = db.query(CRRbiNotification).all()
    return notifications

# Endpoint to read a specific notification by its primary key (id)
@app.get("/notifications/{notification_id}")
def read_notification(notification_id: int, db: Session = Depends(get_db)):
    notification = db.query(CRRbiNotification).filter(CRRbiNotification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

# New API endpoint to get table details

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False, log_level="debug",
                workers=1, limit_concurrency=10, limit_max_requests=100)
