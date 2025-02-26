import cv2
import mediapipe as mp
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal

class PoseDetector(QObject):
    pose_detected = pyqtSignal(dict)
    processed_frame = pyqtSignal(np.ndarray)
    
    def __init__(self):
        super().__init__()
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
    def process_frame(self, frame):
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        
        # Draw pose landmarks on the frame
        annotated_frame = frame.copy()
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                annotated_frame, 
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS
            )
            
            # Extract landmark positions
            landmarks = {}
            for idx, landmark in enumerate(results.pose_landmarks.landmark):
                landmarks[idx] = {
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z,
                    'visibility': landmark.visibility
                }
            
            # Emit the landmarks
            self.pose_detected.emit(landmarks)
            
        # Emit the processed frame
        self.processed_frame.emit(annotated_frame)
        
    def get_pose_signature(self, landmarks):
        """Generate a signature for the current pose for comparison"""
        # This is a simplified version - would need more sophisticated
        # angle calculations for production use
        signature = []
        
        # Calculate some key angles between joints
        # Example: angle between shoulders and elbows
        # More calculations would be needed for a robust system
        
        return signature
