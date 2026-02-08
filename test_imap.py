#!/usr/bin/env python3
import imaplib
import ssl

# Gmail IMAP settings
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993
USERNAME = 'zero850x@gmail.com'
PASSWORD = '990prot500'

try:
    # Create SSL context
    context = ssl.create_default_context()
    
    # Connect to IMAP server
    print(f"Connecting to {IMAP_SERVER}:{IMAP_PORT}...")
    imap = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=context)
    print("Connected successfully!")
    
    # Try to login
    print(f"Logging in as {USERNAME}...")
    imap.login(USERNAME, PASSWORD)
    print("Login successful!")
    
    # List folders
    print("Listing folders...")
    typ, folders = imap.list()
    if typ == 'OK':
        print("Folders:")
        for folder in folders:
            print(f"  {folder.decode('utf-8')}")
    
    # Logout
    imap.logout()
    print("Test completed successfully!")
    
except imaplib.IMAP4.error as e:
    print(f"IMAP error: {e}")
except Exception as e:
    print(f"Error: {e}")