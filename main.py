import sys
import os
import logging
import tensorflow as tf
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QTimer
from ui.main_window import MainWindow

# Suppress TensorFlow warnings and logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 0=all, 1=INFO, 2=WARNING, 3=ERROR
logging.getLogger('tensorflow').setLevel(logging.ERROR)
tf.get_logger().setLevel(logging.ERROR)

# Suppress MediaPipe logging
logging.getLogger('mediapipe').setLevel(logging.ERROR)

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint)
        self.setStyleSheet("background-color: #1A1A1A; color: white;")
        
        layout = QVBoxLayout()
        
        # App Name with custom styling
        app_name = QLabel("Dotwut's MoCapApp")
        app_name.setFont(QFont("Arial", 24, QFont.Bold))
        app_name.setAlignment(Qt.AlignCenter)
        app_name.setStyleSheet("color: #2ECC71; margin-bottom: 20px;")
        
        # Tagline
        tagline = QLabel("Gesture-Powered Computing")
        tagline.setFont(QFont("Arial", 14))
        tagline.setAlignment(Qt.AlignCenter)
        tagline.setStyleSheet("color: #FFFFFF;")
        
        # Copyright notice
        copyright_notice = QLabel("© 2024 Dotwut. All Rights Reserved.")
        copyright_notice.setFont(QFont("Arial", 10))
        copyright_notice.setAlignment(Qt.AlignCenter)
        copyright_notice.setStyleSheet("color: #888888;")
        
        layout.addWidget(app_name)
        layout.addWidget(tagline)
        layout.addWidget(copyright_notice)
        
        self.setLayout(layout)
        
        # Set window size and center
        self.setFixedSize(400, 300)
        self.center()
        
    def center(self):
        """Center the splash screen on the screen"""
        frame_gm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        frame_gm.moveCenter(center_point)
        self.move(frame_gm.topLeft())

def main():
    # Create poses directory if it doesn't exist
    if not os.path.exists("poses"):
        os.makedirs("poses")
        
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Dotwut's MoCapApp")
    app.setStyle("Fusion")  # Use Fusion style for consistent look across platforms
    
    # Show splash screen
    splash = SplashScreen()
    splash.show()
    
    # Modern green and dark grey color scheme
    app.setStyleSheet("""
        QMainWindow, QWidget {
            background-color: #121212;  /* Very dark grey, almost black */
            color: #FFFFFF;
        }
        QPushButton {
            background-color: #2ECC71;  /* Vibrant green */
            color: #121212;  /* Dark text on green background */
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            font-weight: bold;
            text-transform: uppercase;
        }
        QPushButton:hover {
            background-color: #27AE60;  /* Slightly darker green on hover */
        }
        QPushButton:pressed {
            background-color: #1E8449;  /* Even darker green when pressed */
        }
        QTabWidget::pane {
            border: 1px solid #2C3E50;  /* Dark blue-grey border */
        }
        QTabBar::tab {
            background-color: #1A1A1A;  /* Dark grey background */
            color: #FFFFFF;
            padding: 10px 15px;  /* Increased padding */
            border: 1px solid #2C3E50;
            border-bottom: none;
            font-weight: bold;
            min-width: 100px;  /* Ensure minimum width */
            text-align: center;
        }
        QTabBar::tab:selected {
            background-color: #2ECC71;  /* Green for selected tab */
            color: #121212;
        }
        QLabel {
            color: #FFFFFF;
        }
        QLineEdit, QTextEdit {
            background-color: #1E1E1E;  /* Slightly lighter than main background */
            color: #FFFFFF;
            border: 1px solid #2C3E50;
            border-radius: 4px;
            padding: 5px;
        }
        QSlider::groove:horizontal {
            background-color: #2C3E50;
            height: 4px;
        }
        QSlider::handle:horizontal {
            background-color: #2ECC71;
            width: 18px;
            margin: -7px 0;
            border-radius: 9px;
        }
    """)
    
    # Create and show main window
    window = MainWindow()
    
    # Close splash screen after 2 seconds
    QTimer.singleShot(2000, splash.close)
    window.show()
    
    # Run application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()