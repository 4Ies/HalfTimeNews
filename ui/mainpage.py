# ui/mainpage.py
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QScrollArea
from PyQt6.QtCore import Qt
from core.pipeline import *
from ui.newscard import NewsCard, CARD_COLORS


def make_label(text, font_size, bold=False, fixed_height=None):
    """Helper to build a configured QLabel."""
    label = QLabel(text)
    label.setStyleSheet(
        f"font-family: 'New Century Schoolbook';"
        f"font-size: {font_size}px;"
        f"{'font-weight: bold;' if bold else ''}"
    )
    if fixed_height:
        label.setFixedHeight(fixed_height)
    return label


def make_news_section(clusters, color):
    """Builds a scrollable HBox section from a list of clusters."""
    layout = QHBoxLayout()
    layout.setSpacing(10)
    layout.setContentsMargins(4, 4, 4, 4)

    for cluster in clusters:
        card = NewsCard(cluster, color=color)
        layout.addWidget(card)

    scroll_widget = QWidget()
    scroll_widget.setLayout(layout)

    scroll_area = QScrollArea()
    scroll_area.setWidget(scroll_widget)
    scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll_area.setWidgetResizable(True)
    scroll_area.setFixedHeight(280)

    return scroll_area


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Half Time News")

        mainLayout = QVBoxLayout()

        mainLayout.addWidget(make_label("◈ Half Time News", font_size=80, bold=True, fixed_height=90))

        mainLayout.addWidget(make_label("Italian News", font_size=40, bold=True, fixed_height=60))
        mainLayout.addWidget(make_news_section(get_italian_news_clusters(), color=CARD_COLORS[2]))

        mainLayout.addWidget(make_label("World News", font_size=40, bold=True, fixed_height=60))
        mainLayout.addWidget(make_news_section(get_world_news_clusters(), color=CARD_COLORS[0]))

        mainLayout.addWidget(make_label("Tech News", font_size=40, bold=True, fixed_height=60))
        mainLayout.addWidget(make_news_section(get_tech_news_clusters(), color=CARD_COLORS[1]))

        mainLayout.addWidget(make_label("Latest Music", font_size=40, bold=True, fixed_height=60))
        mainLayout.addWidget(make_news_section(get_music_news_clusters(), color=CARD_COLORS[3]))

        scroll_widget = QWidget()
        scroll_widget.setLayout(mainLayout)

        scroll_area = QScrollArea()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidgetResizable(True)
        
        self.setCentralWidget(scroll_area)