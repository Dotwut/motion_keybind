from pynput.keyboard import Controller, Key
from PyQt5.QtCore import QObject, pyqtSignal
import json
import os

class KeyboardMapper(QObject):
    key_triggered = pyqtSignal(str)
    
    def __init__(self, poses_dir="poses"):
        super().__init__()
        self.keyboard = Controller()
        self.pose_map = {}  # Maps pose signatures to key combinations
        self.poses_dir = poses_dir
        
        # Create poses directory if it doesn't exist
        if not os.path.exists(poses_dir):
            os.makedirs(poses_dir)
            
        # Load existing poses
        self.load_poses()
        
    def add_mapping(self, pose_name, pose_signature, key_combo, threshold=0.75):
        """Add a mapping between a pose signature and keys"""
        pose_id = str(len(self.pose_map))
        self.pose_map[pose_id] = {
            "name": pose_name,
            "signature": pose_signature,
            "key_combo": key_combo,
            "threshold": threshold,  # Add threshold parameter
            "image_path": None
        }
        self.save_poses()
        return pose_id
        
    def remove_mapping(self, pose_id):
        """Remove a pose mapping"""
        if pose_id in self.pose_map:
            del self.pose_map[pose_id]
            self.save_poses()
    
    def trigger_key(self, key_combo):
        """Trigger a keyboard combination"""
        try:
            keys = key_combo.split('+')
            
            # Press all keys in the combination
            for key in keys:
                key = key.strip().lower()
                if key in ['ctrl', 'alt', 'shift']:
                    self.keyboard.press(getattr(Key, key))
                elif key.startswith('f') and key[1:].isdigit() and 1 <= int(key[1:]) <= 24:
                    self.keyboard.press(getattr(Key, key))
                elif key.startswith('num') and key[3:].isdigit():
                    # Handle numpad keys
                    self.keyboard.press(getattr(Key, f'num_{key[3:]}'))
                elif len(key) == 1:
                    # Single character keys
                    self.keyboard.press(key)
                else:
                    # Try to find the key in Key enum
                    try:
                        self.keyboard.press(getattr(Key, key))
                    except AttributeError:
                        # If not found, just press it as a regular key
                        self.keyboard.press(key)
                    
            # Release all keys
            for key in reversed(keys):
                key = key.strip().lower()
                if key in ['ctrl', 'alt', 'shift']:
                    self.keyboard.release(getattr(Key, key))
                elif key.startswith('f') and key[1:].isdigit() and 1 <= int(key[1:]) <= 24:
                    self.keyboard.release(getattr(Key, key))
                elif key.startswith('num') and key[3:].isdigit():
                    # Handle numpad keys
                    self.keyboard.release(getattr(Key, f'num_{key[3:]}'))
                elif len(key) == 1:
                    # Single character keys
                    self.keyboard.release(key)
                else:
                    # Try to find the key in Key enum
                    try:
                        self.keyboard.release(getattr(Key, key))
                    except AttributeError:
                        # If not found, just release it as a regular key
                        self.keyboard.release(key)
        except Exception as e:
            print(f"Error triggering key combination {key_combo}: {e}")

                
    def check_pose(self, pose_detector, current_signature):
        """Check if a pose matches any known mappings and trigger keys"""
        best_match = None
        best_score = 0
        
        for pose_id, pose_data in self.pose_map.items():
            saved_signature = pose_data["signature"]
            # Get the custom threshold for this pose, or use default
            threshold = pose_data.get("threshold", 0.75)
            
            similarity = pose_detector.compare_poses(current_signature, saved_signature)
            
            if similarity > threshold and similarity > best_score:
                best_score = similarity
                best_match = pose_id
                
        if best_match:
            self.trigger_key(self.pose_map[best_match]["key_combo"])
            return best_match
            
        return None

        
    def save_poses(self):
        """Save all pose mappings to file"""
        config_path = os.path.join(self.poses_dir, "poses.json")
        with open(config_path, 'w') as f:
            json.dump(self.pose_map, f)
            
    def load_poses(self):
        """Load pose mappings from file"""
        config_path = os.path.join(self.poses_dir, "poses.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.pose_map = json.load(f)

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

