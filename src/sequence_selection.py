"""
Sequence Selection Module for Mission Impossible Supercut Application.

This module selects the best action sequences for the supercut:
- Filtering based on action intensity scores
- Duration-based selection criteria
- Diversity of action types
- User-defined selection parameters
"""

import logging
import random
from collections import Counter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('sequence_selection')

class SequenceSelection:
    """Class for selecting action sequences for the supercut."""
    
    def __init__(self):
        """Initialize the SequenceSelection class."""
        pass
    
    def filter_action_scenes(self, scenes, min_confidence=0.3, min_duration=3.0, max_duration=60.0):
        """
        Filter scenes to keep only action scenes that meet criteria.
        
        Args:
            scenes (list): List of scene information dictionaries with action recognition data
            min_confidence (float): Minimum confidence score for action classification
            min_duration (float): Minimum scene duration in seconds
            max_duration (float): Maximum scene duration in seconds
            
        Returns:
            list: Filtered list of action scenes
        """
        filtered_scenes = [
            scene for scene in scenes 
            if scene.get('is_action_scene', False) and 
               scene.get('action_confidence', 0.0) >= min_confidence and
               min_duration <= scene.get('duration', 0.0) <= max_duration
        ]
        
        logger.info(f"Filtered {len(scenes)} scenes to {len(filtered_scenes)} action scenes " +
                   f"(min confidence: {min_confidence}, duration: {min_duration}s-{max_duration}s)")
        
        return filtered_scenes
    
    def rank_scenes_by_action_intensity(self, scenes):
        """
        Rank scenes by action intensity (confidence score).
        
        Args:
            scenes (list): List of scene information dictionaries
            
        Returns:
            list: List of scenes sorted by action confidence (highest first)
        """
        ranked_scenes = sorted(scenes, key=lambda x: x.get('action_confidence', 0.0), reverse=True)
        
        logger.info(f"Ranked {len(scenes)} scenes by action intensity")
        
        return ranked_scenes
    
    def ensure_action_diversity(self, scenes, max_per_type=None, min_per_type=1):
        """
        Ensure diversity of action types in the selected scenes.
        
        Args:
            scenes (list): List of scene information dictionaries
            max_per_type (int): Maximum number of scenes per action type (None for no limit)
            min_per_type (int): Minimum number of scenes per action type
            
        Returns:
            list: List of scenes with balanced action types
        """
        # Count scenes by action type
        action_types = [scene.get('action_type', 'unknown') for scene in scenes]
        type_counter = Counter(action_types)
        
        logger.info(f"Action type distribution: {dict(type_counter)}")
        
        # If max_per_type is not specified, calculate based on average
        if max_per_type is None:
            if len(type_counter) > 0:
                avg_per_type = len(scenes) / len(type_counter)
                max_per_type = max(int(avg_per_type * 1.5), min_per_type + 1)
                logger.info(f"Setting max_per_type to {max_per_type} (based on average)")
            else:
                max_per_type = len(scenes)  # No limit if no action types
        
        # Group scenes by action type
        scenes_by_type = {}
        for scene in scenes:
            action_type = scene.get('action_type', 'unknown')
            if action_type not in scenes_by_type:
                scenes_by_type[action_type] = []
            scenes_by_type[action_type].append(scene)
        
        # Select scenes with balanced distribution
        balanced_scenes = []
        
        # First, ensure minimum number of scenes per type
        for action_type, type_scenes in scenes_by_type.items():
            # Sort by confidence within each type
            type_scenes = sorted(type_scenes, key=lambda x: x.get('action_confidence', 0.0), reverse=True)
            # Add minimum number of scenes
            balanced_scenes.extend(type_scenes[:min_per_type])
            # Keep remaining scenes for later selection
            scenes_by_type[action_type] = type_scenes[min_per_type:]
        
        # Then, add remaining scenes up to max_per_type, prioritizing by confidence
        remaining_scenes = []
        for action_type, type_scenes in scenes_by_type.items():
            # Calculate how many more scenes we can add for this type
            can_add = max_per_type - min_per_type
            if can_add > 0:
                # Add scenes up to the maximum
                to_add = type_scenes[:can_add]
                remaining_scenes.extend(to_add)
        
        # Sort remaining scenes by confidence and add them
        remaining_scenes = sorted(remaining_scenes, key=lambda x: x.get('action_confidence', 0.0), reverse=True)
        balanced_scenes.extend(remaining_scenes)
        
        logger.info(f"Selected {len(balanced_scenes)} scenes with balanced action types")
        
        return balanced_scenes
    
    def select_sequences_for_supercut(self, scenes, target_duration=300.0, 
                                     min_confidence=0.3, min_duration=3.0, max_duration=60.0,
                                     ensure_diversity=True, max_per_type=None):
        """
        Select sequences for the supercut based on multiple criteria.
        
        Args:
            scenes (list): List of scene information dictionaries
            target_duration (float): Target duration of the supercut in seconds
            min_confidence (float): Minimum confidence score for action classification
            min_duration (float): Minimum scene duration in seconds
            max_duration (float): Maximum scene duration in seconds
            ensure_diversity (bool): Whether to ensure diversity of action types
            max_per_type (int): Maximum number of scenes per action type
            
        Returns:
            list: Selected scenes for the supercut
        """
        # Filter scenes by action confidence and duration
        filtered_scenes = self.filter_action_scenes(
            scenes, min_confidence, min_duration, max_duration
        )
        
        if not filtered_scenes:
            logger.warning("No scenes match the filtering criteria")
            return []
        
        # Rank scenes by action intensity
        ranked_scenes = self.rank_scenes_by_action_intensity(filtered_scenes)
        
        # Ensure diversity if requested
        if ensure_diversity:
            selected_scenes = self.ensure_action_diversity(ranked_scenes, max_per_type)
        else:
            selected_scenes = ranked_scenes
        
        # Adjust selection to meet target duration
        final_selection = []
        current_duration = 0.0
        
        for scene in selected_scenes:
            scene_duration = scene.get('duration', 0.0)
            
            # If adding this scene would exceed target duration by a lot, skip it
            if current_duration + scene_duration > target_duration * 1.2:
                continue
                
            final_selection.append(scene)
            current_duration += scene_duration
            
            # If we've reached the target duration, stop adding scenes
            if current_duration >= target_duration:
                break
        
        logger.info(f"Selected {len(final_selection)} scenes for supercut " +
                   f"(total duration: {current_duration:.2f}s, target: {target_duration:.2f}s)")
        
        return final_selection
    
    def get_supercut_segments(self, selected_scenes):
        """
        Get video segments for the supercut.
        
        Args:
            selected_scenes (list): List of selected scene information dictionaries
            
        Returns:
            list: List of segment dictionaries with video_path, start_time, and end_time
        """
        segments = []
        
        for scene in selected_scenes:
            segment = {
                'video_path': scene.get('video_path', ''),
                'start_time': scene.get('start_time', 0.0),
                'end_time': scene.get('end_time', 0.0),
                'action_type': scene.get('action_type', 'unknown'),
                'action_confidence': scene.get('action_confidence', 0.0)
            }
            segments.append(segment)
        
        return segments


