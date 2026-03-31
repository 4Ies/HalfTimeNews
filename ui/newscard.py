from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import QVariantAnimation, QEasingCurve, QRectF, QThread, pyqtSignal, Qt
from PyQt6.QtGui import QPainter, QColor, QPainterPath, QPen, QPixmap, QImage
from datetime import datetime
from ui.articleViewer import ArticleViewer
import urllib.request

CARD_COLORS = ["#A3DAFF", "#FFBA94", "#E5FFE9", "#FFF8E5", "#F3E5FF"]
DARK_OVERLAY = 140  # 0 = fully transparent, 255 = fully black — tweak to taste

# utility to make uniform labels
def make_label(text, font_size, color="#000", bold=False, word_wrap=False, open_links=False):
    label = QLabel(text)
    label.setWordWrap(word_wrap)
    label.setOpenExternalLinks(open_links)
    label.setStyleSheet(
        f"font-size: {font_size}px; color: {color}; background: transparent; border: none;"
        f"{'font-weight: bold;' if bold else ''}"
    )
    return label

# utility to catch recent news (3 hours)
def _is_recent(date_timestamp, hours=3):
    """Returns True if the article is less than `hours` old."""
    now = datetime.now().timestamp()
    return (now - date_timestamp) < (hours * 3600)

# thread to load images
class ImageLoader(QThread):
    """Downloads image in background thread to avoid freezing the UI."""
    image_loaded = pyqtSignal(QPixmap)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            req = urllib.request.Request(self.url, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=5).read()
            image = QImage()
            image.loadFromData(data)
            self.image_loaded.emit(QPixmap.fromImage(image))
        except Exception:
            self.image_loaded.emit(QPixmap())  # emit empty pixmap on failure

# to make labels clickable
class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()



# actual newscard object
class NewsCard(QWidget):

    COLLAPSED_HEIGHT = 180
    EXPANDED_HEIGHT  = 250

    def __init__(self, cluster, color="#E5F0FF"):
        super().__init__()
        self.color = color
        self._current_bg     = color
        self._current_border = "#b0b0b0"
        self._bg_pixmap      = None   # will hold the downloaded image
        self._hover          = False
        self._is_fresh = _is_recent(cluster[0].date)

        self.setFixedWidth(300)
        self.setFixedHeight(self.COLLAPSED_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # --- Main layout ---
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)

        # White text if image, dark text if fallback color
        text_color = "#ffffff" if cluster[0].image_url else "#444444"

        title = make_label(
            cluster[0].title,
            font_size=17, bold=True, word_wrap=True, color=text_color
        )
        title.setMaximumHeight(60)
        layout.addWidget(title)

        content = ClickableLabel(cluster[0].content[:100] + "...")
        content.setWordWrap(True)
        content.setMaximumHeight(60)
        content.setStyleSheet(
            f"font-size: 15px; color: {text_color}; background: transparent; border: none;"
            f"text-decoration: underline;"
        )
        content.setCursor(Qt.CursorShape.PointingHandCursor)
        content.clicked.connect(lambda: self._open_article(cluster[0].title, cluster[0].url))
        layout.addWidget(content)

        # --- Detail panel ---
        self.detail_panel = QWidget(self)
        self.detail_panel.setFixedWidth(276)
        self.detail_panel.setFixedHeight(0)
        self.detail_panel.setStyleSheet("background: transparent; border: none;")

        detail_layout = QVBoxLayout(self.detail_panel)
        detail_layout.setContentsMargins(0, 8, 0, 0)
        detail_layout.setSpacing(3)

        for article in cluster:
            date_str = datetime.fromtimestamp(article.date).strftime("%d %b %Y")
            label = make_label(
                    f'<a href="{article.url}" style="color:{text_color};">{article.source}  —  {date_str}</a>',
                    font_size=14, color=text_color, open_links=True
                )
            detail_layout.addWidget(label)

        layout.addWidget(self.detail_panel)

        # --- Animations ---
        self._card_anim = QVariantAnimation()
        self._card_anim.setDuration(300)
        self._card_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._card_anim.valueChanged.connect(lambda h: self.setFixedHeight(h))

        self._panel_anim = QVariantAnimation()
        self._panel_anim.setDuration(300)
        self._panel_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._panel_anim.valueChanged.connect(lambda h: self.detail_panel.setFixedHeight(h))

        self._apply_style(hover=False)

        # --- Load image in background if available ---
        if cluster[0].image_url:
            self._loader = ImageLoader(cluster[0].image_url)
            self._loader.image_loaded.connect(self._on_image_loaded)
            self._loader.start()

    def _open_article(self, title, url):
        from PyQt6.QtWidgets import QMainWindow
        top = self.window()
        if isinstance(top, QMainWindow):
            parent = top.centralWidget()
        else:
            parent = top
        viewer = ArticleViewer(title, url, parent=parent)
        viewer.raise_()

    def _on_image_loaded(self, pixmap):
        if not pixmap.isNull():
            self._bg_pixmap = pixmap
            self.update()  # repaint with image


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 16, 16)

        painter.setClipPath(path)  # clip image to rounded corners

        if self._bg_pixmap and not self._bg_pixmap.isNull():
            # Draw image scaled to card size
            scaled = self._bg_pixmap.scaled(
                300, self.EXPANDED_HEIGHT,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            dest = QRectF(0, 0, scaled.width(), scaled.height())
            painter.drawPixmap(dest, scaled, QRectF(scaled.rect()))

            # Draw dark overlay so text is readable
            overlay_color = QColor(0, 0, 0, DARK_OVERLAY)
            if self._hover:
                overlay_color = QColor(0, 0, 0, max(0, DARK_OVERLAY - 20))  # slightly lighter on hover
            painter.fillRect(self.rect(), overlay_color)
        else:
            # Fallback: plain color background
            painter.fillPath(path, QColor(self._current_bg))

        # Draw border
        painter.setClipping(False)
        pen = QPen(QColor(self._current_border))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawPath(path)

        painter.end()

    def enterEvent(self, event):
        self._hover = True
        self._animate(expand=True)
        self._apply_style(hover=True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        self._animate(expand=False)
        self._apply_style(hover=False)
        super().leaveEvent(event)

    def _animate(self, expand: bool):
        card_target  = self.EXPANDED_HEIGHT if expand else self.COLLAPSED_HEIGHT
        panel_target = (self.EXPANDED_HEIGHT - self.COLLAPSED_HEIGHT) if expand else 0

        self._card_anim.stop()
        self._card_anim.setStartValue(self.height())
        self._card_anim.setEndValue(card_target)
        self._card_anim.start()

        self._panel_anim.stop()
        self._panel_anim.setStartValue(self.detail_panel.height())
        self._panel_anim.setEndValue(panel_target)
        self._panel_anim.start()

    def _apply_style(self, hover: bool):
        self._current_bg = "#FFE87C" if hover else self.color
        if hover:
            self._current_border = "#F5C400"
        elif self._is_fresh:
            self._current_border = "#e53935"  # red for recent articles
        else:
            self._current_border = "#b0b0b0"  # default grey
    
        self.update()

        