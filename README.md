@"
# Motion Keybind

A Python application that captures body poses from a webcam and maps them to keyboard inputs for gaming.

## Features

- Real-time pose detection using MediaPipe
- Map physical poses to keyboard inputs
- Voice command support
- Save and load pose configurations

## Setup

1. Clone this repository
2. Create a virtual environment: \`python -m venv venv\`
3. Activate the virtual environment: \`.\venv\Scripts\activate\` (Windows)
4. Install dependencies: \`pip install -r requirements.txt\`
5. Run the application: \`python main.py\`

## Requirements

- Python 3.8+
- Webcam
- Windows/macOS/Linux
"@ | Out-File -FilePath README.md -Encoding utf8
