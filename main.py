import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                           QVBoxLayout, QLabel, QProgressBar, QPushButton)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor

class DevelopmentApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gradtagszahlen")
        self.setFixedSize(600, 400)
        
        # Zentrales Widget und Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Titel
        title = QLabel("Gradtagszahlen")
        title.setFont(QFont('Arial', 32, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setFixedSize(300, 15)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 7px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.progress, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Status Text
        self.status = QLabel("System in Entwicklung")
        self.status.setFont(QFont('Arial', 16))
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status)
        
        # Animierter Text
        self.dev_status = QLabel("⚡ Entwicklung läuft")
        self.dev_status.setFont(QFont('Arial', 14))
        self.dev_status.setStyleSheet("color: gray;")
        self.dev_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.dev_status)
        
        # OK Button
        self.button = QPushButton("OK")
        self.button.setFixedSize(200, 40)
        self.button.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        self.button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 20px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #357a38;
            }
        """)
        self.button.clicked.connect(self.close)
        layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Animation Timer für Progress Bar
        self.progress_value = 0
        self.progress_direction = 1
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress)
        self.progress_timer.start(50)
        
        # Animation Timer für Text
        self.dots_count = 0
        self.text_timer = QTimer()
        self.text_timer.timeout.connect(self.update_text)
        self.text_timer.start(500)
        
        # Fenster zentrieren
        self.center_window()
        
    def center_window(self):
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
        
    def update_progress(self):
        self.progress_value += self.progress_direction
        if self.progress_value >= 100:
            self.progress_direction = -1
        elif self.progress_value <= 0:
            self.progress_direction = 1
        self.progress.setValue(self.progress_value)
        
    def update_text(self):
        dots = "." * ((self.dots_count % 4))
        self.dev_status.setText(f"⚡ Entwicklung läuft{dots}")
        self.dots_count += 1

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Style der Anwendung
    app.setStyle('Fusion')
    
    window = DevelopmentApp()
    window.show()
    sys.exit(app.exec())