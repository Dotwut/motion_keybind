import sys
import os
import logging
import tensorflow as tf
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

# Suppress TensorFlow warnings and logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 0=all, 1=INFO, 2=WARNING, 3=ERROR
logging.getLogger('tensorflow').setLevel(logging.ERROR)
tf.get_logger().setLevel(logging.ERROR)

# Suppress MediaPipe logging
logging.getLogger('mediapipe').setLevel(logging.ERROR)

def main():
    # Create poses directory if it doesn't exist
    if not os.path.exists("poses"):
        os.makedirs("poses")
        
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Motion Keybind")
    app.setStyle("Fusion")  # Use Fusion style for consistent look across platforms
    
    # Set dark theme
    app.setStyleSheet("""
        QMainWindow, QWidget {
            background-color: #2D2D30;
            color: #FFFFFF;
        }
        QPushButton {
            background-color: #007ACC;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 2px;
        }
        QPushButton:hover {
            background-color: #1C97EA;
        }
        QPushButton:pressed {
            background-color: #0062A3;
        }
        QTabWidget::pane {
            border: 1px solid #3F3F46;
        }
        QTabBar::tab {
            background-color: #2D2D30;
            color: #FFFFFF;
            padding: 8px 12px;
            border: 1px solid #3F3F46;
            border-bottom: none;
        }
        QTabBar::tab:selected {
            background-color: #007ACC;
        }
        QLabel {
            color: #FFFFFF;
        }
    """)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
