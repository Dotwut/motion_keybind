from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QDialog, QSlider, QMessageBox)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal

class PoseReviewPanel(QWidget):
    save_pose = pyqtSignal(str, str, float)  # name, key_combo, threshold
    cancel_capture = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.captured_image = None
        self.current_signature = None  # Store the pose signature
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Preview image
        self.image_preview = QLabel()
        self.image_preview.setMinimumSize(320, 240)
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setStyleSheet("background-color: #222222; border: 1px solid #444444;")
        layout.addWidget(self.image_preview)
        
        # Pose name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Pose Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter pose name")
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Key combination input
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("Key Combination:"))
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("e.g. shift+a, f1, ctrl+alt+d")
        key_layout.addWidget(self.key_input)
        layout.addLayout(key_layout)
        
        # Matching threshold slider
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Matching Threshold:"))
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setMinimum(10)
        self.threshold_slider.setMaximum(90)
        self.threshold_slider.setValue(60)  # Default 60%
        self.threshold_value = QLabel("60%")
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
        threshold_explanation.setStyleSheet("color: #AAAAAA; font-style: italic;")
        layout.addWidget(threshold_explanation)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.on_save)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.on_cancel)
        
        self.retake_btn = QPushButton("Retake")
        self.retake_btn.clicked.connect(self.on_retake)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.retake_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        # Voice command indicator
        self.voice_indicator = QLabel("Say \"Save Data\" to save this pose")
        self.voice_indicator.setAlignment(Qt.AlignCenter)
        self.voice_indicator.setStyleSheet("color: #888888;")
        layout.addWidget(self.voice_indicator)
        
        # Initially hide this panel
        self.setVisible(False)
        
    def set_captured_image(self, pixmap):
        # Create a deep copy of the pixmap to prevent it from being garbage collected
        self.captured_image = QPixmap(pixmap)
        self.image_preview.setPixmap(self.captured_image.scaled(
            self.image_preview.size(), Qt.KeepAspectRatio))
        self.setVisible(True)
        
    def on_save(self):
        name = self.name_input.text()
        key_combo = self.key_input.text()
        threshold = self.threshold_slider.value() / 100.0
        
        if not name:
            name = "Unnamed Pose"
        if not key_combo:
            key_combo = "None"
            
        # Validate the keybind
        from modules.keyboard_mapper import validate_keybind
        is_valid, message = validate_keybind(key_combo)
        
        if not is_valid:
            QMessageBox.warning(self, "Invalid Keybind", message)
            return
            
        self.save_pose.emit(name, key_combo, threshold)
        self.clear()
        
    def on_cancel(self):
        self.clear()
        self.cancel_capture.emit()
        
    def on_retake(self):
        self.clear()
        # The main window will handle capturing a new pose
        
    def clear(self):
        self.name_input.clear()
        self.key_input.clear()
        self.image_preview.clear()
        self.current_signature = None  # Clear the stored signature
        self.setVisible(False)
        
    def handle_voice_command(self, command):
        if command == "SAVE_DATA" and self.isVisible():
            self.on_save()