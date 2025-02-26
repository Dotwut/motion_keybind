from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QListWidget)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSlot

from modules.camera import CameraThread
from modules.pose_detector import PoseDetector
from modules.keyboard_mapper import KeyboardMapper

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Motion Keybind")
        self.resize(1000, 600)
        
        # Initialize modules
        self.camera_thread = CameraThread()
        self.pose_detector = PoseDetector()
        self.keyboard_mapper = KeyboardMapper()
        
        # Set up UI
        self.setup_ui()
        
        # Connect signals
        self.camera_thread.raw_frame_ready.connect(self.pose_detector.process_frame)
        self.pose_detector.processed_frame.connect(self.update_frame)
        self.pose_detector.pose_detected.connect(self.on_pose_detected)
        
        # Start camera
        self.camera_thread.start()
        
    def setup_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        
        # Camera view
        self.camera_view = QLabel()
        self.camera_view.setMinimumSize(640, 480)
        self.camera_view.setAlignment(Qt.AlignCenter)
        self.camera_view.setStyleSheet("background-color: black;")
        
        # Control panel
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        
        # Pose list
        self.pose_list = QListWidget()
        control_layout.addWidget(QLabel("Saved Poses:"))
        control_layout.addWidget(self.pose_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.capture_btn = QPushButton("Capture Pose")
        self.capture_btn.clicked.connect(self.capture_pose)
        button_layout.addWidget(self.capture_btn)
        
        self.delete_btn = QPushButton("Delete Pose")
        button_layout.addWidget(self.delete_btn)
        
        control_layout.addLayout(button_layout)
        
        # Add widgets to main layout
        main_layout.addWidget(self.camera_view, 2)
        main_layout.addWidget(control_panel, 1)
        
        self.setCentralWidget(main_widget)
        
    @pyqtSlot(object)
    def update_frame(self, frame):
        """Update the camera view with the processed frame"""
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.camera_view.setPixmap(QPixmap.fromImage(qt_image).scaled(
            self.camera_view.size(), Qt.KeepAspectRatio))
    
    @pyqtSlot(dict)
    def on_pose_detected(self, landmarks):
        """Process detected pose landmarks"""
        # Here we would implement pose comparison and key triggering
        pass
    
    def capture_pose(self):
        """Capture the current pose for mapping"""
        # This would open a dialog to map the pose to keys
        pass
        
    def closeEvent(self, event):
        """Clean up resources when closing"""
        self.camera_thread.stop()
        super().closeEvent(event)
