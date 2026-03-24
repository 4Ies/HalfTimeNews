# core/clusterer.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering

def cluster_articles(articles):
    texts = [a.title + " " + a.content for a in articles]
    
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(texts)
    
    clustering = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=1.2
    ).fit(X.toarray())
    
    clusters = {}
    for label, article in zip(clustering.labels_, articles):
        clusters.setdefault(label, []).append(article)
    
    return list(clusters.values())