# core/fetcher.py
import feedparser
from core.models import Article

RSS_FEEDS = [
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "http://rss.cnn.com/rss/edition_world.rss",
]

def fetch_world():
    articles = []

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)

        for entry in feed.entries:
            articles.append(Article(
                title=getattr(entry,"title"),
                content=getattr(entry, "summary",""),
                url=getattr(entry, "link"),
                source=getattr(entry,"link")
            ))

    return articles