import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage

class CameraThread(QThread):
    frame_ready = pyqtSignal(QImage)
    raw_frame_ready = pyqtSignal(np.ndarray)
    
    def __init__(self, camera_id=0):
        super().__init__()
        self.camera_id = camera_id
        self.running = False
        
    def run(self):
        self.running = True
        cap = cv2.VideoCapture(self.camera_id)
        
        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue
                
            # Emit the raw frame for pose detection
            self.raw_frame_ready.emit(frame)
            
            # Try a different approach to color conversion
            # Convert BGR to RGB directly without intermediate steps
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Create QImage without any additional processing
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.frame_ready.emit(qt_image)
            
        cap.release()

    def stop(self):
        self.running = False
        self.wait()
