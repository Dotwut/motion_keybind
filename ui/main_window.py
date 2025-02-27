from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QGridLayout, QDialog,
                            QLineEdit, QMessageBox, QTabWidget, QSlider,
                            QStyle, QSystemTrayIcon)
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, pyqtSlot, QTimer, QPoint

import cv2
import numpy as np
import os

from modules.camera import CameraThread
from modules.pose_detector import PoseDetector
from modules.keyboard_mapper import KeyboardMapper
from modules.voice_recognition import VoiceListener
from ui.pose_widget import PoseWidget
from ui.pose_review_panel import PoseReviewPanel
from ui.pose_edit_dialog import PoseEditDialog
from ui.voice_tab import VoiceTab

class MainWindow(QMainWindow):
    def __init__(self):
        # Use custom window flags to remove default title bar
        super().__init__(None, Qt.FramelessWindowHint)
        
        # Add these flags to allow resizing and keeping the window on top if needed
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Tracking variables for window dragging
        self._dragging = False
        self._drag_start_position = None
        
        # Custom title bar
        self.setup_custom_titlebar()
        
        self.setWindowTitle("Dotwut's MoCapApp")
        self.resize(1000, 700)
        
        # Set background color to match the app's dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
        """)
        
        # Initialize modules
        self.camera_thread = CameraThread()
        self.pose_detector = PoseDetector()
        self.keyboard_mapper = KeyboardMapper()
        self.voice_listener = VoiceListener()
        
        # State variables
        self.tracking_enabled = False
        self.current_pose_signature = None
        self.capture_mode = False
        self.selected_pose_id = None
        
        # Set up UI
        self.setup_ui()
        
        # Connect signals
        self.camera_thread.raw_frame_ready.connect(self.pose_detector.process_frame)
        self.pose_detector.processed_frame.connect(self.update_frame)
        self.pose_detector.pose_detected.connect(self.on_pose_detected)
        self.voice_listener.command_detected.connect(self.handle_voice_command)
        self.voice_listener.listening_status.connect(self.update_voice_status)
        
        # Ensure landmarks are not drawn initially
        self.pose_detector.set_draw_landmarks(False)
        
        # Start camera and voice listener
        self.camera_thread.start()
        self.voice_listener.start()
        
        # Setup pose checking timer (checks every 500ms)
        self.pose_timer = QTimer(self)
        self.pose_timer.timeout.connect(self.check_current_pose)
        self.pose_timer.start(800)
        
    def setup_custom_titlebar(self):
        """Create a custom title bar that matches the app's theme"""
        # Custom title bar widget
        self.title_bar = QWidget(self)
        self.title_bar.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #2ECC71;
                font-weight: bold;
                padding: 5px 10px;
            }
        """)
        
        # Title bar layout
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        # App title
        self.title_label = QLabel("Dotwut's MoCapApp")
        title_layout.addWidget(self.title_label)
        
        # Minimize, Maximize, Close buttons
        self.minimize_btn = QPushButton("—")
        self.maximize_btn = QPushButton("☐")
        self.close_btn = QPushButton("✕")
        
        # Style buttons
        for btn in [self.minimize_btn, self.maximize_btn, self.close_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #2ECC71;
                    border: none;
                    font-weight: bold;
                    padding: 0 10px;
                }
                QPushButton:hover {
                    background-color: #2C3E50;
                }
            """)
        
        # Connect button actions
        self.minimize_btn.clicked.connect(self.showMinimized)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        self.close_btn.clicked.connect(self.close)
        
        # Add buttons to layout
        title_layout.addStretch()
        title_layout.addWidget(self.minimize_btn)
        title_layout.addWidget(self.maximize_btn)
        title_layout.addWidget(self.close_btn)
        
        # Enable mouse tracking and events for dragging
        self.title_bar.setMouseTracking(True)
        
    def toggle_maximize(self):
        """Toggle between maximized and normal window state"""
        if self.isMaximized():
            self.showNormal()
            self.maximize_btn.setText("☐")
        else:
            self.showMaximized()
            self.maximize_btn.setText("❐")
    
    def titlebar_mousePressEvent(self, event):
        """Handle mouse press on title bar to start dragging"""
        if event.button() == Qt.LeftButton:
            # Start dragging
            self._dragging = True
            # Store the global cursor position and current window position
            self._drag_start_position = event.globalPos() - self.pos()
            event.accept()

    def titlebar_mouseMoveEvent(self, event):
        """Handle mouse move to drag the window"""
        if self._dragging:
            # Move the window based on mouse movement
            self.move(event.globalPos() - self._drag_start_position)
            event.accept()

    def titlebar_mouseReleaseEvent(self, event):
        """Stop dragging when mouse is released"""
        if event.button() == Qt.LeftButton:
            self._dragging = False
            event.accept()

    def toggle_maximize(self):
        """Toggle between maximized and normal window state"""
        if self.isMaximized():
            self.showNormal()
            self.maximize_btn.setText("☐")
        else:
            self.showMaximized()
            self.maximize_btn.setText("❐")

        
    def setup_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Add custom title bar to the main layout
        main_layout.addWidget(self.title_bar)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Bind mouse events to the title bar
        self.title_bar.mousePressEvent = self.titlebar_mousePressEvent
        self.title_bar.mouseMoveEvent = self.titlebar_mouseMoveEvent
        self.title_bar.mouseReleaseEvent = self.titlebar_mouseReleaseEvent
        
        # Rest of the UI setup...
        self.setCentralWidget(main_widget)
        
        # Tab widget for Movement/Voice tabs
        self.tab_widget = QTabWidget()
        
        # Movement tab
        movement_tab = QWidget()
        movement_layout = QVBoxLayout(movement_tab)
        
        # Camera view at the top
        self.camera_view = QLabel()
        self.camera_view.setMinimumSize(640, 480)
        self.camera_view.setAlignment(Qt.AlignCenter)
        self.camera_view.setStyleSheet("background-color: black;")
        
        # Grid of poses
        self.pose_grid = QGridLayout()
        self.pose_grid.setSpacing(10)
        
        # Add camera and grid to movement tab
        movement_layout.addWidget(self.camera_view)
        movement_layout.addLayout(self.pose_grid)
        
        # Voice tab
        voice_tab = VoiceTab(self.voice_listener)
        self.tab_widget.addTab(voice_tab, "Voice")
        
        # Add tabs to tab widget
        self.tab_widget.addTab(movement_tab, "Movement")
        self.tab_widget.addTab(voice_tab, "Voice")
        
        # Control buttons at the bottom
        control_layout = QHBoxLayout()
        
        # Capture button
        self.capture_btn = QPushButton("Capture Pose")
        self.capture_btn.clicked.connect(self.capture_pose)
        control_layout.addWidget(self.capture_btn)
        
        # Save button
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_to_file)
        control_layout.addWidget(self.save_btn)
        
        # Delete button
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_selected_pose)
        control_layout.addWidget(self.delete_btn)
        
        # Toggle tracking button
        self.tracking_btn = QPushButton("Start Tracking")
        self.tracking_btn.clicked.connect(self.toggle_tracking)
        control_layout.addWidget(self.tracking_btn)
        
        # Add voice status indicator
        self.voice_status = QLabel("Voice: Ready")
        self.voice_status.setStyleSheet("color: #888888;")
        control_layout.addWidget(self.voice_status)
        
        # Add pose review panel
        self.pose_review = PoseReviewPanel()
        self.pose_review.save_pose.connect(self.save_reviewed_pose)
        self.pose_review.cancel_capture.connect(self.cancel_pose_review)
        
        # Add pose review panel to movement tab
        movement_layout.addWidget(self.pose_review)
        
        # Add tab widget and controls to main layout
        main_layout.addWidget(self.tab_widget)
        main_layout.addLayout(control_layout)
        
        self.setCentralWidget(main_widget)
        
        # Load existing poses
        self.load_saved_poses()
        self.match_label = QLabel("Match: --")
        self.match_label.setStyleSheet("color: white; background-color: #333333; padding: 5px;")
        movement_layout.addWidget(self.match_label)
        
        # Add debug mode toggle button
        self.add_debug_mode_toggle()
        self.setCentralWidget(main_widget)

    def add_debug_mode_toggle(self):
        """
        Add a debug mode toggle button to the control layout
        """
        self.debug_mode = False
        
        # Create debug button
        self.debug_btn = QPushButton("Enable Debug Mode")
        self.debug_btn.clicked.connect(self.toggle_debug_mode)
        
        # Find the control layout and add the button
        for i in range(self.centralWidget().layout().count()):
            item = self.centralWidget().layout().itemAt(i)
            if isinstance(item.layout(), QHBoxLayout):
                # Found a horizontal layout, likely the control layout
                item.layout().addWidget(self.debug_btn)
                break

    def toggle_debug_mode(self):
        """
        Toggle debug visualization mode
        """
        self.debug_mode = not self.debug_mode
        
        if self.debug_mode:
            self.debug_btn.setText("Disable Debug Mode")
        else:
            self.debug_btn.setText("Enable Debug Mode")

