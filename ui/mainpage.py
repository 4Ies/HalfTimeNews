# ui/mainpage.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from core.pipeline import get_news_clusters
from ui.newscard import NewsCard

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        
        clusters = get_news_clusters()
        
        for cluster in clusters:
            card = NewsCard(cluster)
            layout.addWidget(card)
        
        self.setLayout(layout)