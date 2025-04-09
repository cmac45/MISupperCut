"""
Action Recognition Module for Mission Impossible Supercut Application.

This module identifies and classifies action sequences using deep learning:
- Pre-trained action recognition models
- Classification of scenes by action type (chase, fight, explosion, etc.)
- Confidence scoring for action intensity
- Temporal action localization within scenes
"""

import os
import cv2
import numpy as np
import torch
import logging
from torchvision import transforms
from torchvision.models.video import r3d_18
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('action_recognition')

# Action categories for Kinetics-400 dataset (simplified for our use case)
ACTION_CATEGORIES = {
    'chase': ['running', 'jogging', 'sprinting', 'chasing'],
    'fight': ['punching', 'kicking', 'martial_arts', 'boxing', 'wrestling'],
    'explosion': ['explosion', 'fire', 'smoke'],
    'vehicle': ['driving_car', 'motorcycle', 'car_racing', 'helicopter'],
    'stunts': ['parkour', 'climbing', 'jumping', 'falling'],
    'shooting': ['shooting', 'aiming', 'gun', 'rifle']
}

class ActionRecognition:
    """Class for recognizing action sequences in videos."""
    
    def __init__(self, model_path=None, device=None):
        """
        Initialize the ActionRecognition class.
        
        Args:
            model_path (str): Path to a pre-trained model (if None, uses torchvision model)
            device (str): Device to run inference on ('cuda' or 'cpu')
        """
        # Set device (use CUDA if available)
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
            
        logger.info(f"Using device: {self.device}")
        
        # Load model
        try:
            if model_path and os.path.exists(model_path):
                logger.info(f"Loading custom model from {model_path}")
                self.model = torch.load(model_path, map_location=self.device)
            else:
                logger.info("Loading pre-trained R3D_18 model")
                self.model = r3d_18(pretrained=True)
                
            self.model = self.model.to(self.device)
            self.model.eval()  # Set to evaluation mode
            
            # Define preprocessing transforms
            self.transform = transforms.Compose([
                transforms.Resize((112, 112)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.43216, 0.394666, 0.37645],
                                     std=[0.22803, 0.22145, 0.216989])
            ])
            
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def extract_frames(self, video_path, start_time, end_time, num_frames=16):
        """
        Extract frames from a video segment.
        
        Args:
            video_path (str): Path to the video file
            start_time (float): Start time in seconds
            end_time (float): End time in seconds
            num_frames (int): Number of frames to extract
            
        Returns:
            list: List of extracted frames as PIL Images
        """
        if not os.path.exists(video_path):
            logger.error(f"Video file does not exist: {video_path}")
            return []
            
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"Could not open video file: {video_path}")
                return []
                
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Calculate frame indices to extract
            start_frame = int(start_time * fps)
            end_frame = int(end_time * fps)
            
            if end_frame <= start_frame or start_frame >= total_frames:
                logger.error(f"Invalid time range: {start_time}s - {end_time}s")
                cap.release()
                return []
                
            # Adjust end_frame if it exceeds total frames
            end_frame = min(end_frame, total_frames - 1)
            
            # Calculate frame indices to sample
            if end_frame - start_frame <= num_frames:
                frame_indices = list(range(start_frame, end_frame + 1))
            else:
                frame_indices = np.linspace(start_frame, end_frame, num_frames, dtype=int)
            
            # Extract frames
            frames = []
            for idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if ret:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # Convert to PIL Image
                    pil_image = Image.fromarray(frame_rgb)
                    frames.append(pil_image)
                else:
                    logger.warning(f"Failed to read frame at index {idx}")
            
            cap.release()
            logger.info(f"Extracted {len(frames)} frames from {video_path} ({start_time}s - {end_time}s)")
            return frames
            
        except Exception as e:
            logger.error(f"Error extracting frames from {video_path}: {str(e)}")
            return []
    
    def preprocess_frames(self, frames):
        """
        Preprocess frames for model input.
        
        Args:
            frames (list): List of PIL Image frames
            
        Returns:
            torch.Tensor: Preprocessed frames tensor
        """
        if not frames:
            return None
            
        # Apply transforms to each frame
        transformed_frames = [self.transform(frame) for frame in frames]
        
        # Stack frames into a 4D tensor [C, T, H, W]
        frames_tensor = torch.stack(transformed_frames, dim=1)
        
        # Add batch dimension [B, C, T, H, W]
        frames_tensor = frames_tensor.unsqueeze(0)
        
        return frames_tensor.to(self.device)
    
    def classify_action(self, video_path, start_time, end_time):
        """
        Classify the action in a video segment.
        
        Args:
            video_path (str): Path to the video file
            start_time (float): Start time in seconds
            end_time (float): End time in seconds
            
        Returns:
            dict: Classification results with action type and confidence score
        """
        # Extract frames from the video segment
        frames = self.extract_frames(video_path, start_time, end_time)
        if not frames:
            return {'action_type': 'unknown', 'confidence': 0.0, 'is_action': False}
            
        # Preprocess frames
        input_tensor = self.preprocess_frames(frames)
        if input_tensor is None:
            return {'action_type': 'unknown', 'confidence': 0.0, 'is_action': False}
            
        # Perform inference
        with torch.no_grad():
            outputs = self.model(input_tensor)
            
        # Get top predictions
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        top_prob, top_class = torch.topk(probabilities, k=5)
        
        # Convert to numpy for easier handling
        top_prob = top_prob.cpu().numpy().flatten()
        top_class = top_class.cpu().numpy().flatten()
        
        # Map class indices to action categories
        action_scores = {category: 0.0 for category in ACTION_CATEGORIES.keys()}
        
        # Simple mapping based on class index (would be replaced with actual class names)
        for i, (class_idx, prob) in enumerate(zip(top_class, top_prob)):
            # This is a simplified mapping - in a real implementation, 
            # we would map the class index to the actual class name
            class_name = f"class_{class_idx}"  # Placeholder
            
            # Check which action category this class belongs to
            for category, keywords in ACTION_CATEGORIES.items():
                if any(keyword in class_name for keyword in keywords):
                    action_scores[category] += prob
                    break
        
        # Get the highest scoring action category
        top_action = max(action_scores.items(), key=lambda x: x[1])
        action_type, confidence = top_action
        
        # Determine if this is an action scene (confidence threshold)
        is_action = confidence > 0.3
        
        result = {
            'action_type': action_type,
            'confidence': float(confidence),
            'is_action': is_action,
            'all_scores': action_scores
        }
        
        logger.info(f"Classified segment ({start_time:.2f}s - {end_time:.2f}s) as {action_type} " +
                   f"with confidence {confidence:.2f}")
        
        return result
    
    def analyze_scene(self, video_path, scene_info):
        """
        Analyze a scene to determine if it contains action.
        
        Args:
            video_path (str): Path to the video file
            scene_info (dict): Scene information dictionary
            
        Returns:
            dict: Updated scene information with action classification
        """
        start_time = scene_info['start_time']
        end_time = scene_info['end_time']
        
        # For longer scenes, analyze multiple segments
        if scene_info['duration'] > 10.0:
            # Divide into segments
            segment_duration = 5.0
            segments = []
            
            current_time = start_time
            while current_time < end_time - 1.0:  # Ensure at least 1 second segment
                segment_end = min(current_time + segment_duration, end_time)
                segments.append((current_time, segment_end))
                current_time = segment_end
            
            # Analyze each segment
            segment_results = []
            for seg_start, seg_end in segments:
                result = self.classify_action(video_path, seg_start, seg_end)
                segment_results.append(result)
            
            # Aggregate results (take the segment with highest action confidence)
            best_segment = max(segment_results, key=lambda x: x['confidence'])
            
            # Update scene info
            scene_info.update({
                'action_type': best_segment['action_type'],
                'action_confidence': best_segment['confidence'],
                'is_action_scene': best_segment['is_action'],
                'segment_results': segment_results
            })
            
        else:
            # For shorter scenes, analyze the whole scene
            result = self.classify_action(video_path, start_time, end_time)
            
            # Update scene info
            scene_info.update({
                'action_type': result['action_type'],
                'action_confidence': result['confidence'],
                'is_action_scene': result['is_action'],
                'all_scores': result['all_scores']
            })
        
        return scene_info


# Example usage
if __name__ == "__main__":
    action_recognizer = ActionRecognition()
    
    # Example: Analyze a scene
    scene_info = {
        'scene_number': 1,
        'start_time': 10.5,
        'end_time': 25.8,
        'duration': 15.3
    }
    
    result = action_recognizer.analyze_scene(
        video_path="path/to/mission_impossible_1.mp4",
        scene_info=scene_info
    )
    
    print(f"Scene {result['scene_number']} ({result['start_time']:.2f}s - {result['end_time']:.2f}s):")
    print(f"  Action type: {result['action_type']}")
    print(f"  Confidence: {result['action_confidence']:.2f}")
    print(f"  Is action scene: {result['is_action_scene']}")
