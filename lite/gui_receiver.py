"""Temporary real-window click receiver behind the pet. Not distributed."""
import json
import sys
import time
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QApplication, QWidget


class Receiver(QWidget):
    def __init__(self, path):
        super().__init__(None, Qt.WindowType.Tool)
        self.path = Path(path)
        self.setWindowTitle('DSH Pet Lite input test backdrop')
        self.setGeometry(400, 300, 700, 650)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor('#ffffff'))
        painter.fillRect(350, 0, 350, 650, QColor('#202020'))
        painter.setPen(QColor('#555555'))
        painter.drawText(15, 30, 'Temporary Lite input / alpha test. Closes automatically.')

    def mousePressEvent(self, event):
        with self.path.open('a', encoding='utf-8') as out:
            out.write(json.dumps({'time': time.time(), 'x': event.globalPosition().x(),
                                  'y': event.globalPosition().y()})+'\n')

    def closeEvent(self, event):
        event.accept()
        QApplication.instance().quit()


if __name__ == '__main__':
    app = QApplication([])
    window = Receiver(sys.argv[1])
    window.show()
    QTimer.singleShot(180000, app.quit)
    raise SystemExit(app.exec())
