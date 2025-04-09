# README.md - Mission Impossible Supercut Application

A Python application that analyzes Mission Impossible movies, identifies action sequences, and compiles them into a single supercut video.

## Features

- **Automatic Scene Detection**: Identifies scene transitions using content-aware algorithms
- **Action Recognition**: Uses deep learning to classify action sequences
- **Intelligent Selection**: Selects the best action scenes based on intensity and diversity
- **Professional Editing**: Creates seamless transitions between clips with audio normalization
- **User-Friendly Interface**: Both command-line and graphical interfaces available

## Project Structure

```
mission_impossible_project/
├── src/                        # Source code
│   ├── video_input.py          # Video file handling and validation
│   ├── scene_detection.py      # Scene transition detection
│   ├── action_recognition.py   # Action sequence classification
│   ├── sequence_selection.py   # Action scene selection
│   ├── video_editing.py        # Video cutting and concatenation
│   ├── main.py                 # Command-line interface
│   └── gui.py                  # Graphical user interface
├── samples/                    # Sample video files for testing
├── output/                     # Output directory for supercuts
├── setup.py                    # Installation and setup script
├── user_guide.md               # Comprehensive user documentation
├── application_architecture.md # Technical architecture documentation
├── video_processing_technologies.md # Research on video technologies
└── mission_impossible_movies_info.md # Information about the movies
```

## Installation

1. Ensure you have Python 3.9+ and FFmpeg installed
2. Clone this repository
3. Run the setup script:
   ```
   python setup.py
   ```

## Quick Start

### Command-Line Interface

```bash
# Process videos with default settings
python src/main.py --input path/to/movie1.mp4 path/to/movie2.mp4 --output-dir ./output

# Process with custom settings
python src/main.py --input path/to/movie1.mp4 --detector content --threshold 30.0 --target-duration 600.0
```

### Graphical Interface

```bash
python src/gui.py
```

## Documentation

For detailed instructions, see the [User Guide](user_guide.md).

## Technical Details

This application uses:
- **MoviePy**: For video editing and concatenation
- **PySceneDetect**: For automatic scene detection
- **PyTorch**: For action recognition using deep learning
- **Tkinter**: For the graphical user interface

## Legal Considerations

This application is designed for personal use only. The Mission Impossible films are copyrighted by Paramount Pictures. Creating supercuts for personal use may fall under fair use, but distribution could infringe copyright. Always respect copyright laws and only process content you legally own.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
