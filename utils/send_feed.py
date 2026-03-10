
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json
import os
from dotenv import load_dotenv
from utils.render_templates import render_discord
# from utils.newsletter import generate_html_newsletter
from utils.newsletter_v2 import generate_html_newsletter, generate_email_newsletter
from utils.feed_state import get_unsent_papers, mark_feed_batch_as_sent
from utils.content_generation import generate_tldr
from utils.subscriber_manager import SubscriberManager
from agents.ollama_agent import OllamaAgent

load_dotenv()

def send_email(feed_items, subscribers, smtp_user, smtp_pass, tldr=None):
    # This legacy function signature is kept but logic is moved to main block for personalization
    # Or we can adapt it. But simpler to fully control in main block as per plan.
    pass 

if __name__ == "__main__":
    # Example usage
    discord_web_hook = "https://discord.com/api/webhooks/1435121885187670088/-QO-bAi_EsWGo8usBFWnO-QBGjp8Qx6ICZp5OvtiUcMGGUC7r_iYn6RtPTt94yHGtkPi"
    
    # Initialize LLM for TL;DR
    llm = OllamaAgent(model="gemma3:4b", host="http://127.0.0.1:11434", temperature=0.1, seed=41, num_ctx=61440)
    
    # Initialize Subscriber Manager
    sub_manager = SubscriberManager()
    
    # Add a default subscriber if empty (for testing/first run)
    if not sub_manager.get_active_subscribers():
        print("No subscribers found in DB. Adding default.")
        sub_manager.add_subscriber("tejastejatej@gmail.com", ["AI", "Deep Learning", "LLM"])

    subscribers = sub_manager.get_active_subscribers()
    
    if not subscribers:
        print("No active subscribers.")
    else:
        # Optimization: Fetch union of all topics
        all_topics = set()
        for sub in subscribers:
            all_topics.update(sub['topics'])
        
        print(f"Fetching papers for combined topics: {all_topics}")
        
        # Fetch papers for ALL topics (union)
        all_papers = get_unsent_papers(
            days=7, 
            limit=50, # Increased limit for broader search
            topics=list(all_topics), 
            exclude_sent=False
        )
        
        if not all_papers:
            print("No new papers found for any topic.")
        else:
            print(f"Found {len(all_papers)} total papers. Processing per subscriber...")
            
            papers_sent_ids = set()
            smtp_user = os.getenv("SMTP_USER", "user@example.com")
            smtp_pass = os.getenv("SMTP_PASS", "password")

            # Connect SMTP once
            if smtp_user == "user@example.com":
                 print("Please set SMTP_USER and SMTP_PASS environment variables.")
            else:
                try:
                    server = smtplib.SMTP("smtp.gmail.com", 587)
                    server.starttls()
                    server.login(smtp_user, smtp_pass)
                    
                    for sub in subscribers:
                        user_email = sub['email']
                        user_topics = [t.lower() for t in sub['topics']]
                        
                        # Personalize: Filter papers for this user
                        user_papers = []
                        for paper in all_papers:
                            # Check if paper matches any of user's topics
                            paper_topics = [t.lower() for t in paper.get('topics', [])]
                            
                            if any(ut in paper_dict_topic for ut in user_topics for paper_dict_topic in paper_topics):
                                user_papers.append(paper)
                            elif not paper_topics and "ai" in user_topics: # Fallback for untagged
                                user_papers.append(paper)
                        
                        if not user_papers:
                            print(f"No papers matching topics {user_topics} for {user_email}")
                            continue

                        print(f"Generating personalized TL;DR for {user_email} ({len(user_papers)} papers)...")
                        tldr = generate_tldr(user_papers, llm, max_papers=10)
                        
                        # Render HTML - Use email specific version for GMAIL friendliness
                        html_content = generate_email_newsletter(user_papers, title="The Research Radar", tldr=tldr, issue_number="043")
                        
                        msg = MIMEMultipart("alternative")
                        msg["Subject"] = f"The Research Radar: {len(user_papers)} New Papers"
                        msg["From"] = "The Research Radar"
                        msg["To"] = user_email
                        msg.attach(MIMEText(html_content, "html"))
                        
                        try:
                            server.send_message(msg)
                            print(f"Email sent to {user_email}")
                            for p in user_papers:
                                papers_sent_ids.add(p['id'])
                        except Exception as e:
                            print(f"Failed to send to {user_email}: {e}")

                    server.quit()
                    
                    # Mark sent papers
                    if papers_sent_ids:
                        count = mark_feed_batch_as_sent(list(papers_sent_ids))
                        print(f"Marked {count} unique papers as sent.")
                        
                except Exception as e:
                    print(f"SMTP Error: {e}")
