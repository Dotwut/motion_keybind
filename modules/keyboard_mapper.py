from pynput.keyboard import Controller, Key
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import json
import os
import time

class KeyboardMapper(QObject):
    key_triggered = pyqtSignal(str)
    
    def __init__(self, poses_dir="poses"):
        super().__init__()
        self.keyboard = Controller()
        self.pose_map = {}  # Maps pose signatures to key combinations
        self.poses_dir = poses_dir
        
        # Track currently pressed keys
        self.currently_pressed_keys = set()
        
        # Timers for sustained key presses
        self.key_timers = {}
        
        # Create poses directory if it doesn't exist
        if not os.path.exists(poses_dir):
            os.makedirs(poses_dir)
            
        # Load existing poses
        self.load_poses()
    
    def trigger_key(self, pose_id, release_only=False):
        """Trigger a keyboard combination with enhanced configuration options"""
        # If pose_id is a string representation of a pose, convert it
        if isinstance(pose_id, str):
            pose_data = self.pose_map.get(pose_id, {})
        else:
            # Assume it's a direct pose dictionary
            pose_data = pose_id
            pose_id = self._find_pose_id_by_key_combo(pose_data.get('key_combo'))
        
        key_combo = pose_data.get('key_combo', '')
        
        print(f"\n--- {'RELEASING' if release_only else 'TRIGGERING'} KEY: {key_combo} ---")
        
        try:
            keys = key_combo.split('+')
            
            # Determine key press behavior based on pose configuration
            immediate_release = pose_data.get('immediate_release', True)
            sustained_duration = pose_data.get('sustained_duration', 0)
            
            # Press keys
            if not release_only:
                for key in keys:
                    key = key.strip().lower()
                    # Only press if not already pressed
                    if key not in self.currently_pressed_keys:
                        self._press_single_key(key)
                        self.currently_pressed_keys.add(key)
                
                # Handle sustained key press if configured
                if not immediate_release and sustained_duration > 0:
                    self._setup_key_timer(key_combo, sustained_duration)
            
            # Release keys if immediate release is enabled
            if immediate_release or release_only:
                for key in reversed(keys):
                    key = key.strip().lower()
                    if key in self.currently_pressed_keys:
                        self._release_single_key(key)
                        self.currently_pressed_keys.discard(key)
            
            print(f"--- KEY COMBINATION {key_combo} {'RELEASED' if release_only else 'TRIGGERED'} SUCCESSFULLY ---")
        except Exception as e:
            print(f"CRITICAL ERROR {'releasing' if release_only else 'triggering'} key combination {key_combo}: {e}")
    
    def _press_single_key(self, key):
        """Press a single key with error handling"""
        try:
            if key in ['ctrl', 'alt', 'shift']:
                self.keyboard.press(getattr(Key, key))
            elif key.startswith('f') and key[1:].isdigit() and 1 <= int(key[1:]) <= 24:
                self.keyboard.press(getattr(Key, key))
            elif key.startswith('num') and key[3:].isdigit():
                self.keyboard.press(getattr(Key, f'num_{key[3:]}'))
            elif len(key) == 1:
                self.keyboard.press(key)
            else:
                self.keyboard.press(getattr(Key, key))
        except Exception as e:
            print(f"Error pressing key '{key}': {e}")
    
    def _release_single_key(self, key):
        """Release a single key with error handling"""
        try:
            if key in ['ctrl', 'alt', 'shift']:
                self.keyboard.release(getattr(Key, key))
            elif key.startswith('f') and key[1:].isdigit() and 1 <= int(key[1:]) <= 24:
                self.keyboard.release(getattr(Key, key))
            elif key.startswith('num') and key[3:].isdigit():
                self.keyboard.release(getattr(Key, f'num_{key[3:]}'))
            elif len(key) == 1:
                self.keyboard.release(key)
            else:
                self.keyboard.release(getattr(Key, key))
        except Exception as e:
            print(f"Error releasing key '{key}': {e}")
    
    def _setup_key_timer(self, key_combo, duration):
        """Set up a timer to release keys after a specified duration"""
        # Cancel any existing timer for this key combo
        if key_combo in self.key_timers:
            existing_timer = self.key_timers[key_combo]
            existing_timer.stop()
            existing_timer.deleteLater()
        
        # Create a new timer
        timer = QTimer()
        timer.setSingleShot(True)
        
        # Create a lambda that captures the key_combo
        timer.timeout.connect(lambda: self.trigger_key(self._find_pose_id_by_key_combo(key_combo), release_only=True))
        
        # Start the timer
        timer.start(int(duration * 1000))  # Convert to milliseconds
        
        # Store the timer
        self.key_timers[key_combo] = timer

    def _find_pose_id_by_key_combo(self, key_combo):
        """Find the pose ID associated with a given key combination"""
        for pose_id, pose_data in self.pose_map.items():
            if pose_data.get('key_combo') == key_combo:
                return pose_id
        return None
    
    def add_mapping(self, pose_name, pose_signature, key_combo, 
                    threshold=0.75, 
                    recognition_speed=500,  # ms between pose checks
                    immediate_release=True, 
                    sustained_duration=0):
        """Add a mapping with advanced configuration options"""
        print("\nSAVING NEW POSE:")
        print(f"Pose Name: {pose_name}")
        print(f"Key Combo: {key_combo}")
        print(f"Threshold: {threshold}")
        print(f"Recognition Speed: {recognition_speed}ms")
        print(f"Immediate Release: {immediate_release}")
        print(f"Sustained Duration: {sustained_duration}s")
        
        # Create a deep copy to prevent reference issues
        if pose_signature:
            saved_signature = [tuple(point) for point in pose_signature]
        else:
            saved_signature = None
        
        pose_id = str(len(self.pose_map))
        self.pose_map[pose_id] = {
            "name": pose_name,
            "signature": saved_signature,
            "key_combo": key_combo,
            "threshold": threshold,
            "recognition_speed": recognition_speed,
            "immediate_release": immediate_release,
            "sustained_duration": sustained_duration,
            "image_path": None
        }
        self.save_poses()
        
        print(f"Saved pose with ID: {pose_id}")
        return pose_id

    def check_pose(self, pose_detector, current_signature):
        """Check if a pose matches any known mappings with advanced pose tracking"""
        if not current_signature:
            # If no current signature, release all keys
            self.release_all_keys()
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
            except Exception as e:
                print(f"  ERROR comparing poses: {str(e)}")
                continue
        
        if best_match:
            print(f"FOUND BEST MATCH: {best_match} with score {best_score:.4f}")
            
            # Trigger the key
            key_combo = self.pose_map[best_match]["key_combo"]
            self.key_triggered.emit(key_combo)
            
            # Check if this is a movement pose
            if len(key_combo) == 1 and key_combo.lower() in 'wasd':
                # Special handling for movement keys
                # Only press the key if it's not already pressed
                if key_combo not in self.currently_pressed_keys:
                    self.trigger_key(best_match)
            else:
                # Regular key triggering for other types of poses
                self.trigger_key(best_match)
            
            return best_match
        
        # If no match found, release all keys
        self.release_all_keys()
        print(f"No matching pose found. Best score was {best_score:.4f}")
        return None

    # Existing methods like save_poses, load_poses remain the same
   
    def save_poses(self):
        """Save all pose mappings to file with proper JSON serialization"""
        print("\nSAVING POSES TO FILE:")
        config_path = os.path.join(self.poses_dir, "poses.json")
        
        # Prepare a copy of the pose map for serialization
        serializable_map = {}
        for pose_id, pose_data in self.pose_map.items():
            # Create a deep copy
            pose_copy = pose_data.copy()
            
            # Convert tuple signatures to lists for JSON serialization
            if pose_copy.get("signature"):
                pose_copy["signature"] = [list(point) for point in pose_copy["signature"]]
            
            serializable_map[pose_id] = pose_copy
            
            print(f"Saving Pose {pose_id} ({pose_data.get('name', 'unnamed')}):")
            for key, value in pose_copy.items():
                print(f"  {key}: {value}")
        
        # Save to file
        try:
            with open(config_path, 'w') as f:
                json.dump(serializable_map, f, indent=2)
            print(f"Successfully saved poses to {config_path}")
        except Exception as e:
            print(f"ERROR saving poses: {str(e)}")
                
    def load_poses(self):
        """Load pose mappings from file with proper conversion"""
        config_path = os.path.join(self.poses_dir, "poses.json")
        print(f"\nLOADING POSES FROM: {config_path}")
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    loaded_map = json.load(f)
                    
                # Convert loaded data back to the format we need
                for pose_id, pose_data in loaded_map.items():
                    # Convert signature points from lists back to tuples
                    if pose_data.get("signature"):
                        pose_data["signature"] = [tuple(point) for point in pose_data["signature"]]
                        
                self.pose_map = loaded_map
                
                # Debug info
                print(f"Loaded {len(self.pose_map)} poses:")
                for pose_id, pose_data in self.pose_map.items():
                    print(f"  Pose {pose_id} ({pose_data.get('name', 'unnamed')}):")
                    print(f"  Signature type: {type(pose_data.get('signature'))}")
                    print(f"  Signature length: {len(pose_data.get('signature', [])) if pose_data.get('signature') else 'None'}")
                    
            except Exception as e:
                print(f"ERROR loading poses: {str(e)}")
                # Initialize with empty dict if load fails
                self.pose_map = {}
        else:
            print("No poses file found. Starting with empty pose map.")
            self.pose_map = {}

    def add_mapping(self, pose_name, pose_signature, key_combo, 
                    threshold=0.75, 
                    recognition_speed=500,
                    immediate_release=True, 
                    sustained_duration=0):
        """Add a mapping with advanced configuration options"""
        print("\nSAVING NEW POSE:")
        print(f"Pose Name: {pose_name}")
        print(f"Key Combo: {key_combo}")
        print(f"Threshold: {threshold}")
        print(f"Recognition Speed: {recognition_speed}ms")
        print(f"Immediate Release: {immediate_release}")
        print(f"Sustained Duration: {sustained_duration}s")
        
        # Create a deep copy to prevent reference issues
        if pose_signature:
            saved_signature = [tuple(point) for point in pose_signature]
        else:
            saved_signature = None
        
        pose_id = str(len(self.pose_map))
        self.pose_map[pose_id] = {
            "name": pose_name,
            "signature": saved_signature,
            "key_combo": key_combo,
            "threshold": threshold,
            "recognition_speed": recognition_speed,
            "immediate_release": immediate_release,
            "sustained_duration": sustained_duration,
            "image_path": None
        }
        self.save_poses()
        
        print(f"Saved pose with ID: {pose_id}")
        return pose_id
    
    def remove_mapping(self, pose_id):
        """Remove a pose mapping"""
        print(f"\nREMOVING POSE: {pose_id}")
        
        if pose_id in self.pose_map:
            # Log the details of the pose being removed
            pose_data = self.pose_map[pose_id]
            print(f"Pose Name: {pose_data.get('name', 'Unnamed Pose')}")
            print(f"Key Combo: {pose_data.get('key_combo', 'N/A')}")
            
            # Remove the pose from the map
            del self.pose_map[pose_id]
            
            # Save the updated poses
            self.save_poses()
            
            print(f"Pose {pose_id} removed successfully")
        else:
            print(f"No pose found with ID: {pose_id}")

    def release_all_keys(self):
        """Release all currently pressed keys"""
        print("\n--- RELEASING ALL KEYS ---")
        
        # Create a copy of the currently pressed keys to avoid modifying the set during iteration
        for key_combo in list(self.currently_pressed_keys):
            try:
                print(f"Releasing key combination: {key_combo}")
                self.trigger_key(key_combo, release_only=True)
            except Exception as e:
                print(f"Error releasing key {key_combo}: {e}")
        
        # Clear the set of currently pressed keys
        self.currently_pressed_keys.clear()

def validate_keybind(keybind):
    """Validate the entered keybind to ensure it is supported."""
    try:
        # Split the key combination
        keys = keybind.split('+')
        
        # Check if all parts of the combination are valid
        for key in keys:
            key = key.strip().lower()
            # We'll be very permissive here, just doing basic validation
            if len(key) == 0:
                return False, "Empty key in combination"
                
        return True, "Valid keybind"
    except Exception as e:
        return False, f"Error validating keybind: {str(e)}"