# Example usage
if __name__ == "__main__":
    sequence_selector = SequenceSelection()
    
    # Example: Create some sample scenes with action recognition data
    sample_scenes = [
        {
            'scene_number': 1, 'video_path': 'mission_impossible_1.mp4',
            'start_time': 10.5, 'end_time': 25.8, 'duration': 15.3,
            'action_type': 'chase', 'action_confidence': 0.85, 'is_action_scene': True
        },
        {
            'scene_number': 2, 'video_path': 'mission_impossible_1.mp4',
            'start_time': 45.2, 'end_time': 65.7, 'duration': 20.5,
            'action_type': 'fight', 'action_confidence': 0.92, 'is_action_scene': True
        },
        # Add more sample scenes...
    ]
    
    # Select sequences for supercut
    selected_scenes = sequence_selector.select_sequences_for_supercut(
        scenes=sample_scenes,
        target_duration=120.0,
        min_confidence=0.5,
        ensure_diversity=True
    )
    
    # Get segments for the supercut
    segments = sequence_selector.get_supercut_segments(selected_scenes)
    
    # Print selected segments
    for i, segment in enumerate(segments):
        print(f"Segment {i+1}: {segment['video_path']}")
        print(f"  Time: {segment['start_time']:.2f}s - {segment['end_time']:.2f}s")
        print(f"  Action: {segment['action_type']} (confidence: {segment['action_confidence']:.2f})")
        print()
