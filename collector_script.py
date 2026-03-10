import imaplib
import email
from email.header import decode_header
import time
import os
from utils.subscriber_manager import SubscriberManager
from dotenv import load_dotenv
from email_parser import parse_verification_email

load_dotenv()

# --- CONFIGURATION ---
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")  # Use an App Password, not your real password
IMAP_SERVER = os.getenv("IMAP_SERVER")   # Use your provider's IMAP server
POLL_INTERVAL = os.getenv("POLL_INTERVAL")               # Seconds between checks
SEARCH_SUBJECT = os.getenv("SEARCH_SUBJECT")

subscriber_manager = SubscriberManager()

def clean_text(text):
    return text.strip().replace('\n', '').replace('\r', '')

def process_emails():
    try:
        # 1. Connect and Login
        print(f"[*] Connecting to {IMAP_SERVER}...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        print(f"[+] Login successful.")
        mail.select("inbox")

        # 2. Search for unread emails from our website
        # We search for the specific subject line we set in the frontend
        print(f"[*] Searching for UNSEEN emails with subject: {SEARCH_SUBJECT}...")
        status, messages = mail.search(None, f'(UNSEEN SUBJECT "{SEARCH_SUBJECT}")')
        
        if status != 'OK':
            print(f"[!] Search failed with status: {status}")
            return

        email_ids = messages[0].split()
        
        if not email_ids:
            print(f"[*] No new signals found.")
            return

        print(f"[*] Found {len(email_ids)} new signals. Processing...")

        for e_id in email_ids:
            # Fetch the email body
            res, msg_data = mail.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Extract Body
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                    else:
                        body = msg.get_payload(decode=True).decode()

                    # Parse using email_parser utility
                    try:
                        parsed_data = parse_verification_email(body)
                        sub_email = parsed_data.get("email")
                        sub_interests = parsed_data.get("topics")
                        
                        if sub_email:
                            # Convert interests string to list (handling comma separation)
                            interests_list = []
                            if sub_interests:
                                # Split by comma or whitespace if needed, but the parser regex gets the whole line
                                # Standardizing on comma separation as per email_parser's example
                                interests_list = [i.strip() for i in sub_interests.split(",") if i.strip()]
                            
                            if not interests_list:
                                interests_list = None # Will use defaults in add_subscriber
                                
                            success = subscriber_manager.add_subscriber(sub_email, interests_list)
                            if success:
                                print(f"[+] Saved to DB: {sub_email}")
                            else:
                                print(f"[!] DB insertion failed for: {sub_email}")
                    except Exception as parse_err:
                        print(f"[!] Parsing error on packet {e_id}: {parse_err}")

            # 4. Mark as read (already handled by fetching UNSEEN and selecting INBOX)
            # Or explicitly delete it if you prefer:
            # mail.store(e_id, '+FLAGS', '\\Deleted')

        mail.close()
        mail.logout()

    except Exception as e:
        print(f"[!] Connection Error: {e}")

if __name__ == "__main__":
    print(f"--- THE RESEARCH RADAR COLLECTOR ONLINE ---")
    print(f"[*] Monitoring {EMAIL_USER} for signals...")
    process_emails() # single run

    ## Loop for continuous monitoring
    # while True:
    #     process_emails()
    #     time.sleep(POLL_INTERVAL)
