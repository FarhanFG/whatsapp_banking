Overview
This project implements a WhatsApp Banking interface that connects to a banking system backend, allowing customers to perform various banking operations through the familiar WhatsApp platform. The system supports multiple languages and provides an interactive menu-driven interface for easy navigation.

Features:

Account Services:
Balance Inquiry: Check your account balance instantly
Recent Transactions: View your last 7 transactions
Account Statement: Request and receive account statements

Loan Services:
EMI Payment: Pay your loan EMIs directly through WhatsApp
Loan Statement: Access your loan statement documents

Fixed Deposits & Bill Payments:

Apply for FD: Apply for fixed deposits with competitive interest rates
Bill Payments: Pay utility bills (electricity, water) and vehicle-related bills (FASTag)

Settings:

PIN Reset: Reset your banking PIN securely
Language Preferences: Choose from multiple language options (English, Hindi, Kannada, Marathi)

Technical Architecture:

Backend: FastAPI (Python)
Database: PostgreSQL for user data and transaction storage
WhatsApp Integration: Gupshup API for WhatsApp Business messaging
Authentication: OTP-based verification for secure transactions
Multilingual Support: JSON-based language configuration files

API Endpoints:

Endpoint	Method	Description
/hello	GET	Simple health check endpoint
/hello	POST	Main webhook for WhatsApp message processing
/add-passcode	GET	Add authentication passcode to the system
/notifications/	GET	Retrieve all RBI notifications
/notifications/{notification_id}	GET	Retrieve a specific notification by ID

How It Works:

User Interaction: Users send messages to the WhatsApp number
Authentication: System identifies users by their phone number
Menu Navigation: Interactive menus guide users to their desired service
Service Execution: Requested banking operations are performed
Response: System responds with appropriate information in the user's preferred language

Language Support:
The system supports multiple languages through configuration files:

English (default)
Hindi
Kannada
Marathi
Users can change their language preference at any time through the settings menu.

Security Features
Secure Links: External links for statements and payments
Session Management: Authentication token management
PIN Reset: Secure process for resetting banking PINs

Database Structure:
The application uses PostgreSQL with the following main tables:
users: Stores user information including phone number, name, language preference, and OTP data
cr_rbi_notifications: Stores RBI notifications for users

Environment Configuration:
The application uses environment variables for configuration. Required variables include:

Database credentials
WhatsApp API credentials
External service integration details
Installation & Setup
Clone the repository
Install dependencies:
pip install -r requirements.txt

Copy


Set up environment variables in a .env file
Run the application:
uvicorn app:app --host 0.0.0.0 --port 8000

Copy


Usage Examples:

Checking Account Balance
User selects "Account Services" from the main menu
User selects "Balance" option
System authenticates the user and displays the current balance
Paying Bills
User selects "FD & Bills" from the main menu
User selects "Bill Payments" option
User chooses the bill type (Electricity, Water, FASTag)
User enters the bill number
System processes the payment after OTP verification

License
This project is licensed under the MIT License - see the LICENSE file for details.

