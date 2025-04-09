# Mission Impossible Supercut Application - User Guide

## Overview

The Mission Impossible Supercut Application is a specialized video processing tool designed to analyze Mission Impossible movies, identify action sequences, and compile them into a single supercut video. This guide provides comprehensive instructions for installing, configuring, and using the application.

## Table of Contents

1. [Installation](#installation)
2. [Application Components](#application-components)
3. [Command-Line Interface](#command-line-interface)
4. [Graphical User Interface](#graphical-user-interface)
5. [Configuration Options](#configuration-options)
6. [Workflow Examples](#workflow-examples)
7. [Troubleshooting](#troubleshooting)
8. [Legal Considerations](#legal-considerations)

## Installation

### System Requirements

- Python 3.9 or higher
- FFmpeg installed and available in PATH
- Minimum 8GB RAM (16GB recommended for HD videos)
- GPU recommended for faster processing (optional)
- Sufficient disk space for video processing (at least 10GB free)

### Setup Instructions

1. Clone or download the application repository:
   ```
   git clone https://github.com/yourusername/mission-impossible-supercut.git
   cd mission-impossible-supercut
   ```

2. Run the setup script to install dependencies:
   ```
   python setup.py
   ```

   This script will:
   - Check Python version compatibility
   - Install required Python packages
   - Verify FFmpeg installation
   - Create necessary directories

3. Verify installation:
   ```
   python src/main.py --help
   ```

## Application Components

The application consists of several key components:

- **Video Input Module**: Handles video file validation and metadata extraction
- **Scene Detection Module**: Identifies scene transitions using PySceneDetect
- **Action Recognition Module**: Classifies scenes by action type using deep learning
- **Sequence Selection Module**: Selects the best action sequences based on criteria
- **Video Editing Module**: Cuts and concatenates selected sequences
- **User Interface**: Both command-line and graphical interfaces

## Command-Line Interface

The application can be run from the command line using the `main.py` script.

### Basic Usage

```
python src/main.py --input path/to/movie1.mp4 path/to/movie2.mp4 --output-dir ./output
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--input`, `-i` | Path(s) to input video file(s) | (Required) |
| `--output-dir`, `-o` | Directory to save output files | ./output |
| `--detector` | Scene detector type (content, threshold, adaptive) | content |
| `--threshold` | Threshold for scene detection | 27.0 |
| `--min-scene-len` | Minimum scene length in frames | 15 |
| `--save-images` | Save images from each scene | False |
| `--target-duration` | Target duration of supercut in seconds | 300.0 |
| `--min-confidence` | Minimum confidence score for action classification | 0.3 |
| `--min-duration` | Minimum scene duration in seconds | 3.0 |
| `--max-duration` | Maximum scene duration in seconds | 60.0 |
| `--no-diversity` | Disable action type diversity | False |
| `--no-transitions` | Disable transitions between clips | False |
| `--no-audio-norm` | Disable audio normalization | False |
| `--no-titles` | Disable title overlays | False |

### Example Commands

Process a single movie with default settings:
```
python src/main.py --input samples/mission_impossible_1.mp4 --output-dir ./output
```

Process multiple movies with custom settings:
```
python src/main.py --input samples/mission_impossible_1.mp4 samples/mission_impossible_2.mp4 --output-dir ./output --detector content --threshold 30.0 --target-duration 600.0 --min-confidence 0.5
```

## Graphical User Interface

The application also provides a graphical user interface for easier interaction.

### Starting the GUI

```
python src/gui.py
```

### GUI Features

The GUI is organized into three main tabs:

1. **Input Videos Tab**
   - Add/remove video files
   - Set output directory

2. **Settings Tab**
   - Scene Detection Settings
     - Detector type
     - Threshold
     - Minimum scene length
   - Supercut Settings
     - Target duration
     - Minimum confidence
     - Scene duration limits
     - Action diversity
     - Transitions
     - Audio normalization
     - Title overlays

3. **Preview & Export Tab**
   - Process videos button
   - Preview of created supercut
   - Export options

### GUI Workflow

1. Add Mission Impossible movie files in the Input Videos tab
2. Adjust settings in the Settings tab
3. Click "Process Videos and Create Supercut" in the Preview & Export tab
4. Wait for processing to complete
5. Preview the result and click "Open Supercut" to view the final video

## Configuration Options

### Scene Detection

- **Content Detector**: Detects scene changes based on content differences between frames
  - Best for most scenes with clear transitions
  - Threshold controls sensitivity (higher = fewer scenes detected)

- **Threshold Detector**: Detects scene changes based on pixel intensity
  - Useful for fade transitions
  - Lower threshold values detect more subtle transitions

- **Adaptive Detector**: Automatically adjusts to video content
  - Good for videos with varying lighting conditions
  - May detect more false positives

### Action Recognition

The application uses deep learning to identify action sequences:

- **Action Types**: chase, fight, explosion, vehicle, stunts, shooting
- **Confidence Score**: Higher values indicate more certain action classification
- **Minimum Confidence**: Adjust to filter out low-confidence scenes

### Sequence Selection

- **Target Duration**: Desired length of the final supercut
- **Duration Limits**: Minimum and maximum scene duration
- **Action Diversity**: Ensures variety of action types in the supercut

### Video Editing

- **Transitions**: Add fade transitions between clips
- **Audio Normalization**: Balance audio levels across clips
- **Title Overlays**: Add movie title and action type as text overlays

## Workflow Examples

### Basic Workflow

1. Prepare your Mission Impossible movie files
2. Run the application with default settings
3. Review the generated supercut

### Advanced Workflow

1. Prepare your Mission Impossible movie files
2. Adjust scene detection parameters based on movie style
3. Set higher confidence threshold for action recognition
4. Customize sequence selection for desired action types
5. Add custom transitions and title overlays
6. Generate and review the supercut

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| FFmpeg not found | Install FFmpeg and ensure it's in your PATH |
| Out of memory error | Reduce video resolution or process smaller segments |
| Scene detection too sensitive | Increase threshold value |
| No action scenes detected | Lower minimum confidence threshold |
| Video quality issues | Use higher resolution input files |

### Error Messages

- **"Failed to add video"**: Check if the file exists and is a supported format
- **"No scenes detected"**: Adjust scene detection threshold
- **"No scenes selected for supercut"**: Lower minimum confidence or adjust duration limits
- **"Failed to create supercut"**: Check disk space and file permissions

## Legal Considerations

- This application is designed for personal use only
- The Mission Impossible films are copyrighted by Paramount Pictures
- Creating supercuts for personal use may fall under fair use, but distribution could infringe copyright
- Always respect copyright laws and only process content you legally own
- The application developers are not responsible for any copyright infringement by users

---

## Support and Contact

For support, bug reports, or feature requests, please open an issue on the GitHub repository or contact the development team at support@example.com.

---

*This application was created as a demonstration project and is not affiliated with or endorsed by Paramount Pictures or the Mission Impossible franchise.*
