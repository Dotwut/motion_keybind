from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
import os


class PoseWidget(QWidget):
    selected = pyqtSignal(str)  # Signal emitted when widget is clicked
    
    def __init__(self, pose_id, pose_name, key_combo, image_path=None):
        super().__init__()
        self.pose_id = pose_id
        self.pose_name = pose_name
        self.key_combo = key_combo
        self.image_path = image_path
        self.is_selected = False
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Image
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(120, 120)
        self.image_label.setMaximumSize(200, 200)
        self.image_label.setStyleSheet("background-color: #222222;")
        
        if self.image_path and os.path.exists(self.image_path):
            pixmap = QPixmap(self.image_path)
            self.image_label.setPixmap(pixmap.scaled(
                self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.image_label.setText("No Image")
            
        # Key combo label - centered below image as shown in your screenshot
        self.key_label = QLabel(self.key_combo)
        self.key_label.setAlignment(Qt.AlignCenter)
        self.key_label.setStyleSheet("color: white; font-size: 10pt;")
        
        # Add widgets to layout
        layout.addWidget(self.image_label)
        layout.addWidget(self.key_label)
        
        # Set widget properties to match the dark theme in your image
        self.setStyleSheet("""
            QWidget {
                background-color: #333333;
                border-radius: 5px;
                color: white;
            }
        """)
        
    # Update PoseWidget class
    def mousePressEvent(self, event):
        """Handle mouse click on this widget"""
        # Find all other pose widgets and deselect them
        parent = self.parent()
        if parent:
            for i in range(parent.layout().count()):
                widget = parent.layout().itemAt(i).widget()
                if isinstance(widget, PoseWidget) and widget is not self:
                    widget.is_selected = False
                    widget.remove_highlight()
        
        self.is_selected = True
        self.setStyleSheet("""
            QWidget {
                background-color: #555555;
                border-radius: 5px;
                color: white;
                border: 2px solid #007ACC;
            }
        """)
        self.selected.emit(self.pose_id)
        super().mousePressEvent(event)
        
    def highlight(self):
        """Highlight this widget when its pose is detected"""
        self.setStyleSheet("""
            QWidget {
                background-color: #4CAF50;
                border-radius: 5px;
                color: white;
            }
        """)
        
    def remove_highlight(self):
        """Remove highlight"""
        if self.is_selected:
            self.setStyleSheet("""
                QWidget {
                    background-color: #555555;
                    border-radius: 5px;
                    color: white;
                    border: 2px solid #007ACC;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #333333;
                    border-radius: 5px;
                    color: white;
                }
            """)
