from core.fetcher import *
from core.clusterer import cluster_articles

def get_world_news_clusters():
    articles = fetch_world_news()
    articles.sort(key=lambda article: article.date, reverse=True)
    clusters = cluster_articles(articles)
    return clusters

def get_tech_news_clusters():
    articles = fetch_tech_news()
    articles.sort(key=lambda article: article.date, reverse=True)
    clusters = cluster_articles(articles)
    return clusters

def get_italian_news_clusters():
    articles = fetch_italian_news()
    articles.sort(key=lambda article: article.date, reverse=True)
    clusters = cluster_articles(articles)
    return clusters

def get_music_news_clusters():
    articles = fetch_music_news()
    articles.sort(key=lambda article: article.date, reverse=True)
    clusters = cluster_articles(articles)
    return clusters