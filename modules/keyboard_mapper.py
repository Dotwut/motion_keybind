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
        """Add a mapping between a pose signature and keys with detailed debugging"""
        # Debug info about the signature being saved
        print("\nSAVING NEW POSE:")
        print(f"Pose Name: {pose_name}")
        print(f"Key Combo: {key_combo}")
        print(f"Threshold: {threshold}")
        print(f"Signature Type: {type(pose_signature)}")
        print(f"Signature Length: {len(pose_signature) if pose_signature else 'None'}")
        
        if pose_signature:
            print("Signature Points:")
            for i, point in enumerate(pose_signature):
                print(f"  Point {i}: {point}")
        
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
            "image_path": None
        }
        self.save_poses()
        
        print(f"Saved pose with ID: {pose_id}")
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
        """Check if a pose matches any known mappings and trigger keys with better debugging"""
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
            except Exception as e:
                print(f"  ERROR comparing poses: {str(e)}")
                continue
        
        if best_match:
            print(f"FOUND BEST MATCH: {best_match} with score {best_score:.4f}")
            # Trigger the key
            self.key_triggered.emit(self.pose_map[best_match]["key_combo"])
            self.trigger_key(self.pose_map[best_match]["key_combo"])
            return best_match
        
        print(f"No matching pose found. Best score was {best_score:.4f}")
        return None

        
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
            
            print(f"Pose {pose_id} ({pose_data.get('name', 'unnamed')}):")
            print(f"  Original signature type: {type(pose_data.get('signature'))}")
            print(f"  Serialized signature type: {type(pose_copy.get('signature'))}")
        
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

