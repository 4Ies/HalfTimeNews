from dataclasses import dataclass
from typing import List
from feedparser import FeedParserDict

@dataclass
class Article:
    title: str
    url: str
    source: str
    content: str
    date: int | List[FeedParserDict]
    image_url: str | None

@dataclass
class NewsCluster:
    title: str
    articles: List[Article]