import feedparser

def fetch_meta_fair_papers(query='', max_results=20, timedeltaindays=7):
    RSS_FEED = "https://ai.facebook.com/blog/rss/"
    feed = feedparser.parse(RSS_FEED)
    papers = []

    for entry in feed.entries[:max_results]:
        if query.lower() in entry.title.lower():
            papers.append({
                'title': entry.title,
                'summary': entry.summary,
                'link': entry.link,
                'published': entry.published
            })
    return papers
