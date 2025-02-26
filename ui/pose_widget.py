from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
import os


class PoseWidget(QWidget):
    selected = pyqtSignal(str)  # Signal emitted when widget is clicked
    double_clicked = pyqtSignal(str)  # Signal specifically for double clicks
    
    def __init__(self, pose_id, pose_name, key_combo, image_path=None):
        super().__init__()
        self.pose_id = pose_id
        self.pose_name = pose_name
        self.key_combo = key_combo
        self.image_path = image_path
        self.is_selected = False
        
        # Variables for handling double click detection
        self.click_timer = QTimer(self)
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self.handle_single_click)
        self.pending_click = False
        
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
            
        # Name label
        self.name_label = QLabel(self.pose_name)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("color: white; font-weight: bold;")
            
        # Key combo label
        self.key_label = QLabel(self.key_combo)
        self.key_label.setAlignment(Qt.AlignCenter)
        self.key_label.setStyleSheet("color: white; font-size: 10pt;")
        
        # Add widgets to layout
        layout.addWidget(self.image_label)
        layout.addWidget(self.name_label)
        layout.addWidget(self.key_label)
        
        # Set widget properties to match the dark theme
        self.update_styling()
        
        # Make the widget clickable
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)
    
    def update_styling(self):
        """Update the styling based on selection state"""
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
        
    def mousePressEvent(self, event):
        """Handle mouse press on this widget"""
        if event.button() == Qt.LeftButton:
            if self.pending_click:  # This is a double click
                self.pending_click = False
                self.click_timer.stop()
                self.handle_double_click()
            else:  # This might be a single click or the first click of a double click
                self.pending_click = True
                self.click_timer.start(200)  # 200ms timeout to detect double click
                
        super().mousePressEvent(event)
    
    def handle_single_click(self):
        """Process a confirmed single click"""
        self.pending_click = False
        
        # Find all other pose widgets and deselect them
        parent = self.parent()
        if parent:
            for i in range(parent.layout().count()):
                widget = parent.layout().itemAt(i).widget()
                if isinstance(widget, PoseWidget) and widget is not self:
                    widget.is_selected = False
                    widget.update_styling()
        
        # Select this widget
        self.is_selected = True
        self.update_styling()
        
        # Emit selection signal
        self.selected.emit(self.pose_id)
        print(f"PoseWidget: Single click on {self.pose_name} (ID: {self.pose_id})")
    
    def handle_double_click(self):
        """Process a confirmed double click"""
        # Make sure this widget is selected
        self.is_selected = True
        self.update_styling()
        
        # Emit double click signal
        self.double_clicked.emit(self.pose_id)
        print(f"PoseWidget: Double click on {self.pose_name} (ID: {self.pose_id})")
        
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
        """Remove highlight and restore normal styling"""
        self.update_styling()