# Dotwut's MoCapApp

![image](https://github.com/user-attachments/assets/953749a9-0810-4b7c-95e7-c0962a89f044)

## Overview

Dotwut's MoCapApp is a Python application that allows you to map body poses detected by your webcam to keyboard inputs. This innovative tool lets you create custom keybindings using physical poses, making interactions more dynamic and intuitive.

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

## Using Dotwut's MoCapApp

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

## Copyright and License

### Copyright Notice
Copyright © 2024 [Jason Hartman]. All Rights Reserved.

### Licensing
This project is distributed under the MIT License. 

#### MIT License Summary
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

- The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.

See the `LICENSE` file for full details.

## Trademark
Dotwut's MoCapApp™ is a trademark of [Jason Hartman/Dotwut].

## Contact

Name: [Jason Hartman]
Email: dotwut@dotwut.io

## Attribution
This software uses the following key technologies:
- MediaPipe by Google
- PyQt5
- OpenCV
- TensorFlow
