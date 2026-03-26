# core/fetcher.py
import feedparser
import calendar
from core.models import Article
import re

RSS_WORLD_FEEDS = [
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://abcnews.com/abcnews/internationalheadlines",
    "https://www.cbsnews.com/latest/rss/world",
    "https://feeds.skynews.com/feeds/rss/world.xml"
]

RSS_TECH_FEEDS = [
    "https://feeds.feedburner.com/IeeeSpectrumFullText",
    "https://www.wired.com/feed/category/security/latest/rss",
    "https://www.theverge.com/rss/index.xml"
]

RSS_ITALIAN_FEEDS = [
    "https://www.ansa.it/sito/ansait_rss.xml",
    "https://www.repubblica.it/rss/homepage/rss2.0.xml",
    "https://www.lastampa.it/rss/copertina.xml",
    "https://www.milanotoday.it/rss",
    "https://www.rainews.it/rss/politica",
    "https://www.corriere.it/dynamic-feed/rss/section/Politica.xml"
]

RSS_MUSIC_FEEDS = [
    "https://pitchfork.com/feed/reviews/best/albums/rss",
    "https://pitchfork.com/feed/reviews/best/reissues/rss",
    "https://pitchfork.com/feed/reviews/best/tracks/rss"
]
SOURCE_NAMES = {
    "http://feeds.bbci.co.uk/news/world/rss.xml":                       "BBC News",
    "https://abcnews.com/abcnews/internationalheadlines":               "ABC News",
    "https://www.cbsnews.com/latest/rss/world":                         "CBS News",
    "https://feeds.skynews.com/feeds/rss/world.xml":                    "Sky News",
    "https://feeds.feedburner.com/IeeeSpectrumFullText":                "IEEE Spectrum",
    "https://www.wired.com/feed/category/security/latest/rss":          "Wired",
    "https://www.theverge.com/rss/index.xml":                           "The Verge",
    "https://www.ansa.it/sito/ansait_rss.xml":                          "ANSA",
    "https://www.repubblica.it/rss/homepage/rss2.0.xml":                "La Repubblica",
    "https://www.lastampa.it/rss/copertina.xml":                        "La Stampa",
    "https://www.milanotoday.it/rss":                                   "Milano Today",
    "https://www.rainews.it/rss/politica":                              "Rai News",
    "https://www.corriere.it/dynamic-feed/rss/section/Politica.xml":    "Il Corriere della Sera",
    "https://pitchfork.com/feed/reviews/best/albums/rss":               "Pitchfork Albums",
    "https://pitchfork.com/feed/reviews/best/reissues/rss":             "Pitchfork Reissues",
    "https://pitchfork.com/feed/reviews/best/tracks/rss":               "Pitchfork Tracks"

}

MAX_ARTICLES_PER_FEED = 8

def _get_image_url(entry):
    # media:thumbnail
    if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
        return entry.media_thumbnail[0].get("url")
    
    # media:content
    if hasattr(entry, "media_content") and entry.media_content:
        for m in entry.media_content:
            if m.get("medium") == "image" or m.get("url", "").endswith((".jpg", ".png", ".webp")):
                return m.get("url")
    
    # enclosures
    if hasattr(entry, "enclosures") and entry.enclosures:
        for enc in entry.enclosures:
            if enc.get("type", "").startswith("image/"):
                return enc.get("href")

    # <image> tag directly in <item>
    if hasattr(entry, "image") and entry.image:
        if isinstance(entry.image, str):
            return entry.image.strip()
        if isinstance(entry.image, dict):
            return entry.image.get("href") or entry.image.get("url")

    # first <img> from content HTML
    content = getattr(entry, "content", None)
    if content:
        html = content[0].get("value", "")
        match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html)
        if match:
            return match.group(1)

    # summary??
    summary = getattr(entry, "summary", "")
    if summary:
        match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', summary)
        if match:
            return match.group(1)

    return None


def _fetch_from_feeds(feed_urls):
    articles = []
    for feed_url in feed_urls:
        feed = feedparser.parse(feed_url)
        source_name = SOURCE_NAMES.get(feed_url, feed_url)  # fallback to url if not mapped

        for entry in feed.entries[:MAX_ARTICLES_PER_FEED]:
            title   = getattr(entry, "title",   None) or "Empty Title"
            summary = getattr(entry, "summary", None) or "Empty Summary"
            link    = getattr(entry, "link",    None) or "Empty URL"
            date = calendar.timegm(entry.published_parsed) if entry.get("published_parsed") else 0


            articles.append(Article(
                title=title,
                content=summary,
                url=link,
                source = source_name  or "Empty Source",
                date = date,
                image_url = _get_image_url(entry)
            ))
    return articles


def fetch_world_news():
    return _fetch_from_feeds(RSS_WORLD_FEEDS)

def fetch_tech_news():
    return _fetch_from_feeds(RSS_TECH_FEEDS)

def fetch_italian_news():
    return _fetch_from_feeds(RSS_ITALIAN_FEEDS)

def fetch_music_news():
    return _fetch_from_feeds(RSS_MUSIC_FEEDS)