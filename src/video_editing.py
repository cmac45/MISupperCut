"""
Video Editing Module for Mission Impossible Supercut Application.

This module handles cutting, processing, and concatenating selected sequences:
- Precise cutting of selected sequences
- Transition effects between clips
- Audio normalization and enhancement
- Optional text overlays (movie title, year)
- Final compilation and rendering
"""

import os
import logging
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
from moviepy.video.fx import all as vfx
from moviepy.audio.fx import all as afx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('video_editing')

class VideoEditing:
    """Class for editing and compiling video sequences."""
    
    def __init__(self, output_dir="./output"):
        """
        Initialize the VideoEditing class.
        
        Args:
            output_dir (str): Directory to save output files
        """
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def extract_clip(self, video_path, start_time, end_time, resize=None):
        """
        Extract a clip from a video file.
        
        Args:
            video_path (str): Path to the video file
            start_time (float): Start time in seconds
            end_time (float): End time in seconds
            resize (tuple): Optional new size (width, height)
            
        Returns:
            VideoFileClip: Extracted video clip
        """
        try:
            # Load the video file
            video = VideoFileClip(video_path)
            
            # Extract the subclip
            clip = video.subclip(start_time, end_time)
            
            # Resize if specified
            if resize:
                clip = clip.resize(resize)
                
            logger.info(f"Extracted clip from {video_path} ({start_time:.2f}s - {end_time:.2f}s)")
            
            return clip
            
        except Exception as e:
            logger.error(f"Error extracting clip from {video_path}: {str(e)}")
            return None
    
    def add_transition(self, clip1, clip2, transition_type="fade", duration=0.5):
        """
        Add a transition effect between two clips.
        
        Args:
            clip1 (VideoFileClip): First clip
            clip2 (VideoFileClip): Second clip
            transition_type (str): Type of transition ('fade', 'crossfade', 'slide')
            duration (float): Duration of the transition in seconds
            
        Returns:
            list: List of clips with transition effect
        """
        if clip1 is None or clip2 is None:
            logger.error("Cannot add transition: one or both clips are None")
            return [c for c in [clip1, clip2] if c is not None]
            
        try:
            if transition_type == "fade":
                # Add fade out to the first clip
                clip1 = clip1.fx(vfx.fadeout, duration)
                # Add fade in to the second clip
                clip2 = clip2.fx(vfx.fadein, duration)
                return [clip1, clip2]
                
            elif transition_type == "crossfade":
                # Create a crossfade transition
                clip1 = clip1.crossfadeout(duration)
                clip2 = clip2.crossfadein(duration)
                # The clips will automatically crossfade when concatenated
                return [clip1, clip2]
                
            elif transition_type == "slide":
                # Create a slide transition (simplified version)
                clip1_duration = clip1.duration
                clip2 = clip2.set_start(clip1_duration - duration)
                # This will create an overlay effect
                return [clip1, clip2]
                
            else:
                logger.warning(f"Unknown transition type: {transition_type}, using fade")
                clip1 = clip1.fx(vfx.fadeout, duration)
                clip2 = clip2.fx(vfx.fadein, duration)
                return [clip1, clip2]
                
        except Exception as e:
            logger.error(f"Error adding {transition_type} transition: {str(e)}")
            return [clip1, clip2]
    
    def normalize_audio(self, clip, target_volume=0.8):
        """
        Normalize audio volume in a clip.
        
        Args:
            clip (VideoFileClip): Video clip
            target_volume (float): Target volume level (0.0 to 1.0)
            
        Returns:
            VideoFileClip: Clip with normalized audio
        """
        if clip is None or clip.audio is None:
            logger.warning("Cannot normalize audio: clip is None or has no audio")
            return clip
            
        try:
            # Normalize audio
            normalized_audio = clip.audio.fx(afx.audio_normalize)
            
            # Set to target volume
            normalized_audio = normalized_audio.fx(afx.volumex, target_volume)
            
            # Replace audio in clip
            clip = clip.set_audio(normalized_audio)
            
            logger.info(f"Normalized audio to volume level {target_volume}")
            
            return clip
            
        except Exception as e:
            logger.error(f"Error normalizing audio: {str(e)}")
            return clip
    
    def add_text_overlay(self, clip, text, position='bottom', fontsize=30, color='white', 
                        duration=None, font='Arial'):
        """
        Add text overlay to a clip.
        
        Args:
            clip (VideoFileClip): Video clip
            text (str): Text to overlay
            position (str or tuple): Position ('top', 'bottom', 'center' or (x,y))
            fontsize (int): Font size
            color (str): Text color
            duration (float): Duration of text (None for full clip duration)
            font (str): Font name
            
        Returns:
            CompositeVideoClip: Clip with text overlay
        """
        if clip is None:
            logger.error("Cannot add text overlay: clip is None")
            return None
            
        try:
            # Create text clip
            txt_clip = TextClip(text, fontsize=fontsize, color=color, font=font)
            
            # Set duration
            if duration is None:
                duration = clip.duration
            txt_clip = txt_clip.set_duration(duration)
            
            # Set position
            if position == 'top':
                txt_clip = txt_clip.set_position(('center', 20))
            elif position == 'bottom':
                txt_clip = txt_clip.set_position(('center', clip.h - 50))
            elif position == 'center':
                txt_clip = txt_clip.set_position('center')
            else:
                txt_clip = txt_clip.set_position(position)
            
            # Composite with original clip
            result = CompositeVideoClip([clip, txt_clip])
            
            logger.info(f"Added text overlay: '{text}'")
            
            return result
            
        except Exception as e:
            logger.error(f"Error adding text overlay: {str(e)}")
            return clip
    
    def create_supercut(self, segments, output_filename="supercut.mp4", 
                       add_transitions=True, normalize_audio=True, 
                       add_title=True, resize=None):
        """
        Create a supercut from video segments.
        
        Args:
            segments (list): List of segment dictionaries with video_path, start_time, and end_time
            output_filename (str): Name of the output file
            add_transitions (bool): Whether to add transitions between clips
            normalize_audio (bool): Whether to normalize audio
            add_title (bool): Whether to add title overlays
            resize (tuple): Optional size to resize all clips (width, height)
            
        Returns:
            str: Path to the created supercut file
        """
        if not segments:
            logger.error("Cannot create supercut: no segments provided")
            return None
            
        try:
            # Extract clips from segments
            clips = []
            for i, segment in enumerate(segments):
                clip = self.extract_clip(
                    segment['video_path'], 
                    segment['start_time'], 
                    segment['end_time'],
                    resize
                )
                
                if clip is None:
                    logger.warning(f"Skipping segment {i+1}: failed to extract clip")
                    continue
                
                # Normalize audio if requested
                if normalize_audio and clip.audio is not None:
                    clip = self.normalize_audio(clip)
                
                # Add title overlay if requested
                if add_title:
                    # Extract movie title from filename
                    filename = os.path.basename(segment['video_path'])
                    movie_title = os.path.splitext(filename)[0]
                    
                    # Add action type as text
                    action_type = segment.get('action_type', 'action')
                    text = f"{movie_title} - {action_type.upper()}"
                    
                    clip = self.add_text_overlay(
                        clip, text, position='bottom', 
                        duration=min(3.0, clip.duration)
                    )
                
                clips.append(clip)
            
            if not clips:
                logger.error("No valid clips to concatenate")
                return None
            
            # Add transitions between clips if requested
            if add_transitions and len(clips) > 1:
                clips_with_transitions = []
                for i in range(len(clips) - 1):
                    transition_clips = self.add_transition(clips[i], clips[i+1], "fade", 0.5)
                    if i == 0:
                        clips_with_transitions.extend(transition_clips)
                    else:
                        clips_with_transitions.append(transition_clips[1])
                clips = clips_with_transitions
            
            # Concatenate clips
            final_clip = concatenate_videoclips(clips, method="compose")
            
            # Add main title at the beginning
            final_clip = self.add_text_overlay(
                final_clip, 
                "MISSION IMPOSSIBLE: ACTION SUPERCUT", 
                position='center', 
                fontsize=50, 
                duration=3.0
            )
            
            # Write output file
            output_path = os.path.join(self.output_dir, output_filename)
            final_clip.write_videofile(
                output_path, 
                codec='libx264', 
                audio_codec='aac', 
                temp_audiofile='temp-audio.m4a', 
                remove_temp=True,
                threads=4
            )
            
            logger.info(f"Created supercut with {len(clips)} clips: {output_path}")
            
            # Close clips to free resources
            for clip in clips:
                clip.close()
            final_clip.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating supercut: {str(e)}")
            return None


# Example usage
if __name__ == "__main__":
    video_editor = VideoEditing(output_dir="./output")
    
    # Example: Create a supercut from sample segments
    sample_segments = [
        {
            'video_path': 'path/to/mission_impossible_1.mp4',
            'start_time': 10.5, 'end_time': 25.8,
            'action_type': 'chase', 'action_confidence': 0.85
        },
        {
            'video_path': 'path/to/mission_impossible_2.mp4',
            'start_time': 45.2, 'end_time': 65.7,
            'action_type': 'fight', 'action_confidence': 0.92
        },
        # Add more sample segments...
    ]
    
    supercut_path = video_editor.create_supercut(
        segments=sample_segments,
        output_filename="mission_impossible_supercut.mp4",
        add_transitions=True,
        normalize_audio=True,
        add_title=True
    )
    
    if supercut_path:
        print(f"Supercut created successfully: {supercut_path}")
    else:
        print("Failed to create supercut")
