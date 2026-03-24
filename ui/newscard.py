# ui/newscard.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class NewsCard(QWidget):
    def __init__(self, cluster):
        super().__init__()
        
        layout = QVBoxLayout()
        
        title = QLabel(cluster[0].title)
        content = QLabel(cluster[0].content)
        layout.addWidget(title)
        layout.addWidget(content)
        
        for article in cluster:
            source = QLabel(article.source)
            layout.addWidget(source)
        
        self.setLayout(layout)