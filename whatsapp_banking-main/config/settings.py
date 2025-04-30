import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_HOST = os.getenv('DB_HOST', '13.126.242.31')
DB_NAME = os.getenv('DB_NAME', 'whatzapp')
DB_USER = os.getenv('DB_USER', 'far')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'Finovate@2023')

# SQLAlchemy database URL
DATABASE_URL = "postgresql://dev_cbs_admin:Finovate%402023@13.126.242.31:5432/cr_dev"

# WhatsApp API configuration
WHATSAPP_API_KEY = "ioy3vumnhkwcvnttsaz8p4t1flnuheyk"
WHATSAPP_SOURCE_NUMBER = "917834811114"
WHATSAPP_SRC_NAME = "Demofinovate"

# Twilio configuration
TWILIO_ACCOUNT_SID = "AC7a5e6d3727d4e6cd8c66a619cc364aa2"
TWILIO_AUTH_TOKEN = "3f7e9ba092833226f054044d00a39c10"
TWILIO_PHONE_NUMBER = "+16084077139"

# Services data
SERVICES = {
    "finchat": {
        "id": 1,
        "title": "FinChat - Banking Hub",
        "icon": "https://finchat.Demofinovate.com/assets/images/icons/finchat.png",
        "description":"Welcome to the FinChat Banking Hub! This is where you can find all the latest news, updates, and resources related to banking and finance.",
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
