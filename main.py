# main.py
from PyQt6.QtWidgets import QApplication
from ui.mainpage import MainWindow

app = QApplication([])
window = MainWindow()
window.show()
app.exec()