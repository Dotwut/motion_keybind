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
        
        # Convert back to RGB for displaying in PyQt
        annotated_frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        
        # Emit the processed frame
        self.processed_frame.emit(annotated_frame_rgb)

    def set_draw_landmarks(self, draw):
        """Set whether to draw landmarks on the frame"""
        self.draw_landmarks = draw

    # Replace these two methods in your PoseDetector class

    def get_current_pose_signature(self):
        """Generate a comprehensive pose signature using multiple body regions"""
        if not self.current_landmarks:
            return None
        
        # Define key body regions with their corresponding landmark indices
        body_regions = {
            'shoulders': [11, 12],  # Left and right shoulders
            'torso': [23, 24, 11, 12],  # Left and right hip, left and right shoulder
            'arms': [13, 14, 15, 16],  # Left and right elbows, wrists
            'hands': [15, 16, 19, 20],  # Wrists and hand landmarks
            'legs': [23, 24, 25, 26],  # Left and right hip, knee
            'feet': [27, 28, 31, 32]   # Left and right ankle, heel
        }
        
        # Collect valid landmarks
        valid_points = []
        
        # Check for shoulders (reference points)
        if 11 not in self.current_landmarks or 12 not in self.current_landmarks:
            print("Shoulders not clearly visible")
            return None
        
        # Calculate body center and scale using shoulders
        left_shoulder = (self.current_landmarks[11]['x'], self.current_landmarks[11]['y'])
        right_shoulder = (self.current_landmarks[12]['x'], self.current_landmarks[12]['y'])
        
        center_x = (left_shoulder[0] + right_shoulder[0]) / 2
        center_y = (left_shoulder[1] + right_shoulder[1]) / 2
        shoulder_width = np.sqrt((left_shoulder[0] - right_shoulder[0])**2 + 
                                (left_shoulder[1] - right_shoulder[1])**2)
        
        # Collect landmarks from all body regions with sufficient visibility
        signature = []
        total_landmarks_used = 0
        
        for region, landmarks in body_regions.items():
            region_points = []
            for landmark_id in landmarks:
                if (landmark_id in self.current_landmarks and 
                    self.current_landmarks[landmark_id]['visibility'] > 0.5):
                    point = (self.current_landmarks[landmark_id]['x'], 
                            self.current_landmarks[landmark_id]['y'])
                    
                    # Normalize relative to body center and scale
                    norm_x = (point[0] - center_x) / shoulder_width
                    norm_y = (point[1] - center_y) / shoulder_width
                    
                    region_points.append((norm_x, norm_y))
            
            # If we have at least half the landmarks for a region, include it
            if len(region_points) >= len(landmarks) / 2:
                signature.extend(region_points)
                total_landmarks_used += len(region_points)
        
        # Ensure we have a meaningful number of points
        if total_landmarks_used < 10:
            print(f"Not enough landmarks detected: {total_landmarks_used}")
            return None
        
        print(f"Created comprehensive pose signature with {total_landmarks_used} points")
        return signature

    def compare_poses(self, pose1, pose2):
        """Enhanced pose comparison with more sophisticated similarity calculation"""
        # Basic validation
        if pose1 is None or pose2 is None:
            print("Cannot compare: One or both pose signatures are None")
            return 0.0
        
        if not isinstance(pose1, list) or not isinstance(pose2, list):
            print(f"Type error: pose1 is {type(pose1)}, pose2 is {type(pose2)}")
            return 0.0
        
        if len(pose1) == 0 or len(pose2) == 0:
            print("Cannot compare: Empty pose signatures")
            return 0.0
        
        # Account for different numbers of points
        common_len = min(len(pose1), len(pose2))
        
        # Calculate distances between points with region-based weighting
        total_dist = 0.0
        valid_points = 0
        weighted_dist = 0.0
        
        # Define region weights (you can adjust these)
        region_weights = {
            0: 1.0,  # First points (e.g., shoulders)
            1: 1.0,
            2: 1.2,  # Torso points might be more important
            3: 1.2,
            4: 1.1,  # Arms slightly less critical
            5: 1.1,
            6: 0.9,  # Hands and extremities less critical
            7: 0.9
        }
        
        for i in range(common_len):
            try:
                p1 = pose1[i]
                p2 = pose2[i]
                
                # Skip invalid points
                if len(p1) != 2 or len(p2) != 2:
                    continue
                    
                # Calculate Euclidean distance
                dist = np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
                
                # Apply region-based weighting
                weight = region_weights.get(i, 1.0)
                weighted_dist += dist * weight
                
                total_dist += dist
                valid_points += 1
            except Exception as e:
                print(f"Error comparing point {i}: {str(e)}")
                continue
        
        # Check if we have any valid comparisons
        if valid_points == 0:
            return 0.0
        
        # Calculate average distances
        avg_dist = total_dist / valid_points
        avg_weighted_dist = weighted_dist / valid_points
        
        # More sophisticated similarity calculation
        # Prioritize lower distances and apply a non-linear transformation
        similarity = 1.0 / (1.0 + 4.0 * avg_weighted_dist)
        
        # Apply a curve to enhance similarities
        if similarity > 0.6:
            similarity = 0.6 + (similarity - 0.6) * 1.5
            similarity = min(similarity, 1.0)
        
        print(f"Pose comparison:")
        print(f"  Total points: {valid_points}")
        print(f"  Average distance: {avg_dist:.4f}")
        print(f"  Weighted distance: {avg_weighted_dist:.4f}")
        print(f"  Similarity: {similarity:.4f}")
        
        return similarity
    
    def visualize_pose_signature(frame, signature, color=(0, 255, 0), thickness=2):
        """
        Visualize a pose signature on a frame for debugging
        
        Args:
            frame: The image frame to draw on
            signature: The pose signature to visualize
            color: Color for drawing points and lines
            thickness: Line thickness
        
        Returns:
            The frame with visualization drawn on it
        """
        if not signature:
            return frame
        
        # Get frame dimensions
        h, w = frame.shape[:2]
        
        # Draw the reference point (center of visualization)
        center_x, center_y = w // 2, h // 2
        cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)
        
        # Scale factor to make the visualization visible
        # Normalized coordinates are usually very small
        scale = min(w, h) // 3
        
        # Draw each point in the signature
        for i, (norm_x, norm_y) in enumerate(signature):
            # Convert normalized coordinates to pixel coordinates
            px = int(center_x + norm_x * scale)
            py = int(center_y + norm_y * scale)
            
            # Make sure point is within frame bounds
            px = max(0, min(w-1, px))
            py = max(0, min(h-1, py))
            
            # Draw the point
            cv2.circle(frame, (px, py), 4, color, -1)
            
            # Label the point
            cv2.putText(frame, str(i), (px+5, py-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            # Draw line from center to point
            cv2.line(frame, (center_x, center_y), (px, py), color, thickness)
        
        return frame

    def create_debug_frame(self, frame):
        """
        Create a debug visualization frame showing the current pose signature
        
        Args:
            frame: The current camera frame
        
        Returns:
            A visualization frame for debugging
        """
        # Create a copy of the frame to draw on
        debug_frame = frame.copy()
        
        # Get the current pose signature
        signature = self.get_current_pose_signature()
        
        # Import the function from the global scope
        from modules.pose_detector import visualize_pose_signature
        # Draw the signature on the frame
        if signature:
            debug_frame = visualize_pose_signature(debug_frame, signature)
            
            # Add debug text
            cv2.putText(
                debug_frame, 
                f"Pose Points: {len(signature)}", 
                (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.7, 
                (0, 255, 0), 
                2
            )
        else:
            # Show error message if no signature
            cv2.putText(
                debug_frame, 
                "No valid pose detected", 
                (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.7, 
                (0, 0, 255), 
                2
            )
        
        return debug_frame

    # This method should replace the existing update_frame method in MainWindow
    def update_frame(self, frame):
        """Update the camera view with the processed frame"""
        if hasattr(self, 'debug_mode') and self.debug_mode:
            # Create and show debug visualization instead of normal frame
            debug_frame = self.pose_detector.create_debug_frame(frame)
            frame = debug_frame
        
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.camera_view.setPixmap(QPixmap.fromImage(qt_image).scaled(
            self.camera_view.size(), Qt.KeepAspectRatio))
        
    def check_pose(self, pose_detector, current_signature):
        print("\n--- CHECKING CURRENT POSE ---")
        print(f"Current signature available: {current_signature is not None}")
        
        if not current_signature:
            print("No current pose signature to check")
            return None
        
        print(f"\nCHECKING CURRENT POSE against {len(self.pose_map)} saved poses")
        print(f"Current signature type: {type(current_signature)}")
        print(f"Current signature length: {len(current_signature)}")
        
        best_match = None
        best_score = 0
        
        for pose_id, pose_data in self.pose_map.items():
            saved_signature = pose_data.get("signature")
            threshold = pose_data.get("threshold", 0.6)
            
            print(f"\nPose {pose_id} ({pose_data.get('name', 'unnamed')}):")
            print(f"  Saved signature type: {type(saved_signature)}")
            print(f"  Saved signature length: {len(saved_signature) if saved_signature else 'None'}")
            
            if not saved_signature:
                print("  ERROR: No saved signature for this pose")
                continue
            
            # Calculate similarity
            try:
                similarity = pose_detector.compare_poses(current_signature, saved_signature)
                print(f"  Similarity: {similarity:.4f}, Threshold: {threshold:.4f}")
                
                if similarity > threshold and similarity > best_score:
                    best_score = similarity
                    best_match = pose_id
                    print(f"  NEW BEST MATCH: {best_match} with score {best_score:.4f}")
            except Exception as e:
                print(f"  ERROR comparing poses: {str(e)}")
                continue
        
        if best_match:
            print(f"FOUND BEST MATCH: {best_match} with score {best_score:.4f}")
            print(f"Triggering key: {self.pose_map[best_match]['key_combo']}")
            return best_match
        
        print(f"No matching pose found. Best score was {best_score:.4f}")
        return None