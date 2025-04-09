"""
GUI Interface for Mission Impossible Supercut Application.

This module provides a graphical user interface for the application:
- Video file selection
- Processing parameter configuration
- Progress visualization
- Preview capabilities
- Export options
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import json

# Import application modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from main import MissionImpossibleSupercut

class SupercutGUI:
    """GUI class for Mission Impossible Supercut application."""
    
    def __init__(self, root):
        """
        Initialize the GUI.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Mission Impossible Supercut Creator")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Set application icon if available
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # Initialize variables
        self.video_paths = []
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        self.processing_thread = None
        self.supercut_path = None
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Initialize application
        self.app = MissionImpossibleSupercut(output_dir=self.output_dir)
        
        # Create GUI elements
        self.create_widgets()
        
        # Center window
        self.center_window()
    
    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Create GUI widgets."""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        input_tab = ttk.Frame(notebook)
        settings_tab = ttk.Frame(notebook)
        preview_tab = ttk.Frame(notebook)
        
        notebook.add(input_tab, text="Input Videos")
        notebook.add(settings_tab, text="Settings")
        notebook.add(preview_tab, text="Preview & Export")
        
        # Create widgets for input tab
        self.create_input_tab(input_tab)
        
        # Create widgets for settings tab
        self.create_settings_tab(settings_tab)
        
        # Create widgets for preview tab
        self.create_preview_tab(preview_tab)
        
        # Create status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, anchor=tk.W)
        status_label.pack(side=tk.LEFT)
        
        # Create progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_var.set(0)
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
    
    def create_input_tab(self, parent):
        """Create widgets for the input tab."""
        # Create frame for video list
        list_frame = ttk.LabelFrame(parent, text="Selected Videos")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create scrollable listbox for videos
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.video_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, selectmode=tk.EXTENDED)
        self.video_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar.config(command=self.video_listbox.yview)
        
        # Create frame for buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Add buttons
        add_button = ttk.Button(button_frame, text="Add Videos", command=self.add_videos)
        add_button.pack(side=tk.LEFT, padx=5)
        
        remove_button = ttk.Button(button_frame, text="Remove Selected", command=self.remove_videos)
        remove_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = ttk.Button(button_frame, text="Clear All", command=self.clear_videos)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Add output directory selection
        dir_frame = ttk.Frame(parent)
        dir_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Label(dir_frame, text="Output Directory:").pack(side=tk.LEFT)
        
        self.output_dir_var = tk.StringVar()
        self.output_dir_var.set(self.output_dir)
        
        dir_entry = ttk.Entry(dir_frame, textvariable=self.output_dir_var, width=50)
        dir_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        browse_button = ttk.Button(dir_frame, text="Browse...", command=self.browse_output_dir)
        browse_button.pack(side=tk.LEFT)
    
    def create_settings_tab(self, parent):
        """Create widgets for the settings tab."""
        # Create frame for scene detection settings
        scene_frame = ttk.LabelFrame(parent, text="Scene Detection Settings")
        scene_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Detector type
        detector_frame = ttk.Frame(scene_frame)
        detector_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(detector_frame, text="Detector Type:").pack(side=tk.LEFT)
        
        self.detector_var = tk.StringVar()
        self.detector_var.set("content")
        
        detector_combo = ttk.Combobox(detector_frame, textvariable=self.detector_var, 
                                     values=["content", "threshold", "adaptive"], 
                                     state="readonly", width=15)
        detector_combo.pack(side=tk.LEFT, padx=5)
        
        # Threshold
        threshold_frame = ttk.Frame(scene_frame)
        threshold_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(threshold_frame, text="Threshold:").pack(side=tk.LEFT)
        
        self.threshold_var = tk.DoubleVar()
        self.threshold_var.set(27.0)
        
        threshold_scale = ttk.Scale(threshold_frame, from_=1.0, to=100.0, 
                                   variable=self.threshold_var, orient=tk.HORIZONTAL)
        threshold_scale.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        threshold_label = ttk.Label(threshold_frame, textvariable=self.threshold_var, width=5)
        threshold_label.pack(side=tk.LEFT)
        
        # Min scene length
        min_scene_frame = ttk.Frame(scene_frame)
        min_scene_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(min_scene_frame, text="Min Scene Length (frames):").pack(side=tk.LEFT)
        
        self.min_scene_var = tk.IntVar()
        self.min_scene_var.set(15)
        
        min_scene_spin = ttk.Spinbox(min_scene_frame, from_=1, to=100, 
                                    textvariable=self.min_scene_var, width=5)
        min_scene_spin.pack(side=tk.LEFT, padx=5)
        
        # Save images checkbox
        self.save_images_var = tk.BooleanVar()
        self.save_images_var.set(False)
        
        save_images_check = ttk.Checkbutton(scene_frame, text="Save scene images", 
                                          variable=self.save_images_var)
        save_images_check.pack(anchor=tk.W, padx=5, pady=5)
        
        # Create frame for supercut settings
        supercut_frame = ttk.LabelFrame(parent, text="Supercut Settings")
        supercut_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Target duration
        duration_frame = ttk.Frame(supercut_frame)
        duration_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(duration_frame, text="Target Duration (seconds):").pack(side=tk.LEFT)
        
        self.duration_var = tk.DoubleVar()
        self.duration_var.set(300.0)
        
        duration_spin = ttk.Spinbox(duration_frame, from_=30, to=1800, increment=30,
                                   textvariable=self.duration_var, width=5)
        duration_spin.pack(side=tk.LEFT, padx=5)
        
        # Min confidence
        confidence_frame = ttk.Frame(supercut_frame)
        confidence_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(confidence_frame, text="Min Action Confidence:").pack(side=tk.LEFT)
        
        self.confidence_var = tk.DoubleVar()
        self.confidence_var.set(0.3)
        
        confidence_scale = ttk.Scale(confidence_frame, from_=0.0, to=1.0, 
                                    variable=self.confidence_var, orient=tk.HORIZONTAL)
        confidence_scale.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        confidence_label = ttk.Label(confidence_frame, textvariable=self.confidence_var, width=5)
        confidence_label.pack(side=tk.LEFT)
        
        # Scene duration limits
        scene_duration_frame = ttk.Frame(supercut_frame)
        scene_duration_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(scene_duration_frame, text="Scene Duration Limits (seconds):").pack(side=tk.LEFT)
        
        self.min_duration_var = tk.DoubleVar()
        self.min_duration_var.set(3.0)
        
        min_duration_spin = ttk.Spinbox(scene_duration_frame, from_=1, to=30, increment=0.5,
                                       textvariable=self.min_duration_var, width=5)
        min_duration_spin.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(scene_duration_frame, text="to").pack(side=tk.LEFT)
        
        self.max_duration_var = tk.DoubleVar()
        self.max_duration_var.set(60.0)
        
        max_duration_spin = ttk.Spinbox(scene_duration_frame, from_=10, to=300, increment=5,
                                       textvariable=self.max_duration_var, width=5)
        max_duration_spin.pack(side=tk.LEFT, padx=5)
        
        # Checkboxes for options
        options_frame = ttk.Frame(supercut_frame)
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.diversity_var = tk.BooleanVar()
        self.diversity_var.set(True)
        
        diversity_check = ttk.Checkbutton(options_frame, text="Ensure action type diversity", 
                                        variable=self.diversity_var)
        diversity_check.pack(anchor=tk.W)
        
        self.transitions_var = tk.BooleanVar()
        self.transitions_var.set(True)
        
        transitions_check = ttk.Checkbutton(options_frame, text="Add transitions between clips", 
                                          variable=self.transitions_var)
        transitions_check.pack(anchor=tk.W)
        
        self.audio_norm_var = tk.BooleanVar()
        self.audio_norm_var.set(True)
        
        audio_norm_check = ttk.Checkbutton(options_frame, text="Normalize audio", 
                                         variable=self.audio_norm_var)
        audio_norm_check.pack(anchor=tk.W)
        
        self.titles_var = tk.BooleanVar()
        self.titles_var.set(True)
        
        titles_check = ttk.Checkbutton(options_frame, text="Add title overlays", 
                                     variable=self.titles_var)
        titles_check.pack(anchor=tk.W)
    
    def create_preview_tab(self, parent):
        """Create widgets for the preview tab."""
        # Create frame for processing button
        process_frame = ttk.Frame(parent)
        process_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.process_button = ttk.Button(process_frame, text="Process Videos and Create Supercut", 
                                       command=self.process_videos)
        self.process_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = ttk.Button(process_frame, text="Cancel Processing", 
                                      command=self.cancel_processing, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Create frame for preview
        preview_frame = ttk.LabelFrame(parent, text="Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create canvas for video preview
        self.preview_canvas = tk.Canvas(preview_frame, bg="black")
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create label for preview message
        self.preview_label = ttk.Label(preview_frame, text="Process videos to create a supercut", 
                                     anchor=tk.CENTER)
        self.preview_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Create frame for export button
        export_frame = ttk.Frame(parent)
        export_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.export_button = ttk.Button(export_frame, text="Open Supercut", 
                                      command=self.open_supercut, state=tk.DISABLED)
        self.export_button.pack(side=tk.LEFT, padx=5)
        
        self.open_folder_button = ttk.Button(export_frame, text="Open Output Folder", 
                                           command=self.open_output_folder)
        self.open_folder_button.pack(side=tk.LEFT, padx=5)
    
    def add_videos(self):
        """Add videos to the list."""
        filetypes = [
            ("Video files", "*.mp4 *.mkv *.avi *.mov"),
            ("All files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Select Mission Impossible Movie Files",
            filetypes=filetypes
        )
        
        if files:
            for file in files:
                if file not in self.video_paths:
                    self.video_paths.append(file)
                    self.video_listbox.insert(tk.END, os.path.basename(file))
            
            self.status_var.set(f"Added {len(files)} video(s)")
    
    def remove_videos(self):
        """Remove selected videos from the list."""
        selected_indices = self.video_listbox.curselection()
        
        if not selected_indices:
            return
        
        # Remove in reverse order to avoid index shifting
        for index in sorted(selected_indices, reverse=True):
            del self.video_paths[index]
            self.video_listbox.delete(index)
        
        self.status_var.set(f"Removed {len(selected_indices)} video(s)")
    
    def clear_videos(self):
        """Clear all videos from the list."""
        self.video_paths = []
        self.video_listbox.delete(0, tk.END)
        self.status_var.set("Cleared all videos")
    
    def browse_output_dir(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir
        )
        
        if directory:
            self.output_dir = directory
            self.output_dir_var.set(directory)
            self.app.output_dir = directory
            self.status_var.set(f"Output directory set to: {directory}")
    
    def process_videos(self):
        """Process videos and create supercut."""
        if not self.video_paths:
            messagebox.showwarning("No Videos", "Please add at least one video to process.")
            return
        
        # Update output directory
        self.output_dir = self.output_dir_var.get()
        self.app.output_dir = self.output_dir
        
        # Disable UI elements during processing
        self.process_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.export_button.config(state=tk.DISABLED)
        
        # Reset progress
        self.progress_var.set(0)
        self.status_var.set("Processing videos...")
        self.preview_label.config(text="Processing... Please wait.")
        
        # Get settings
        settings = {
            'detector_type': self.detector_var.get(),
            'threshold': self.threshold_var.get(),
            'min_scene_len': self.min_scene_var.get(),
            'save_images': self.save_images_var.get(),
            'target_duration': self.duration_var.get(),
            'min_confidence': self.confidence_var.get(),
            'min_duration': self.min_duration_var.get(),
            'max_duration': self.max_duration_var.get(),
            'ensure_diversity': self.diversity_var.get(),
            'add_transitions': self.transitions_var.get(),
            'normalize_audio': self.audio_norm_var.get(),
            'add_title': self.titles_var.get()
        }
        
        # Start processing thread
        self.processing_thread = threading.Thread(
            target=self.process_videos_thread,
            args=(self.video_paths, settings)
        )
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        # Start progress update
        self.root.after(100, self.update_progress)
    
    def process_videos_thread(self, video_paths, settings):
        """Process videos in a separate thread."""
        try:
            # Process videos
            self.supercut_path = self.app.process_multiple_videos(
                video_paths=video_paths,
                **settings
            )
            
            # Update UI from main thread
            self.root.after(0, self.processing_complete)
            
        except Exception as e:
            # Handle errors
            error_message = str(e)
            self.root.after(0, lambda: self.processing_error(error_message))
    
    def update_progress(self):
        """Update progress bar."""
        if self.processing_thread and self.processing_thread.is_alive():
            # Simulate progress (actual progress tracking would require modifications to the backend)
            current = self.progress_var.get()
            if current < 90:
                self.progress_var.set(current + 0.5)
            
            # Continue updating
            self.root.after(100, self.update_progress)
    
    def processing_complete(self):
        """Handle processing completion."""
        self.progress_var.set(100)
        
        if self.supercut_path:
            self.status_var.set(f"Supercut created: {os.path.basename(self.supercut_path)}")
            self.preview_label.config(text="Supercut created successfully!")
            self.export_button.config(state=tk.NORMAL)
            
            # Load preview image
            self.load_preview_image(self.supercut_path)
        else:
            self.status_var.set("Failed to create supercut")
            self.preview_label.config(text="Failed to create supercut. Check console for errors.")
        
        # Re-enable UI elements
        self.process_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
    
    def processing_error(self, error_message):
        """Handle processing error."""
        self.progress_var.set(0)
        self.status_var.set("Error during processing")
        self.preview_label.config(text=f"Error: {error_message}")
        
        # Show error message
        messagebox.showerror("Processing Error", f"An error occurred during processing:\n\n{error_message}")
        
        # Re-enable UI elements
        self.process_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
    
    def cancel_processing(self):
        """Cancel processing."""
        # Note: This doesn't actually stop the processing thread,
        # as the backend doesn't support cancellation.
        # In a real implementation, we would need to add cancellation support.
        self.status_var.set("Processing cancelled")
        self.preview_label.config(text="Processing cancelled by user.")
        
        # Re-enable UI elements
        self.process_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
    
    def load_preview_image(self, video_path):
        """Load a preview image from the video."""
        try:
            # Open video file
            cap = cv2.VideoCapture(video_path)
            
            # Get video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Seek to 1/3 of the video
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames // 3)
            
            # Read frame
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Convert frame to PIL Image
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                # Resize to fit canvas
                canvas_width = self.preview_canvas.winfo_width()
                canvas_height = self.preview_canvas.winfo_height()
                
                if canvas_width > 1 and canvas_height > 1:
                    # Calculate aspect ratio
                    aspect_ratio = width / height
                    
                    if canvas_width / canvas_height > aspect_ratio:
                        # Canvas is wider than video
                        new_height = canvas_height
                        new_width = int(new_height * aspect_ratio)
                    else:
                        # Canvas is taller than video
                        new_width = canvas_width
                        new_height = int(new_width / aspect_ratio)
                    
                    # Resize image
                    pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
                    
                    # Create PhotoImage
                    self.preview_image = ImageTk.PhotoImage(pil_image)
                    
                    # Clear canvas and display image
                    self.preview_canvas.delete("all")
                    self.preview_canvas.create_image(
                        canvas_width // 2, canvas_height // 2,
                        image=self.preview_image, anchor=tk.CENTER
                    )
                    
                    # Hide preview label
                    self.preview_label.place_forget()
                else:
                    # Canvas not ready yet, try again later
                    self.root.after(100, lambda: self.load_preview_image(video_path))
        except Exception as e:
            print(f"Error loading preview image: {str(e)}")
    
    def open_supercut(self):
        """Open the created supercut."""
        if self.supercut_path and os.path.exists(self.supercut_path):
            # Open with default video player
            if sys.platform == 'win32':
                os.startfile(self.supercut_path)
            elif sys.platform == 'darwin':
                os.system(f'open "{self.supercut_path}"')
            else:
                os.system(f'xdg-open "{self.supercut_path}"')
        else:
            messagebox.showwarning("File Not Found", "Supercut file not found.")
    
    def open_output_folder(self):
        """Open the output folder."""
        if os.path.exists(self.output_dir):
            # Open folder
            if sys.platform == 'win32':
                os.startfile(self.output_dir)
            elif sys.platform == 'darwin':
                os.system(f'open "{self.output_dir}"')
            else:
                os.system(f'xdg-open "{self.output_dir}"')
        else:
            messagebox.showwarning("Folder Not Found", "Output folder not found.")


def main():
    """Main function."""
    root = tk.Tk()
    app = SupercutGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
