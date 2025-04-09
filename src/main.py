"""
Main Application Module for Mission Impossible Supercut Application.

This module integrates all components and provides a command-line interface:
- Video input handling
- Scene detection
- Action recognition
- Sequence selection
- Video editing
"""

import os
import argparse
import logging
import json
from datetime import datetime

# Import application modules
from video_input import VideoInput
from scene_detection import SceneDetection
from action_recognition import ActionRecognition
from sequence_selection import SequenceSelection
from video_editing import VideoEditing

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('mission_impossible_supercut')

class MissionImpossibleSupercut:
    """Main application class for Mission Impossible Supercut."""
    
    def __init__(self, output_dir="./output"):
        """
        Initialize the application.
        
        Args:
            output_dir (str): Directory to save output files
        """
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Initialize components
        self.video_input = VideoInput()
        self.scene_detection = SceneDetection(output_dir=output_dir)
        self.action_recognition = ActionRecognition()
        self.sequence_selection = SequenceSelection()
        self.video_editing = VideoEditing(output_dir=output_dir)
        
        logger.info("Mission Impossible Supercut application initialized")
    
    def process_video(self, video_path, detector_type="content", threshold=27.0, 
                     min_scene_len=15, save_images=False):
        """
        Process a single video file.
        
        Args:
            video_path (str): Path to the video file
            detector_type (str): Type of scene detector to use
            threshold (float): Threshold value for scene detection
            min_scene_len (int): Minimum scene length in frames
            save_images (bool): Whether to save scene images
            
        Returns:
            list: List of processed scenes with action recognition data
        """
        logger.info(f"Processing video: {video_path}")
        
        # Add video to input module
        if not self.video_input.add_video(video_path):
            logger.error(f"Failed to add video: {video_path}")
            return []
        
        # Detect scenes
        scene_list = self.scene_detection.detect_scenes(
            video_path=video_path,
            detector_type=detector_type,
            threshold=threshold,
            min_scene_len=min_scene_len,
            save_images_flag=save_images
        )
        
        if not scene_list:
            logger.warning(f"No scenes detected in {video_path}")
            return []
        
        # Get scene information
        scene_info = self.scene_detection.get_scene_info(scene_list)
        
        # Add video path to each scene
        for scene in scene_info:
            scene['video_path'] = video_path
        
        # Analyze scenes for action content
        processed_scenes = []
        for scene in scene_info:
            processed_scene = self.action_recognition.analyze_scene(video_path, scene)
            processed_scenes.append(processed_scene)
            
        # Save processed scenes to JSON
        base_filename = os.path.splitext(os.path.basename(video_path))[0]
        scenes_json_path = os.path.join(self.output_dir, f"{base_filename}_processed_scenes.json")
        with open(scenes_json_path, 'w') as f:
            json.dump(processed_scenes, f, indent=2)
            
        logger.info(f"Processed {len(processed_scenes)} scenes from {video_path}")
        logger.info(f"Saved processed scenes to {scenes_json_path}")
        
        return processed_scenes
    
    def create_supercut(self, processed_scenes, target_duration=300.0, min_confidence=0.3,
                       min_duration=3.0, max_duration=60.0, ensure_diversity=True,
                       add_transitions=True, normalize_audio=True, add_title=True):
        """
        Create a supercut from processed scenes.
        
        Args:
            processed_scenes (list): List of processed scenes with action recognition data
            target_duration (float): Target duration of the supercut in seconds
            min_confidence (float): Minimum confidence score for action classification
            min_duration (float): Minimum scene duration in seconds
            max_duration (float): Maximum scene duration in seconds
            ensure_diversity (bool): Whether to ensure diversity of action types
            add_transitions (bool): Whether to add transitions between clips
            normalize_audio (bool): Whether to normalize audio
            add_title (bool): Whether to add title overlays
            
        Returns:
            str: Path to the created supercut file
        """
        # Select sequences for the supercut
        selected_scenes = self.sequence_selection.select_sequences_for_supercut(
            scenes=processed_scenes,
            target_duration=target_duration,
            min_confidence=min_confidence,
            min_duration=min_duration,
            max_duration=max_duration,
            ensure_diversity=ensure_diversity
        )
        
        if not selected_scenes:
            logger.error("No scenes selected for supercut")
            return None
        
        # Get segments for the supercut
        segments = self.sequence_selection.get_supercut_segments(selected_scenes)
        
        # Create timestamp for output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"mission_impossible_supercut_{timestamp}.mp4"
        
        # Create the supercut
        supercut_path = self.video_editing.create_supercut(
            segments=segments,
            output_filename=output_filename,
            add_transitions=add_transitions,
            normalize_audio=normalize_audio,
            add_title=add_title
        )
        
        if supercut_path:
            logger.info(f"Supercut created successfully: {supercut_path}")
            
            # Save selected scenes to JSON
            selected_scenes_json_path = os.path.join(self.output_dir, f"selected_scenes_{timestamp}.json")
            with open(selected_scenes_json_path, 'w') as f:
                json.dump(selected_scenes, f, indent=2)
                
            logger.info(f"Saved selected scenes to {selected_scenes_json_path}")
        else:
            logger.error("Failed to create supercut")
            
        return supercut_path
    
    def process_multiple_videos(self, video_paths, **kwargs):
        """
        Process multiple videos and create a combined supercut.
        
        Args:
            video_paths (list): List of video file paths
            **kwargs: Additional arguments for scene detection and supercut creation
            
        Returns:
            str: Path to the created supercut file
        """
        all_processed_scenes = []
        
        # Process each video
        for video_path in video_paths:
            processed_scenes = self.process_video(
                video_path=video_path,
                detector_type=kwargs.get('detector_type', 'content'),
                threshold=kwargs.get('threshold', 27.0),
                min_scene_len=kwargs.get('min_scene_len', 15),
                save_images=kwargs.get('save_images', False)
            )
            all_processed_scenes.extend(processed_scenes)
        
        if not all_processed_scenes:
            logger.error("No scenes processed from any videos")
            return None
        
        # Create supercut from all processed scenes
        supercut_path = self.create_supercut(
            processed_scenes=all_processed_scenes,
            target_duration=kwargs.get('target_duration', 300.0),
            min_confidence=kwargs.get('min_confidence', 0.3),
            min_duration=kwargs.get('min_duration', 3.0),
            max_duration=kwargs.get('max_duration', 60.0),
            ensure_diversity=kwargs.get('ensure_diversity', True),
            add_transitions=kwargs.get('add_transitions', True),
            normalize_audio=kwargs.get('normalize_audio', True),
            add_title=kwargs.get('add_title', True)
        )
        
        return supercut_path


