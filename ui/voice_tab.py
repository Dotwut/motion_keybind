# ui/voice_tab.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QLineEdit, QHeaderView, QGroupBox, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal

class VoiceCommandEditor(QWidget):
    command_updated = pyqtSignal(str, str)  # old_command, new_command
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Command table
        self.command_table = QTableWidget(0, 2)
        self.command_table.setHorizontalHeaderLabels(["Voice Command", "Action"])
        self.command_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.command_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.command_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.command_table)
        
        # Edit controls
        edit_layout = QHBoxLayout()
        
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("New voice command phrase")
        
        self.update_btn = QPushButton("Update Command")
        self.update_btn.clicked.connect(self.update_command)
        
        edit_layout.addWidget(self.command_input)
        edit_layout.addWidget(self.update_btn)
        layout.addLayout(edit_layout)
        
        # Instructions
        instructions = QLabel("Select a command from the table above, then enter a new phrase to use for that command.")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
    def load_commands(self, commands):
        self.command_table.setRowCount(0)
        
        row = 0
        for command_text, action in commands.items():
            self.command_table.insertRow(row)
            self.command_table.setItem(row, 0, QTableWidgetItem(command_text))
            self.command_table.setItem(row, 1, QTableWidgetItem(action))
            row += 1
            
    def update_command(self):
        selected_rows = self.command_table.selectedItems()
        if not selected_rows:
            return
            
        selected_row = selected_rows[0].row()
        old_command = self.command_table.item(selected_row, 0).text()
        action = self.command_table.item(selected_row, 1).text()
        
        new_command = self.command_input.text()
        if not new_command:
            return
            
        # Update the table
        self.command_table.setItem(selected_row, 0, QTableWidgetItem(new_command))
        
        # Emit signal to update the command in the voice listener
        self.command_updated.emit(old_command, new_command)
        
        # Clear input
        self.command_input.clear()

class KeybindReference(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create a scrollable area for the keybind reference
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Common keybinds
        common_group = QGroupBox("Common Keybinds")
        common_layout = QVBoxLayout(common_group)
        
        common_keybinds = [
            "a-z, 0-9: Single letter/number keys",
            "ctrl+[key]: Control modifier",
            "shift+[key]: Shift modifier",
            "alt+[key]: Alt modifier",
            "f1-f12: Function keys",
            "num0-num9: Numpad keys",
            "up, down, left, right: Arrow keys",
            "space, enter, tab, esc: Special keys"
        ]
        
        for keybind in common_keybinds:
            common_layout.addWidget(QLabel(keybind))
            
        content_layout.addWidget(common_group)
        
        # Example combinations
        examples_group = QGroupBox("Example Combinations")
        examples_layout = QVBoxLayout(examples_group)
        
        example_keybinds = [
            "ctrl+a: Select all",
            "ctrl+c: Copy",
            "ctrl+v: Paste",
            "shift+a: Capital A",
            "alt+e: Special character",
            "ctrl+shift+s: Save as",
            "f1: Help",
            "num8+num6: Numpad diagonal"
        ]
        
        for keybind in example_keybinds:
            examples_layout.addWidget(QLabel(keybind))
            
        content_layout.addWidget(examples_group)
        
        # Tips
        tips_group = QGroupBox("Tips")
        tips_layout = QVBoxLayout(tips_group)
        
        tips = [
            "Use simple, memorable keybinds for common poses",
            "Avoid using Windows key combinations",
            "Test your keybinds in your game before saving",
            "Use modifiers (ctrl, alt, shift) for more options",
            "Function keys (F1-F12) work well for quick actions"
        ]
        
        for tip in tips:
            tips_layout.addWidget(QLabel(tip))
            
        content_layout.addWidget(tips_group)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)

class VoiceTab(QWidget):
    def __init__(self, voice_listener, parent=None):
        super().__init__(parent)
        self.voice_listener = voice_listener
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Voice commands section
        commands_group = QGroupBox("Voice Commands")
        commands_layout = QVBoxLayout(commands_group)
        
        # Add command editor
        self.command_editor = VoiceCommandEditor()
        self.command_editor.command_updated.connect(self.update_voice_command)
        self.command_editor.load_commands(self.voice_listener.commands)
        commands_layout.addWidget(self.command_editor)
        
        layout.addWidget(commands_group)
        
        # Keybind reference section
        keybind_group = QGroupBox("Keybind Reference")
        keybind_layout = QVBoxLayout(keybind_group)
        
        self.keybind_reference = KeybindReference()
        keybind_layout.addWidget(self.keybind_reference)
        
        layout.addWidget(keybind_group)
        
        # Best practices section
        practices_group = QGroupBox("Voice Command Best Practices")
        practices_layout = QVBoxLayout(practices_group)
        
        practices = [
            "Speak clearly and at a normal pace",
            "Use short, distinct commands",
            "Avoid similar-sounding commands",
            "Test commands in different environments",
            "Position yourself within range of the microphone",
            "Reduce background noise when possible"
        ]
        
        for practice in practices:
            practices_layout.addWidget(QLabel(practice))
            
        layout.addWidget(practices_group)
        
    def update_voice_command(self, old_command, new_command):
        """Update a voice command in the voice listener"""
        if old_command in self.voice_listener.commands:
            action = self.voice_listener.commands[old_command]
            del self.voice_listener.commands[old_command]
            self.voice_listener.commands[new_command] = action
