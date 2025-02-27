from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QMessageBox, QSlider, 
                            QCheckBox, QSpinBox, QDoubleSpinBox)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class PoseEditDialog(QDialog):
    def __init__(self, pose_id, pose_name, key_combo, image_path, 
                threshold=0.60, 
                recognition_speed=500, 
                immediate_release=True, 
                sustained_duration=0, 
                parent=None):
        # Ensure all parameters are of the correct type
        self.pose_id = str(pose_id)
        self.pose_name = str(pose_name)
        self.key_combo = str(key_combo)
        self.image_path = image_path
        self.threshold = float(threshold)
        self.recognition_speed = int(recognition_speed)  # Explicitly convert to int
        self.immediate_release = bool(immediate_release)
        self.sustained_duration = float(sustained_duration)
        
        # Call the parent constructor with the parent widget
        super().__init__(parent)
        
        self.setWindowTitle("Edit Pose")
        self.resize(500, 500)
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
        
        # Matching Threshold
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Matching Threshold:"))
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setMinimum(10)
        self.threshold_slider.setMaximum(90)
        self.threshold_slider.setValue(int(self.threshold * 100))
        
        self.threshold_value = QLabel(f"{int(self.threshold * 100)}%")
        self.threshold_slider.valueChanged.connect(
            lambda v: self.threshold_value.setText(f"{v}%")
        )
        
        threshold_layout.addWidget(self.threshold_slider)
        threshold_layout.addWidget(self.threshold_value)
        layout.addLayout(threshold_layout)
        
        # Recognition Speed
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Recognition Speed (ms):"))
        self.speed_input = QSpinBox()
        self.speed_input.setRange(100, 2000)
        self.speed_input.setSingleStep(50)
        self.speed_input.setValue(self.recognition_speed)
        speed_layout.addWidget(self.speed_input)
        layout.addLayout(speed_layout)
        
        # Immediate Release Option
        release_layout = QHBoxLayout()
        self.immediate_release_check = QCheckBox("Immediate Key Release")
        self.immediate_release_check.setChecked(self.immediate_release)
        release_layout.addWidget(self.immediate_release_check)
        layout.addLayout(release_layout)
        
        # Sustained Duration
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Sustained Key Duration (seconds):"))
        self.duration_input = QDoubleSpinBox()
        self.duration_input.setRange(0, 10)
        self.duration_input.setSingleStep(0.1)
        self.duration_input.setValue(self.sustained_duration)
        self.duration_input.setEnabled(not self.immediate_release_check.isChecked())
        duration_layout.addWidget(self.duration_input)
        layout.addLayout(duration_layout)
        
        # Enable/Disable duration input based on immediate release
        self.immediate_release_check.toggled.connect(
            lambda checked: self.duration_input.setEnabled(not checked)
        )
        
        # Explanatory text
        explanation = QLabel(
            "Matching Threshold: Lower values require more precise matching.\n"
            "Recognition Speed: Time between pose checks (ms).\n"
            "Immediate Release: If unchecked, key will be held for specified duration."
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)
        
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
            "threshold": self.threshold_slider.value() / 100.0,
            "recognition_speed": self.speed_input.value(),
            "immediate_release": self.immediate_release_check.isChecked(),
            "sustained_duration": self.duration_input.value()
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