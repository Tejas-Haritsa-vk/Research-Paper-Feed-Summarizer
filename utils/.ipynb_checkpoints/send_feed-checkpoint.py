import smtplib
from email.mime.text import MIMEText
import requests
from utils.render_templates import render_discord, render_email

def send_email(feed_items, to_email, smtp_user, smtp_pass):
    msg = MIMEText(render_email(feed_items), "html")
    msg["Subject"] = "🧠 Weekly AI Research Digest"
    msg["From"] = smtp_user
    msg["To"] = to_email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)

def send_discord(feed_items, source, webhook_url, batch_size=5):
    for i in range(0, len(feed_items), batch_size):
        payload = render_discord(feed_items[i:i+batch_size], source)
        requests.post(webhook_url, json=payload)


if __name__ == "__main__":
    # Example usage
    discord_web_hook = "https://discord.com/api/webhooks/1435121885187670088/-QO-bAi_EsWGo8usBFWnO-QBGjp8Qx6ICZp5OvtiUcMGGUC7r_iYn6RtPTt94yHGtkPi"
    # send_email(feed_items, "recipient@example.com", "you@gmail.com", "YOUR_APP_PASSWORD")
    send_discord(feed_items, discord_web_hook)
