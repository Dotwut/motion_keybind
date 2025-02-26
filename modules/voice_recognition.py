import speech_recognition as sr
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import time

class VoiceListener(QThread):
    command_detected = pyqtSignal(str)
    listening_status = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.running = False
        # Update command definitions to be more flexible
        self.commands = {
            "capture": "CAPTURE",
            "save data": "SAVE_DATA",
            "save": "SAVE_DATA",
            "edit": "EDIT",
            "delete": "DELETE",
            "start": "START",  # Simplified from "start tracking"
            "stop": "STOP"     # Simplified from "stop tracking"
        }
        # Set extremely low threshold for all commands
        self.recognizer.energy_threshold = 100
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.pause_threshold = 0.5
    
    def run(self):
        self.running = True
        
        while self.running:
            with sr.Microphone() as source:
                # Minimal adjustment for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.1)
                
                # Keep threshold low for better distance detection
                self.recognizer.energy_threshold = 100
                
                self.listening_status.emit(True)
                try:
                    print("Listening for commands...")  # Debug output
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                    self.listening_status.emit(False)
                    
                    text = self.recognizer.recognize_google(audio).lower()
                    print(f"Recognized: {text}")  # Debug output
                    
                    # More permissive command matching
                    for command_text, command_action in self.commands.items():
                        if command_text in text:
                            print(f"Command detected: {command_action}")  # Debug output
                            self.command_detected.emit(command_action)
                            # Brief pause after command detection
                            time.sleep(0.5)
                            break
                            
                except sr.WaitTimeoutError:
                    self.listening_status.emit(False)
                except sr.UnknownValueError:
                    self.listening_status.emit(False)
                except sr.RequestError:
                    self.listening_status.emit(False)
                    print("Could not request results from Google Speech Recognition service")
                except Exception as e:
                    self.listening_status.emit(False)
                    print(f"Error in voice recognition: {e}")
                    
    def stop(self):
        self.running = False
        self.wait()
