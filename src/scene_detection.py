"""
Scene Detection Module for Mission Impossible Supercut Application.

This module identifies scene transitions and segments videos using PySceneDetect:
- Content-aware scene detection
- Threshold-based detection for fade transitions
- Adaptive detection for handling fast camera movement
- Scene boundary identification and timestamp extraction
"""

import os
import logging
from scenedetect import VideoManager, SceneManager, StatsManager
from scenedetect.detectors import ContentDetector, ThresholdDetector, AdaptiveDetector
from scenedetect.scene_manager import save_images, write_scene_list_html

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('scene_detection')

class SceneDetection:
    """Class for detecting scenes in videos."""
    
    def __init__(self, output_dir="./output"):
        """
        Initialize the SceneDetection class.
        
        Args:
            output_dir (str): Directory to save output files
        """
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
    def detect_scenes(self, video_path, detector_type="content", threshold=27.0, 
                      min_scene_len=15, save_images_flag=False, num_images=3):
        """
        Detect scenes in a video file.
        
        Args:
            video_path (str): Path to the video file
            detector_type (str): Type of detector to use ('content', 'threshold', or 'adaptive')
            threshold (float): Threshold value for content detector
            min_scene_len (int): Minimum scene length in frames
            save_images_flag (bool): Whether to save images from each scene
            num_images (int): Number of images to save per scene
            
        Returns:
            list: List of scene boundaries (tuples of start and end frames)
        """
        if not os.path.exists(video_path):
            logger.error(f"Video file does not exist: {video_path}")
            return []
            
        try:
            # Create a VideoManager and SceneManager
            video_manager = VideoManager([video_path])
            stats_manager = StatsManager()
            scene_manager = SceneManager(stats_manager)
            
            # Add the appropriate detector
            if detector_type == "content":
                scene_manager.add_detector(ContentDetector(threshold=threshold, min_scene_len=min_scene_len))
                logger.info(f"Using ContentDetector with threshold={threshold}")
            elif detector_type == "threshold":
                scene_manager.add_detector(ThresholdDetector(threshold=threshold, min_scene_len=min_scene_len))
                logger.info(f"Using ThresholdDetector with threshold={threshold}")
            elif detector_type == "adaptive":
                scene_manager.add_detector(AdaptiveDetector(min_scene_len=min_scene_len))
                logger.info("Using AdaptiveDetector")
            else:
                logger.error(f"Unknown detector type: {detector_type}")
                return []
                
            # Start video manager and perform scene detection
            video_manager.start()
            
            # Detect scenes
            logger.info(f"Detecting scenes in {video_path}...")
            scene_manager.detect_scenes(frame_source=video_manager)
            
            # Get the scene list
            scene_list = scene_manager.get_scene_list()
            logger.info(f"Detected {len(scene_list)} scenes")
            
            # Save scene list to file
            base_filename = os.path.splitext(os.path.basename(video_path))[0]
            scene_list_filename = os.path.join(self.output_dir, f"{base_filename}_scenes.csv")
            with open(scene_list_filename, 'w') as f:
                f.write("Scene Number,Start Frame,End Frame,Start Time (seconds),End Time (seconds)\n")
                for i, scene in enumerate(scene_list):
                    start_frame = scene[0].get_frames()
                    end_frame = scene[1].get_frames()
                    start_time = scene[0].get_seconds()
                    end_time = scene[1].get_seconds()
                    f.write(f"{i+1},{start_frame},{end_frame},{start_time:.2f},{end_time:.2f}\n")
            
            logger.info(f"Scene list saved to {scene_list_filename}")
            
            # Optionally save images from each scene
            if save_images_flag:
                image_dir = os.path.join(self.output_dir, f"{base_filename}_images")
                if not os.path.exists(image_dir):
                    os.makedirs(image_dir)
                    
                save_images(
                    scene_list=scene_list,
                    video=video_manager.get_video(),
                    num_images=num_images,
                    image_name_template=os.path.join(image_dir, 'scene-$SCENE_NUMBER-$IMAGE_NUMBER'),
                    show_progress=True
                )
                logger.info(f"Scene images saved to {image_dir}")
                
            # Generate HTML report
            html_filename = os.path.join(self.output_dir, f"{base_filename}_scenes.html")
            write_scene_list_html(html_filename, scene_list)
            logger.info(f"HTML scene list saved to {html_filename}")
            
            # Return the scene list
            return scene_list
            
        except Exception as e:
            logger.error(f"Error detecting scenes in {video_path}: {str(e)}")
            return []
            
    def get_scene_info(self, scene_list):
        """
        Get detailed information about detected scenes.
        
        Args:
            scene_list (list): List of scene boundaries
            
        Returns:
            list: List of dictionaries with scene information
        """
        scene_info = []
        for i, scene in enumerate(scene_list):
            start_frame = scene[0].get_frames()
            end_frame = scene[1].get_frames()
            start_time = scene[0].get_seconds()
            end_time = scene[1].get_seconds()
            duration = end_time - start_time
            
            scene_info.append({
                'scene_number': i + 1,
                'start_frame': start_frame,
                'end_frame': end_frame,
                'start_time': start_time,
                'end_time': end_time,
                'duration': duration
            })
            
        return scene_info
        
    def filter_scenes_by_duration(self, scene_info, min_duration=1.0, max_duration=60.0):
        """
        Filter scenes based on duration.
        
        Args:
            scene_info (list): List of scene information dictionaries
            min_duration (float): Minimum scene duration in seconds
            max_duration (float): Maximum scene duration in seconds
            
        Returns:
            list: Filtered list of scene information dictionaries
        """
        filtered_scenes = [
            scene for scene in scene_info 
            if min_duration <= scene['duration'] <= max_duration
        ]
        
        logger.info(f"Filtered {len(scene_info)} scenes to {len(filtered_scenes)} " +
                   f"(duration between {min_duration}s and {max_duration}s)")
        
        return filtered_scenes


# Example usage
if __name__ == "__main__":
    scene_detector = SceneDetection(output_dir="./output")
    
    # Example: Detect scenes in a video
    scene_list = scene_detector.detect_scenes(
        video_path="path/to/mission_impossible_1.mp4",
        detector_type="content",
        threshold=27.0,
        save_images_flag=True
    )
    
    # Get and filter scene information
    scene_info = scene_detector.get_scene_info(scene_list)
    filtered_scenes = scene_detector.filter_scenes_by_duration(
        scene_info, min_duration=3.0, max_duration=30.0
    )
    
    # Print filtered scenes
    for scene in filtered_scenes:
        print(f"Scene {scene['scene_number']}: {scene['start_time']:.2f}s - {scene['end_time']:.2f}s " +
              f"(duration: {scene['duration']:.2f}s)")
