"""
Video Input Module for Mission Impossible Supercut Application.

This module handles video file input and validation, including:
- Support for various video formats (MP4, MKV, AVI)
- Video metadata extraction (resolution, duration, framerate)
- Input validation and error handling
- Support for batch processing multiple movie files
"""

import os
import cv2
from moviepy.editor import VideoFileClip
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('video_input')

# Supported video formats
SUPPORTED_FORMATS = ['.mp4', '.mkv', '.avi', '.mov']

class VideoInput:
    """Class for handling video input operations."""
    
    def __init__(self):
        """Initialize the VideoInput class."""
        self.videos = []
        
    def validate_file(self, file_path):
        """
        Validate if a file exists and has a supported format.
        
        Args:
            file_path (str): Path to the video file
            
        Returns:
            bool: True if file is valid, False otherwise
        """
        if not os.path.exists(file_path):
            logger.error(f"File does not exist: {file_path}")
            return False
            
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in SUPPORTED_FORMATS:
            logger.error(f"Unsupported file format: {ext}")
            return False
            
        return True
    
    def add_video(self, file_path):
        """
        Add a video file to the processing queue.
        
        Args:
            file_path (str): Path to the video file
            
        Returns:
            bool: True if video was added successfully, False otherwise
        """
        if not self.validate_file(file_path):
            return False
            
        try:
            # Extract video metadata using MoviePy
            with VideoFileClip(file_path) as clip:
                video_info = {
                    'path': file_path,
                    'filename': os.path.basename(file_path),
                    'duration': clip.duration,
                    'fps': clip.fps,
                    'size': clip.size,
                    'audio': clip.audio is not None
                }
                
            # Additional metadata using OpenCV
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                logger.error(f"Could not open video file: {file_path}")
                return False
                
            # Get total frame count
            video_info['frame_count'] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            
            self.videos.append(video_info)
            logger.info(f"Added video: {file_path} ({video_info['duration']:.2f}s, {video_info['size'][0]}x{video_info['size'][1]})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding video {file_path}: {str(e)}")
            return False
    
    def add_videos_from_directory(self, directory_path):
        """
        Add all supported video files from a directory.
        
        Args:
            directory_path (str): Path to the directory
            
        Returns:
            int: Number of videos added successfully
        """
        if not os.path.isdir(directory_path):
            logger.error(f"Directory does not exist: {directory_path}")
            return 0
            
        count = 0
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path) and any(filename.lower().endswith(ext) for ext in SUPPORTED_FORMATS):
                if self.add_video(file_path):
                    count += 1
                    
        logger.info(f"Added {count} videos from directory: {directory_path}")
        return count
    
    def get_videos(self):
        """
        Get the list of added videos.
        
        Returns:
            list: List of video information dictionaries
        """
        return self.videos
    
    def clear_videos(self):
        """Clear the list of added videos."""
        self.videos = []
        logger.info("Cleared all videos from the queue")


# Example usage
if __name__ == "__main__":
    video_input = VideoInput()
    
    # Example: Add a single video
    video_input.add_video("path/to/mission_impossible_1.mp4")
    
    # Example: Add all videos from a directory
    video_input.add_videos_from_directory("path/to/mission_impossible_movies")
    
    # Get and print video information
    for video in video_input.get_videos():
        print(f"Video: {video['filename']}")
        print(f"  Duration: {video['duration']:.2f} seconds")
        print(f"  Resolution: {video['size'][0]}x{video['size'][1]}")
        print(f"  FPS: {video['fps']}")
        print(f"  Frame count: {video['frame_count']}")
        print(f"  Has audio: {video['audio']}")
        print()
