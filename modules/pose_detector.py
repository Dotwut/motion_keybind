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
        
        # Custom drawing specs to exclude face landmarks
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.custom_connections = [
            connection for connection in self.mp_pose.POSE_CONNECTIONS 
            if not (connection[0] < 11 and connection[1] < 11)  # Exclude face connections
        ]
        
        # Create custom drawing spec
        self.custom_drawing_spec = self.mp_drawing_styles.get_default_pose_landmarks_style()
        
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=1,  # Use a more accurate model
            smooth_landmarks=True
        )
        self.current_landmarks = None
        self.draw_landmarks = True
       
    def process_frame(self, frame):
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        
        # Draw pose landmarks on the frame only if drawing is enabled
        annotated_frame = frame.copy()
        if results.pose_landmarks and self.draw_landmarks:
            # Create a custom connection list excluding facial landmarks
            connections = [
                connection for connection in self.mp_pose.POSE_CONNECTIONS 
                if connection[0] >= 11 and connection[1] >= 11  # Skip facial landmarks (0-10)
            ]
            
            # Create a custom landmark list excluding facial landmarks
            landmarks_proto = results.pose_landmarks
            for i in range(11):  # Set visibility of facial landmarks to 0
                if i < len(landmarks_proto.landmark):
                    landmarks_proto.landmark[i].visibility = 0
            
            # Draw only body landmarks
            self.mp_drawing.draw_landmarks(
                annotated_frame, 
                landmarks_proto,
                connections
            )
            
            # Extract landmark positions (excluding face landmarks)
            landmarks = {}
            for idx, landmark in enumerate(results.pose_landmarks.landmark):
                if idx >= 11:  # Only include body landmarks
                    landmarks[idx] = {
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z,
                        'visibility': landmark.visibility
                    }
            
            self.current_landmarks = landmarks
            # Emit the landmarks
            self.pose_detected.emit(landmarks)
        elif results.pose_landmarks and not self.draw_landmarks:
            # Still extract landmarks but don't draw them
            landmarks = {}
            for idx, landmark in enumerate(results.pose_landmarks.landmark):
                if idx >= 11:  # Skip facial landmarks
                    landmarks[idx] = {
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z,
                        'visibility': landmark.visibility
                    }
            
            self.current_landmarks = landmarks
            # Emit the landmarks
            self.pose_detected.emit(landmarks)
            
        # Emit the processed frame
        self.processed_frame.emit(annotated_frame)

    def set_draw_landmarks(self, draw):
        """Set whether to draw landmarks on the frame"""
        self.draw_landmarks = draw

    def get_current_pose_signature(self):
        """Generate a signature for the current pose"""
        if not self.current_landmarks:
            return None
            
        signature = []
        
        # Get key joint positions (shoulders, elbows, wrists, hips, knees, ankles)
        # Exclude facial landmarks (0-10)
        key_points = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
        
        for point in key_points:
            if point in self.current_landmarks:
                landmark = self.current_landmarks[point]
                signature.append((landmark['x'], landmark['y']))
                
        return signature

        
    def compare_poses(self, pose1, pose2, threshold=0.15):
        """Compare two poses and return similarity score"""
        if not pose1 or not pose2 or len(pose1) != len(pose2):
            return 0
            
        total_distance = 0
        for p1, p2 in zip(pose1, pose2):
            # Calculate Euclidean distance
            distance = np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
            total_distance += distance
            
        avg_distance = total_distance / len(pose1)
        similarity = max(0, 1 - avg_distance / threshold)
        
        return similarity
