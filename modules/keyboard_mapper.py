from pynput.keyboard import Controller, Key
from PyQt5.QtCore import QObject

class KeyboardMapper(QObject):
    def __init__(self):
        super().__init__()
        self.keyboard = Controller()
        self.pose_map = {}  # Maps pose signatures to key combinations
        
    def add_mapping(self, pose_signature, key_combo):
        """Add a mapping between a pose signature and keys"""
        self.pose_map[str(pose_signature)] = key_combo
        
    def remove_mapping(self, pose_signature):
        """Remove a pose mapping"""
        if str(pose_signature) in self.pose_map:
            del self.pose_map[str(pose_signature)]
    
    def trigger_key(self, key_combo):
        """Trigger a keyboard combination"""
        keys = key_combo.split('+')
        
        # Press all keys in the combination
        for key in keys:
            if hasattr(Key, key.lower()):
                self.keyboard.press(getattr(Key, key.lower()))
            else:
                self.keyboard.press(key)
                
        # Release all keys
        for key in reversed(keys):
            if hasattr(Key, key.lower()):
                self.keyboard.release(getattr(Key, key.lower()))
            else:
                self.keyboard.release(key)
                
    def check_pose(self, pose_signature):
        """Check if a pose matches any known mappings and trigger keys"""
        pose_str = str(pose_signature)
        if pose_str in self.pose_map:
            self.trigger_key(self.pose_map[pose_str])
            return True
        return False
