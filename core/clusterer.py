# core/clusterer.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering
import numpy as np

def cluster_articles(articles):
    texts = [a.title for a in articles]
    
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(texts)
    
    clustering = AgglomerativeClustering(n_clusters=None,distance_threshold=1.3) # default threshold = 1.2
    labels = clustering.fit_predict(np.asarray(X.todense())) #conversion with numpy needed because X is large sparse
    
    clusters = {}
    for label, article in zip(labels, articles):
        clusters.setdefault(label, []).append(article)
    
    return list(clusters.values())