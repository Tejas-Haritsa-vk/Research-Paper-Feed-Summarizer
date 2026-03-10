import re
import json

def parse_verification_email(email_body):
    """
    Parses the Research Radar verification email format to extract user details.
    """
    
    # Define regex patterns for each field based on the email structure
    patterns = {
        "email": r"Email:\s*(.*)",
        "topics": r"Topics:\s*(.*)",
        "date": r"Date:\s*(.*)",
        "platform": r"Platform:\s*(.*)",
        "version": r"Version:\s*(.*)"
    }
    
    extracted_data = {}
    
    for key, pattern in patterns.items():
        match = re.search(pattern, email_body)
        if match:
            # Extract and clean the value
            extracted_data[key] = match.group(1).strip()
        else:
            extracted_data[key] = None

    return extracted_data

# Example usage with the format provided
raw_email_content = """
Hello Research Radar Team,

Please verify my account.

--- USER DETAILS ---
Email: tejastejatej@gmail.com
Topics: LLMs,CV,RL
Date: 29-12-2025

Platform: Email Verification
Version: 2.3.0
"""

if __name__ == "__main__":
    result = parse_verification_email(raw_email_content)
    
    # Output the result as structured JSON
    print(json.dumps(result, indent=4))