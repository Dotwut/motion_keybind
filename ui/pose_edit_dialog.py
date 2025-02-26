from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QMessageBox, QSlider)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class PoseEditDialog(QDialog):
    def __init__(self, pose_id, pose_name, key_combo, image_path, threshold=0.60, parent=None):
        super().__init__(parent)
        self.pose_id = pose_id
        self.pose_name = pose_name
        self.key_combo = key_combo
        self.image_path = image_path
        self.threshold = threshold
        
        self.setWindowTitle("Edit Pose")
        self.resize(400, 350)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Image preview
        self.image_preview = QLabel()
        self.image_preview.setMinimumSize(200, 150)
        self.image_preview.setAlignment(Qt.AlignCenter)
        
        if self.image_path:
            pixmap = QPixmap(self.image_path)
            self.image_preview.setPixmap(pixmap.scaled(
                self.image_preview.size(), Qt.KeepAspectRatio))
                
        layout.addWidget(self.image_preview)
        
        # Pose name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Pose Name:"))
        self.name_input = QLineEdit(self.pose_name)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Key combination input
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("Key Combination:"))
        self.key_input = QLineEdit(self.key_combo)
        key_layout.addWidget(self.key_input)
        layout.addLayout(key_layout)
        
        # Threshold slider - using the whole range for flexibility
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Matching Threshold:"))
        self.threshold_slider = QSlider(Qt.Horizontal)
        
        # Range from 10% to 90% with proper initial value
        self.threshold_slider.setMinimum(10)
        self.threshold_slider.setMaximum(90)
        
        # Convert threshold from 0.0-1.0 to percentage for the slider
        threshold_percent = int(self.threshold * 100)
        self.threshold_slider.setValue(threshold_percent)

        # Display current value
        self.threshold_value = QLabel(f"{threshold_percent}%")
        self.threshold_slider.valueChanged.connect(
            lambda v: self.threshold_value.setText(f"{v}%")
        )
        threshold_layout.addWidget(self.threshold_slider)
        threshold_layout.addWidget(self.threshold_value)
        layout.addLayout(threshold_layout)
        
        # Add explanation
        threshold_explanation = QLabel(
            "Lower values require more precise matching. Higher values are more forgiving."
        )
        threshold_explanation.setWordWrap(True)
        layout.addWidget(threshold_explanation)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
    def get_values(self):
        return {
            "pose_id": self.pose_id,
            "name": self.name_input.text(),
            "key_combo": self.key_input.text(),
            "threshold": self.threshold_slider.value() / 100.0
        }
    
    def accept(self):
        key_combo = self.key_input.text()
        
        # Validate the keybind
        from modules.keyboard_mapper import validate_keybind
        is_valid, message = validate_keybind(key_combo)
        
        if not is_valid:
            QMessageBox.warning(self, "Invalid Keybind", message)
            return
            
        super().accept()