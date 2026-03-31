from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPainter, QColor
import urllib.request
from bs4 import BeautifulSoup


class ArticleFetcher(QThread):
    """Fetches full article text in background."""
    article_fetched = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            req = urllib.request.Request(self.url, headers={"User-Agent": "Mozilla/5.0"})
            html = urllib.request.urlopen(req, timeout=8).read()
            soup = BeautifulSoup(html, "html.parser")

            for tag in soup(["script", "style", "nav", "header", "footer", "aside", "figure"]):
                tag.decompose()

            article = soup.find("article")
            if article:
                text = article.get_text(separator="\n\n", strip=True)
            else:
                paragraphs = soup.find_all("p")
                text = "\n\n".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 40)

            self.article_fetched.emit(text if text else "Could not extract article text.")
        except Exception as e:
            self.article_fetched.emit(f"Failed to load article: {e}")


class ArticleViewer(QWidget):
    def __init__(self, title, url, parent=None):
        super().__init__(parent)
        self._card = None 
        self.url = url
        self._fetcher = None

        # Guard against None parent
        if parent is None:
            self.setFixedSize(800, 600)
            self.move(100, 100)
        else:
            self.setGeometry(parent.rect())

        self.setStyleSheet("")

        # Card size based on available space
        available_w = parent.width() if parent else 800
        available_h = parent.height() if parent else 600

        card = QWidget(self)
        card.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-radius: 16px;
            }
        """)
        card.setFixedSize(int(available_w * 0.65), int(available_h * 0.85))
        card.move(
            (available_w - card.width()) // 2,
            (available_h - card.height()) // 2
        )

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 24, 32, 24)
        card_layout.setSpacing(12)

        # --- Header row: title + close button ---
        header = QHBoxLayout()

        title_label = QLabel(title)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("font-size: 30px; font-family: 'New Century Schoolbook'; font-weight: bold; color: #ffffff; background: transparent; border: none;")

        title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(36, 36)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border-radius: 18px;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #e53935;
            }
        """)
        close_btn.clicked.connect(self._close_viewer)

        header.addWidget(title_label)
        header.addWidget(close_btn)
        card_layout.addLayout(header)

        # --- Divider ---
        divider = QWidget()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: #444; border: none;")
        card_layout.addWidget(divider)

        # --- Scrollable article body ---
        self._body_label = QLabel("Loading article...")
        self._body_label.setWordWrap(True)
        self._body_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._body_label.setStyleSheet("font-size: 20px; font-family: 'New Century Schoolbook'; color: #dddddd; background: transparent; border: none; line-height: 1.6;")

        scroll = QScrollArea()
        scroll.setWidget(self._body_label)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar { width: 0px; height: 0px; }
        """)
        card_layout.addWidget(scroll)

        # --- Source link ---
        source_label = QLabel(f'<a href="{url}" style="color:#A3DAFF;">Open original article ↗</a>')
        source_label.setOpenExternalLinks(True)
        source_label.setStyleSheet("font-size: 13px; background: transparent; border: none;")
        card_layout.addWidget(source_label)

        # --- Fetch article in background ---
        self._fetcher = ArticleFetcher(url)
        self._fetcher.article_fetched.connect(self._on_article_fetched)
        self._fetcher.start()

        self.show()

    def _on_article_fetched(self, text):
        self._body_label.setText(text)

    def _close_viewer(self):
        if self._fetcher and self._fetcher.isRunning():
            self._fetcher.quit()
            self._fetcher.wait()  # 👈 wait for thread to finish cleanly
        self.deleteLater()

    def mousePressEvent(self, event):
        if self._card is None or not self._card.geometry().contains(event.pos()):
            self._close_viewer()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 180))
        painter.end()