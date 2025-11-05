def render_email(feed_items):
    feed_html = ""
    for item in feed_items:
        feed_html += f"""
        <div style="margin-bottom:24px;border-left:4px solid #6366f1;padding-left:12px;">
            <h3 style="margin:0;font-size:18px;color:#111827;">{item['title']}</h3>
            <p style="margin:6px 0 10px 0;color:#374151;font-size:14px;line-height:1.5;">{item['summary']}</p>
            <p style="margin:4px 0 10px 0;color:#6b7280;font-size:12px;">
                {' • '.join(item['tags'])} | {item['source']} | {item['date']}
            </p>
            <a href="{item['link']}" 
               style="display:inline-block;background:#6366f1;color:white;text-decoration:none;padding:6px 12px;border-radius:6px;font-size:13px;">
               Read More →
            </a>
        </div>
        """

    return f"""
    <html>
    <body style="margin:0;padding:24px;background:#f4f5f7;font-family:Inter,Arial,sans-serif;">
      <table align="center" width="100%" style="max-width:650px;margin:auto;background:white;border-radius:12px;box-shadow:0 3px 10px rgba(0,0,0,0.1);overflow:hidden;">
        <tr><td style="background:#0f172a;color:white;padding:18px 24px;font-size:20px;font-weight:600;">🧠 Latest AI Research Feed</td></tr>
        <tr><td style="padding:24px;">{feed_html}</td></tr>
        <tr><td style="padding:16px;text-align:center;color:#9ca3af;font-size:12px;">Sent by your AI Research Agent 🤖</td></tr>
      </table>
    </body>
    </html>
    """



def render_discord(feed_items, source):
    embeds = []
    for item in feed_items[:5]:  # Discord allows max 10 embeds per message
        embeds.append({
            "title": f"🧠 {item['title']}",
            "description": item["summary"],
            "url": item["link"],
            "color": 657931,
            # "fields": [
            #     {
            #         "name": "Tags",
            #         "value": ", ".join(item["tags"]),
            #         "inline": False
            #     }
            # ],
            "footer": {
                "text": f"{source} • {item['published']}"
            }
        })
    if len(embeds) > 0:
        return {
            "content": "📡 **Latest AI Research Papers:**",
            "embeds" : embeds
        }
    else:
        return {
            "content": "No new research papers today!",
        }



if __name__ == "__main__":
    feed_items = [
    {
        "title": "Vision Transformers Revisited: A 2025 Perspective",
        "summary": "Adaptive patching improves zero-shot generalization in large-scale ViTs.",
        "url": "https://arxiv.org/abs/2510.12345",
        "tags": ["Vision Transformers", "Zero-Shot", "Deep Learning"],
        "source": "arXiv",
        "date": "2025-11-02"
    },
    {
        "title": "LLMs with Visual Context: From Text to Multimodal Reasoning",
        "summary": "Survey on large multimodal models integrating text and vision for reasoning.",
        "url": "https://arxiv.org/abs/2510.56789",
        "tags": ["LLM", "Multimodal", "Reasoning"],
        "source": "arXiv",
        "date": "2025-11-02"
    }
    ]

