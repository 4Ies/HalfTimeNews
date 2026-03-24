# core/pipeline.py
from core.fetcher import fetch_news
from core.clusterer import cluster_articles

def get_news_clusters():
    articles = fetch_news()
    clusters = cluster_articles(articles)
    return clusters