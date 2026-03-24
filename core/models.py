from dataclasses import dataclass
from typing import List

@dataclass
class Article:
    title: str
    url: str
    source: str
    content: str

@dataclass
class NewsCluster:
    title: str
    articles: List[Article]