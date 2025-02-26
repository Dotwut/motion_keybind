# Motion Keybind

## Overview

Motion Keybind is a Python application that allows you to map body poses detected by your webcam to keyboard inputs. This innovative tool lets you create custom keybindings using physical poses, making interactions more dynamic and intuitive.

## Features

- Real-time body pose detection using MediaPipe
- Map physical poses to keyboard inputs
- Voice command support
- Save and load pose configurations
- Cross-platform compatibility (Windows/macOS/Linux)

## Prerequisites

- Python 3.8 or higher
- Webcam
- Microphone (optional, for voice commands)

## Setup Instructions

### 1. Clone the Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/motion-keybind.git

# Navigate to the project directory
cd motion-keybind
```

### 2. Create a Virtual Environment

#### On Windows:
```powershell
# Create virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\activate
```

#### On macOS/Linux:
```bash
# Create virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Ensure you're in the project directory with the virtual environment activated
pip install -r requirements.txt
```

### 4. Install Additional System Dependencies

#### Windows:
- You may need to install Microsoft Visual C++ Redistributable
- Ensure you have the latest graphics drivers

#### macOS:
```bash
# Install portaudio for PyAudio
brew install portaudio
```

#### Linux (Ubuntu/Debian):
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-pyaudio portaudio19-dev
```

### 5. Launch the Application

```bash
# Run the application
python main.py
```

## Using Motion Keybind

### Pose Capture
1. Click "Capture Pose" to record a new pose
2. Position yourself in front of the webcam
3. Enter a name and key combination for the pose
4. Save the pose configuration

### Voice Commands
- Say "Capture" to start pose capture
- Say "Save" to save a pose
- Say "Start" to begin tracking
- Say "Stop" to halt tracking

### Tips
- Ensure good lighting and full body visibility
- Use clear, distinct poses
- Test keybindings in different applications

## Troubleshooting

### Common Issues
- Ensure webcam is connected and accessible
- Check microphone permissions
- Verify Python and dependency versions
- Restart the application if pose detection fails

### Debugging
- Enable debug mode in the application for detailed pose information
- Check console output for specific error messages

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.