def main():
    """Main function for command-line interface."""
    parser = argparse.ArgumentParser(description='Mission Impossible Supercut Application')
    
    # Input options
    parser.add_argument('--input', '-i', nargs='+', required=True,
                      help='Path(s) to input video file(s)')
    parser.add_argument('--output-dir', '-o', default='./output',
                      help='Directory to save output files')
    
    # Scene detection options
    parser.add_argument('--detector', choices=['content', 'threshold', 'adaptive'],
                      default='content', help='Scene detector type')
    parser.add_argument('--threshold', type=float, default=27.0,
                      help='Threshold for scene detection')
    parser.add_argument('--min-scene-len', type=int, default=15,
                      help='Minimum scene length in frames')
    parser.add_argument('--save-images', action='store_true',
                      help='Save images from each scene')
    
    # Supercut options
    parser.add_argument('--target-duration', type=float, default=300.0,
                      help='Target duration of supercut in seconds')
    parser.add_argument('--min-confidence', type=float, default=0.3,
                      help='Minimum confidence score for action classification')
    parser.add_argument('--min-duration', type=float, default=3.0,
                      help='Minimum scene duration in seconds')
    parser.add_argument('--max-duration', type=float, default=60.0,
                      help='Maximum scene duration in seconds')
    parser.add_argument('--no-diversity', action='store_true',
                      help='Disable action type diversity')
    parser.add_argument('--no-transitions', action='store_true',
                      help='Disable transitions between clips')
    parser.add_argument('--no-audio-norm', action='store_true',
                      help='Disable audio normalization')
    parser.add_argument('--no-titles', action='store_true',
                      help='Disable title overlays')
    
    args = parser.parse_args()
    
    # Create application instance
    app = MissionImpossibleSupercut(output_dir=args.output_dir)
    
    # Process videos and create supercut
    supercut_path = app.process_multiple_videos(
        video_paths=args.input,
        detector_type=args.detector,
        threshold=args.threshold,
        min_scene_len=args.min_scene_len,
        save_images=args.save_images,
        target_duration=args.target_duration,
        min_confidence=args.min_confidence,
        min_duration=args.min_duration,
        max_duration=args.max_duration,
        ensure_diversity=not args.no_diversity,
        add_transitions=not args.no_transitions,
        normalize_audio=not args.no_audio_norm,
        add_title=not args.no_titles
    )
    
    if supercut_path:
        print(f"\nSupercut created successfully: {supercut_path}")
    else:
        print("\nFailed to create supercut")


if __name__ == "__main__":
    main()
