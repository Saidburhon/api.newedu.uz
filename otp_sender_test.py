#!/usr/bin/env python3
import requests
import json
import time
import hashlib
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# SMS API Configuration
API_BASE_URL = "https://routee.sayqal.uz"
SMS_ENDPOINT = "/sms/TransmitSMS"

# These would typically be stored securely in environment variables
# For this test script, we'll define them here
USERNAME = "newedu"  # Replace with your actual username
SECRET_KEY = "75b33e87e4bad463e51c4d0c73fda316"  # Replace with your actual secret key
SERVICE_ID = 2  # Replace with your actual service ID

# Function to generate a random OTP code
def generate_otp(length=6):
    """Generate a random numeric OTP code of specified length"""
    digits = "0123456789"
    otp = ""
    for _ in range(length):
        otp += random.choice(digits)
    return otp

# Function to generate the access token for SMS API
def generate_transmit_access_token(username, secret_key, utime):
    """Generate the access token required for the SMS API"""
    access_string = f"TransmitSMS {username} {secret_key} {utime}"
    return hashlib.md5(access_string.encode()).hexdigest()

# Function to send OTP via SMS
def send_otp(phone_number, otp_code):
    """Send OTP code to the specified phone number"""
    # Current Unix timestamp
    utime = int(time.time())
    
    # Generate access token
    access_token = generate_transmit_access_token(USERNAME, SECRET_KEY, utime)
    
    # Prepare headers
    headers = {
        "Content-Type": "application/json",
        "X-Access-Token": access_token
    }
    
    # Prepare SMS payload
    payload = {
        "utime": utime,
        "username": USERNAME,
        "service": {
            "service": SERVICE_ID
        },
        "message": {
            "smsid": str(int(time.time())),  # Using timestamp as a unique ID
            "phone": phone_number,
            "text": f"Tikoncha mobil ilovasida ro'yxatdan o'tish uchun tasdiqlash kodi - {otp_code}"
        }
    }
    
    # Send the request
    try:
        response = requests.post(
            f"{API_BASE_URL}{SMS_ENDPOINT}", 
            headers=headers, 
            data=json.dumps(payload)
        )
        
        # Process the response
        if response.status_code == 200:
            result = response.json()
            print("SMS sent successfully!")
            print(f"Transaction ID: {result.get('transactionid')}")
            print(f"SMS ID: {result.get('smsid')}")
            print(f"Parts: {result.get('parts')}")
            return True, result
        else:
            error = response.json()
            print(f"Error sending SMS: {error.get('errorMsg', 'Unknown error')}")
            print(f"Error code: {error.get('errorCode', 'N/A')}")
            return False, error
    
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return False, {"error": str(e)}

# Main function
def main():
    print("===== OTP Sender Test =====\n")
    
    # Get phone number from user input
    while True:
        phone_number = input("Enter phone number (format: 998XXXXXXXXX): ")
        
        # Validate phone number format
        if not phone_number.startswith("998") or not phone_number.isdigit() or len(phone_number) != 12:
            print("Invalid phone number format. Please use format: 998XXXXXXXXX")
            continue
        
        break
    
    # Generate OTP
    otp_code = generate_otp()
    print(f"\nGenerated OTP: {otp_code}")
    
    # Confirm sending
    confirm = input(f"\nSend OTP to {phone_number}? (y/n): ").lower()
    if confirm != 'y':
        print("Operation cancelled.")
        return
    
    # Send OTP
    print("\nSending OTP...")
    success, result = send_otp(phone_number, otp_code)
    print(success, result)
    if success:
        print("\nOTP sent successfully!")
    else:
        print("\nFailed to send OTP.")

# Run the script
if __name__ == "__main__":
    main()
