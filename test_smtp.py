#!/usr/bin/env python3
import smtplib
from email.mime.text import MIMEText

# Gmail SMTP settings
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
USERNAME = 'zero850x@gmail.com'
PASSWORD = '990prot500'

try:
    # Create message
    msg = MIMEText('Test email from Python')
    msg['Subject'] = 'Test Email'
    msg['From'] = USERNAME
    msg['To'] = USERNAME
    
    print(f"Connecting to {SMTP_SERVER}:{SMTP_PORT}...")
    smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    print("Connected!")
    
    print("Starting TLS...")
    smtp.starttls()
    print("TLS started!")
    
    print(f"Logging in as {USERNAME}...")
    smtp.login(USERNAME, PASSWORD)
    print("Login successful!")
    
    print("Sending test email...")
    smtp.send_message(msg)
    print("Email sent!")
    
    smtp.quit()
    print("Test completed successfully!")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"SMTP authentication error: {e}")
except Exception as e:
    print(f"Error: {e}")