# Updates for MainWindow update_match_percentage method
    def update_match_percentage(self):
        """Update the match percentage display for the selected pose"""
        if not self.current_pose_signature or not self.selected_pose_id:
            self.match_label.setText("Match: --")
            self.match_label.setStyleSheet("color: white; background-color: #333333; padding: 5px;")
            return
                
        pose_data = self.keyboard_mapper.pose_map.get(self.selected_pose_id)
        if not pose_data or "signature" not in pose_data or not pose_data["signature"]:
            self.match_label.setText("Match: --")
            self.match_label.setStyleSheet("color: white; background-color: #333333; padding: 5px;")
            return
                
        # Get the threshold for this specific pose
        threshold = pose_data.get("threshold", 0.60)
        
        # Calculate similarity
        similarity = self.pose_detector.compare_poses(
            self.current_pose_signature, 
            pose_data["signature"]
        )
        
        # Update the match percentage text
        match_percent = int(similarity * 100)
        threshold_percent = int(threshold * 100)
        self.match_label.setText(f"Match: {match_percent}% (Threshold: {threshold_percent}%)")
        
        # Update color based on match quality
        if similarity > threshold:
            self.match_label.setStyleSheet("color: white; background-color: #4CAF50; padding: 5px;")
        else:
            self.match_label.setStyleSheet("color: white; background-color: #333333; padding: 5px;")
    
    def update_voice_status(self, is_listening):
        if is_listening:
            self.voice_status.setText("Voice: Listening...")
            self.voice_status.setStyleSheet("color: #4CAF50;")
        else:
            self.voice_status.setText("Voice: Ready")
            self.voice_status.setStyleSheet("color: #888888;")
    
    def load_saved_poses(self):
        """Load and display saved poses in the grid"""
        # Clear existing grid items
        for i in reversed(range(self.pose_grid.count())): 
            widget = self.pose_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Add poses to grid
        row, col = 0, 0
        max_cols = 3  # Number of columns in the grid as shown in the image
        
        for pose_id, pose_data in self.keyboard_mapper.pose_map.items():
            pose_widget = PoseWidget(
                pose_id,
                pose_data["name"],
                pose_data["key_combo"],
                pose_data.get("image_path")
            )
            # Connect both signals to their handlers
            pose_widget.selected.connect(self.on_pose_selected)
            pose_widget.double_clicked.connect(self.on_pose_double_clicked)
            
            self.pose_grid.addWidget(pose_widget, row, col)
            
            # Move to next position
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    
    @pyqtSlot(object)
    def update_frame(self, frame):
        """Update the camera view with the processed frame (already in RGB format)"""
        # The frame should already be in RGB format from the pose_detector
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.camera_view.setPixmap(QPixmap.fromImage(qt_image).scaled(
            self.camera_view.size(), Qt.KeepAspectRatio))
    
    @pyqtSlot(dict)
    def on_pose_detected(self, landmarks):
        """Process detected pose landmarks"""
        # Update current pose signature
        self.current_pose_signature = self.pose_detector.get_current_pose_signature()
        
        # If a pose is selected, update the match percentage display
        if self.selected_pose_id:
            self.update_match_percentage()
    
    # Modify check_current_pose
    def check_current_pose(self):
        """Check if current pose matches any saved poses"""
        # If tracking is disabled, release all keys and exit
        if not self.tracking_enabled:
            self.keyboard_mapper.release_all_keys()
            return
        
        # Ensure we have a valid pose signature
        if not self.current_pose_signature:
            # Release all keys if no pose is detected
            self.keyboard_mapper.release_all_keys()
            return
        
        # Update match percentage for selected pose
        self.update_match_percentage()
        
        # Check if pose matches any saved poses and trigger keys if it does
        matched_pose = self.keyboard_mapper.check_pose(
            self.pose_detector, 
            self.current_pose_signature
        )
        
        # Highlight matched pose in UI if there's a match
        if matched_pose:
            self.highlight_pose(matched_pose)
    

    def highlight_pose(self, pose_id):
        """Highlight the matched pose in the UI"""
        # Find the pose widget and highlight it
        for i in range(self.pose_grid.count()):
            widget = self.pose_grid.itemAt(i).widget()
            if isinstance(widget, PoseWidget) and widget.pose_id == pose_id:
                widget.highlight()
                # Schedule to remove highlight after 1 second
                QTimer.singleShot(1000, widget.remove_highlight)
    
    def capture_pose(self):
        """Capture the current pose for review"""
        # First ensure we have a valid pose signature
        if not self.current_pose_signature:
            # Try to get a fresh signature
            self.current_pose_signature = self.pose_detector.get_current_pose_signature()
            
        if not self.current_pose_signature:
            QMessageBox.warning(self, "Warning", "No pose detected! Please make sure your full body is visible in the camera.")
            return
                
        # Get current frame from camera view and make a deep copy
        current_pixmap = QPixmap(self.camera_view.pixmap())
        if current_pixmap:
            # Store the current pose signature with the review panel
            self.pose_review.current_signature = self.current_pose_signature
            
            # Show the review panel with the captured image
            self.pose_review.set_captured_image(current_pixmap)
        else:
            QMessageBox.warning(self, "Error", "Failed to capture camera image.")

    def save_reviewed_pose(self, name, key_combo, threshold, recognition_speed, immediate_release, sustained_duration):
        """Save a pose after review with advanced configuration"""
        print("\nSAVING REVIEWED POSE:")
        print(f"Name: {name}")
        print(f"Key combo: {key_combo}")
        print(f"Threshold: {threshold}")
        print(f"Recognition Speed: {recognition_speed}")
        print(f"Immediate Release: {immediate_release}")
        print(f"Sustained Duration: {sustained_duration}")
        
        # Use the signature stored in the pose_review panel
        signature = getattr(self.pose_review, 'current_signature', None)
        
        if not signature:
            # Fallback to the current signature
            signature = self.current_pose_signature
        
        if not signature:
            QMessageBox.warning(self, "Warning", "Pose data lost! Please recapture.")
            return
        
        # Create poses directory if it doesn't exist
        if not os.path.exists("poses"):
            os.makedirs("poses")
        
        # Generate a unique filename
        image_path = f"poses/pose_{len(self.keyboard_mapper.pose_map)}.png"
        
        # Save the current frame as an image
        if hasattr(self.pose_review, 'captured_image') and self.pose_review.captured_image:
            # Make another copy just to be safe
            save_pixmap = QPixmap(self.pose_review.captured_image)
            save_pixmap.save(image_path)
            
            # Add mapping with new parameters
            pose_id = self.keyboard_mapper.add_mapping(
                name,
                signature,
                key_combo,
                threshold,
                recognition_speed,
                immediate_release,
                sustained_duration
            )
            
            # Update the image path in the mapping
            self.keyboard_mapper.pose_map[pose_id]["image_path"] = image_path
            self.keyboard_mapper.save_poses()
            
            # Reload poses in the UI
            self.load_saved_poses()
            
            QMessageBox.information(self, "Success", f"Pose '{name}' mapped to '{key_combo}'")
        else:
            QMessageBox.warning(self, "Error", "Failed to save image. Please try capturing again.")

    
    def cancel_pose_review(self):
        """Cancel the pose review process"""
        # Nothing special needed here, the panel clears itself
        pass
    
    def save_to_file(self):
        """Save all poses to file"""
        self.keyboard_mapper.save_poses()
        QMessageBox.information(self, "Success", "Poses saved successfully!")
    
    def toggle_tracking(self):
        """Toggle pose tracking on/off"""
        self.tracking_enabled = not self.tracking_enabled
        
        # Also toggle landmark visibility
        self.pose_detector.set_draw_landmarks(self.tracking_enabled)
        
        if self.tracking_enabled:
            self.tracking_btn.setText("Stop Tracking")
        else:
            self.tracking_btn.setText("Start Tracking")
   
    def handle_voice_command(self, command):
        """Handle voice commands"""
        print(f"Processing command: {command}")  # Debug output
        
        if command == "CAPTURE":
            print("Executing capture command")  # Debug output
            self.capture_pose()
        elif command == "SAVE_DATA":
            print("Executing save data command")  # Debug output
            # Forward to pose review panel if visible
            if self.pose_review.isVisible():
                self.pose_review.handle_voice_command("SAVE_DATA")
            else:
                self.save_to_file()
        elif command == "EDIT":
            print("Executing edit command")  # Debug output
            self.edit_selected_pose()
        elif command == "DELETE":
            print("Executing delete command")  # Debug output
            self.delete_selected_pose()
        elif command == "START":
            print("Executing start command")  # Debug output
            if not self.tracking_enabled:
                self.toggle_tracking()
        elif command == "STOP":
            print("Executing stop command")  # Debug output
            if self.tracking_enabled:
                self.toggle_tracking()

   
    def on_pose_selected(self, pose_id):
        """Handle pose selection in the grid"""
        self.selected_pose_id = pose_id
        print(f"MainWindow: Pose selected: {pose_id}")
        # Update the match percentage display
        self.update_match_percentage()

    def on_pose_double_clicked(self, pose_id):
        """Handle pose double-click in the grid"""
        self.selected_pose_id = pose_id
        print(f"MainWindow: Pose double-clicked: {pose_id}")
        # Open the edit dialog
        self.edit_selected_pose()
    
    def edit_selected_pose(self):
        """Edit the selected pose"""
        if not self.selected_pose_id:
            QMessageBox.warning(self, "Warning", "No pose selected!")
            return
                
        pose_data = self.keyboard_mapper.pose_map.get(str(self.selected_pose_id))
        if not pose_data:
            return
        
        # Get all parameters with proper defaults
        threshold = pose_data.get("threshold", 0.60)
        recognition_speed = pose_data.get("recognition_speed", 500)
        immediate_release = pose_data.get("immediate_release", True)
        sustained_duration = pose_data.get("sustained_duration", 0)
        
        dialog = PoseEditDialog(
            self.selected_pose_id,
            pose_data["name"],
            pose_data["key_combo"],
            pose_data.get("image_path"),
            threshold,
            recognition_speed,
            immediate_release,
            sustained_duration,
            self
        )
        
        if dialog.exec_():
            updated_data = dialog.get_values()
            
            # Update the pose data with ALL new configuration parameters
            self.keyboard_mapper.pose_map[str(updated_data["pose_id"])] = {
                "name": updated_data["name"],
                "key_combo": updated_data["key_combo"],
                "threshold": updated_data["threshold"],
                "recognition_speed": updated_data["recognition_speed"],
                "immediate_release": updated_data["immediate_release"],
                "sustained_duration": updated_data["sustained_duration"],
                # Preserve existing signature and image path
                "signature": self.keyboard_mapper.pose_map[str(updated_data["pose_id"])].get("signature"),
                "image_path": self.keyboard_mapper.pose_map[str(updated_data["pose_id"])].get("image_path")
            }
            
            # Save changes
            self.keyboard_mapper.save_poses()
            
            # Reload the grid
            self.load_saved_poses()
            
            # Update the match percentage display if this is the currently selected pose
            if str(self.selected_pose_id) == str(updated_data["pose_id"]):
                self.update_match_percentage()

        # Add to MainWindow
    def mousePressEvent(self, event):
        """Handle mouse clicks on the main window to deselect poses"""
        # Only deselect if clicking on the window itself, not on a widget
        if event.pos().y() > self.pose_grid.geometry().bottom() or event.pos().y() < self.pose_grid.geometry().top():
            # Clear selected pose when clicking outside pose widgets
            self.selected_pose_id = None
            # Update all pose widgets to remove selection styling
            for i in range(self.pose_grid.count()):
                widget = self.pose_grid.itemAt(i).widget()
                if isinstance(widget, PoseWidget):
                    widget.is_selected = False
                    widget.update_styling()
        
        super().mousePressEvent(event)

    def delete_selected_pose(self):
        """Delete the selected pose"""
        if not hasattr(self, 'selected_pose_id') or not self.selected_pose_id:
            QMessageBox.warning(self, "Warning", "No pose selected!")
            return
            
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion",
            f"Are you sure you want to delete this pose?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Delete the image file if it exists
            pose_data = self.keyboard_mapper.pose_map.get(self.selected_pose_id)
            if pose_data and "image_path" in pose_data:
                image_path = pose_data["image_path"]
                if image_path and os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                    except Exception as e:
                        print(f"Error deleting image file: {e}")
            
            # Remove from keyboard mapper
            self.keyboard_mapper.remove_mapping(self.selected_pose_id)
            
            # Reload the grid
            self.load_saved_poses()
            
            # Clear selected pose
            self.selected_pose_id = None
            
    def closeEvent(self, event):
        """Clean up resources when closing"""
        self.camera_thread.stop()
        self.voice_listener.stop()
        super().closeEvent(event)
