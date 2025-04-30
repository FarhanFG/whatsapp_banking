import asyncio
import random
import json
from fastapi import APIRouter, Response, Request, Depends, HTTPException
from sqlalchemy.orm import Session

from .dependencies import verify_authentication, get_db_session
from .schemas import ServiceRequest
from db.models import CRRbiNotification
from db.repositories import (
    get_language_counts, get_age_group_utilization, get_table_details
)
from services.auth_services import (
    add_passcode, remove_passcode, generate_and_send_otp, verify_user_otp
)
from services.user_service import (
    get_user_info, change_user_language, get_user_account_balance,
    update_account_balance, reload_messages_for_user, get_messages
)
from services.payment_service import process_payment, check_outstanding_amount
from whatsapp.clients import (
    send_text_message, send_link_message, send_quick_reply_message
)
from whatsapp.menu_builder import (
    send_main_menu, send_language_menu, send_settings_menu, send_bill_payment_menu
)
from config.settings import SERVICES

router = APIRouter()

@router.get("/hello")
def read_hello():
    return {"message": "Hello"}

@router.post("/hello")
async def read_root(request: Request, auth: bool = Depends(verify_authentication)):
    data = await request.json()
    print("Incoming Request:", data)
    
    # Get the user's phone number and load appropriate language messages
    Dest = data["payload"]["source"]
    messages = reload_messages_for_user(Dest)
    print(f"Loaded messages for language: {get_user_info(Dest)['language']}")
    
    if "Hi" in str(data):
        await send_main_menu(Dest, messages, get_user_info(Dest)["name"])
        print("Function send_main_menu() executed for destination:", Dest)
        return Response(content="Message sent", status_code=200)
    
    elif "BALENG" in str(data):
        balance = get_user_account_balance(Dest)
        
        if balance is not None:
            message = messages["messages"]["balance"].format(balance=balance)
        else:
            message = messages["messages"]["balance_error"]
            
        response = send_text_message(message, Dest)
        print(response)
        await send_main_menu(Dest, messages, get_user_info(Dest)["name"])

    elif "USER002" in str(data):
        message = messages["messages"]["recent_transactions"]
        response = send_link_message(Dest, "https://plum-stephie-67.tiiny.site/", True)
        print(response)
        await send_main_menu(Dest, messages, get_user_info(Dest)["name"])

    elif "BILLS" in str(data):
        message = messages["messages"]["account_statement"]
        response = send_link_message(Dest, "https://pdfupload.io/docs/5319d0fb", True)
        print(response)
        await send_main_menu(Dest, messages, get_user_info(Dest)["name"])

    elif "DEL" in str(data):
        message = messages["messages"]["emi_payment"]
        response = send_link_message(Dest, "https://rzp.io/rzp/6tAlEUab", True)
        print(response)
        await send_main_menu(Dest, messages, get_user_info(Dest)["name"])

    elif "RESETPIN" in str(data):
        message = messages["messages"]["password_reset"]
        response = send_link_message(Dest, "https://secure-pin-reset.vercel.app", True)
        print(response)
        await send_main_menu(Dest, messages, get_user_info(Dest)["name"])

    elif any(code in str(data) for code in ["ELEC", "WATER", "FAST"]):
        message = messages["messages"]["enter_bill"]
        response = send_text_message(message, Dest)
        print(response)

    elif "ADD" in str(data):
        message = messages["messages"]["loan_statement"]
        response = send_link_message(Dest, "https://pdfupload.io/docs/5b8e8d41", True)
        print(response)
        await send_main_menu(Dest, messages, get_user_info(Dest)["name"])

    elif "WLANG" in str(data):
        await send_language_menu(Dest, messages)

    elif "DooDu" in str(data):
        message = messages["messages"]["fd_scheme"]
        message_body = messages["messages"]["fd_nominee"]
        button_title = 'Apply'
        footer = '8.5 %'
        header = ''
        tracking_text = 'traackindg123'
        
        response = send_text_message(message, Dest)
        print("WhatsApp message sent:", response)
        
        try:
            response = send_quick_reply_message(Dest, message_body, footer, header, button_title, tracking_text)
            print("Additional message sent:", response)
            # Wait for 3 seconds before showing the menu
            await asyncio.sleep(3)
            await send_main_menu(Dest, messages, get_user_info(Dest)["name"])
        except Exception as e:
            print("Error sending additional message:", e)

    elif "PR" in str(data):
        message = messages["messages"]["request_sent"]
        response = send_text_message(message, Dest)
        print("WhatsApp message sent:", response)
        await send_main_menu(Dest, messages, get_user_info(Dest)["name"])
    
    elif "TILLS" in str(data):
        message = messages["messages"]["request_sent"]
        response = send_text_message(message, Dest)
        print("WhatsApp message sent:", response)
        await send_main_menu(Dest, messages, get_user_info(Dest)["name"])
        
    elif "DANK" in str(data):
        await send_bill_payment_menu(Dest, messages)
        
    elif "SETWET" in str(data):
        await send_settings_menu(Dest, messages)
        return Response(content="Message sent", status_code=200)

    elif "PERCIS" in str(data):
        message = messages["messages"]["enter_cheque"]
        response = send_text_message(message, Dest)
        print("WhatsApp message sent:", response)
        
    elif "FREEZE" in str(data):
        message = messages["messages"]["request_sent"]
        response = send_text_message(message, Dest)
        print("WhatsApp message sent:", response)
       
        # Make API call to remove passcode
        try:
            remove_passcode()
            print("Passcode removed")
        except Exception as e:
            print("Error removing passcode:", str(e))

    elif any(code in str(data) for code in ["tracking123", "xcd123", "dtsi", "vlsi"]):
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
        if change_user_language(Dest, new_lang):
            # Get success message in the new language
            messages = reload_messages_for_user(Dest)
            message = messages["messages"]["language_changed"][new_lang]
            response = send_text_message(message, Dest)
        else:
                        # Send error message
            error_message = messages["messages"]["language_update_error"]
            response = send_text_message(error_message, Dest)
            
        await send_main_menu(Dest, messages, get_user_info(Dest)["name"])
        
    # Check for 12-digit number with Stop/ISSUE or 4/6 digit numbers
    elif data["payload"]["type"] == "text":
        text = data["payload"]["payload"]["text"]

        # Check for 12-digit number with Stop/ISSUE
        if any(word.lower() in text.lower() for word in ["stop", "issue"]):
            numbers = [num for num in text.split() if num.isdigit() and len(num) == 12]
            if numbers:
                message = messages["messages"]["request_sent"]
                response = send_text_message(message, Dest)
                print("WhatsApp message sent:", response)
                await send_main_menu(Dest, messages, get_user_info(Dest)["name"])
                return Response(content="Message sent", status_code=200)

        # Handle numeric inputs (4 or 6 digits)
        if text.isdigit():
            if len(text) == 6:
                # Handle 6-digit check number
                message = messages["messages"]["outstanding_amount"]
                response = send_text_message(message, Dest)
                print("WhatsApp message sent:", response)
                
                # Generate and send OTP
                success, twilio_response = generate_and_send_otp(Dest)
                if success:
                    print("OTP sent via Twilio:", twilio_response)
                else:
                    print("Failed to send OTP:", twilio_response)
                    
                return Response(content="Message sent", status_code=200)
            
            elif len(text) == 4:
                # Handle 4-digit OTP verification
                is_valid, balance = verify_user_otp(Dest, text)
                
                if is_valid:
                    if balance >= 3000:
                        new_balance = balance - 3000
                        if update_account_balance(Dest, new_balance):
                            message = messages["messages"]["payment_success"].format(new_balance=new_balance)
                        else:
                            message = messages["messages"]["payment_error"]
                    else:
                        message = messages["messages"]["insufficient_balance"]
                else:
                    message = messages["messages"]["invalid_otp"]
                
                response = send_text_message(message, Dest)
                print("Response message sent:", response)
                return Response(content="Message sent", status_code=200)

        # If no special patterns match, show main menu
        await send_main_menu(Dest, messages, get_user_info(Dest)["name"])
        return Response(content="Message sent", status_code=200)
    else:
        await send_main_menu(Dest, messages, get_user_info(Dest)["name"])
        print("Function send_main_menu() executed for destination:", Dest)
        return Response(content="Message sent", status_code=200)

@router.get("/add-passcode")
async def add_passcode_endpoint():
    return add_passcode()

@router.get("/remove-passcode")
async def remove_passcode_endpoint():
    return remove_passcode()



@router.get("/notifications/")
def read_notifications(db: Session = Depends(get_db_session)):
    notifications = db.query(CRRbiNotification).all()
    return notifications

@router.get("/notifications/{notification_id}")
def read_notification(notification_id: int, db: Session = Depends(get_db_session)):
    notification = db.query(CRRbiNotification).filter(CRRbiNotification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

