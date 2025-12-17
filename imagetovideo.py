#!/usr/bin/env python3
"""
Image to Video Converter
Converts multiple images into a video file.
Run directly from terminal: python imagetovideo.py
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Optional
import cv2
import numpy as np
import random


def get_image_files(paths: List[str]) -> List[str]:
    """
    Get all image files from provided paths (files or directories).
    
    Args:
        paths: List of file paths or directory paths
        
    Returns:
        List of image file paths
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp', '.gif'}
    image_files = []
    
    for path_str in paths:
        path = Path(path_str)
        
        if not path.exists():
            print(f"⚠️  Warning: Path does not exist: {path_str}")
            continue
            
        if path.is_file():
            if path.suffix.lower() in image_extensions:
                image_files.append(str(path.absolute()))
            else:
                print(f"⚠️  Warning: Not an image file: {path_str}")
        elif path.is_dir():
            # Get all image files from directory
            for ext in image_extensions:
                image_files.extend([str(p.absolute()) for p in path.glob(f'*{ext}')])
                image_files.extend([str(p.absolute()) for p in path.glob(f'*{ext.upper()}')])
    
    # Remove duplicates and sort
    image_files = sorted(list(set(image_files)))
    return image_files


def get_transition_type() -> str:
    """
    Prompt user to select transition type.
    
    Returns:
        Selected transition type
    """
    transitions = {
        '1': ('fade', 'Fade - Smooth crossfade between images'),
        '2': ('slide_left', 'Slide Left - New image slides in from right'),
        '3': ('slide_right', 'Slide Right - New image slides in from left'),
        '4': ('slide_up', 'Slide Up - New image slides in from bottom'),
        '5': ('slide_down', 'Slide Down - New image slides in from top'),
        '6': ('zoom_in', 'Zoom In - Zoom into new image'),
        '7': ('zoom_out', 'Zoom Out - Zoom out from current image'),
        '8': ('wipe_left', 'Wipe Left - Wipe from right to left'),
        '9': ('wipe_right', 'Wipe Right - Wipe from left to right'),
        '10': ('wipe_up', 'Wipe Up - Wipe from bottom to top'),
        '11': ('wipe_down', 'Wipe Down - Wipe from top to bottom'),
        '12': ('random', 'Random - Random transition for each image'),
        '13': ('none', 'None - No transitions (instant switch)')
    }
    
    print("\n🎭 Available Transitions:")
    print("-" * 60)
    for key, (_, description) in transitions.items():
        print(f"  {key:>2}. {description}")
    print("-" * 60)
    
    while True:
        try:
            choice = input("\n   Select transition type (1-13, default: 1): ").strip()
            
            if not choice:
                choice = '1'
            
            if choice in transitions:
                selected = transitions[choice][0]
                print(f"✅ Selected: {transitions[choice][1]}")
                return selected
            else:
                print(f"❌ Invalid choice. Please enter a number between 1-13.")
                
        except KeyboardInterrupt:
            print("\n\n❌ Cancelled by user.")
            sys.exit(0)


def get_transition_duration() -> float:
    """
    Prompt user for transition duration in seconds.
    
    Returns:
        Transition duration in seconds
    """
    while True:
        try:
            duration_input = input("\n⏱️  Enter transition duration in seconds (e.g., 0.5, 1.0, 2.0, default: 1.0): ").strip()
            
            if not duration_input:
                duration_seconds = 1.0
            else:
                duration_seconds = float(duration_input)
            
            if duration_seconds < 0:
                print("❌ Duration cannot be negative. Please try again.")
                continue
            
            if duration_seconds > 5:
                print("⚠️  Warning: Very long transitions (>5s) may not work well with short image durations.")
                confirm = input("   Continue anyway? (y/n): ").strip().lower()
                if confirm != 'y':
                    continue
            
            print(f"✅ Transition duration: {duration_seconds:.2f} seconds")
            return duration_seconds
            
        except ValueError:
            print("❌ Invalid input. Please enter a number (e.g., 0.5 or 1.0).")
        except KeyboardInterrupt:
            print("\n\n❌ Cancelled by user.")
            sys.exit(0)


def get_video_duration() -> float:
    """
    Prompt user for video duration in minutes.
    Accepts format like 1.3 (1 minute 3 seconds) or 1.05 (1 minute 5 seconds).
    
    Returns:
        Duration in seconds
    """
    while True:
        try:
            duration_input = input("\n📹 Enter video duration in minutes (e.g., 1.3 for 1 min 3 sec, or 2.5 for 2 min 30 sec): ").strip()
            
            if not duration_input:
                print("❌ Duration cannot be empty. Please try again.")
                continue
            
            # Parse the duration
            duration_minutes = float(duration_input)
            
            if duration_minutes <= 0:
                print("❌ Duration must be greater than 0. Please try again.")
                continue
            
            # Convert to seconds
            duration_seconds = duration_minutes * 60
            
            # Calculate minutes and seconds for display
            minutes = int(duration_seconds // 60)
            seconds = int(duration_seconds % 60)
            
            print(f"✅ Video duration: {minutes} minute(s) {seconds} second(s) ({duration_seconds:.2f} seconds)")
            return duration_seconds
            
        except ValueError:
            print("❌ Invalid input. Please enter a number (e.g., 1.3 or 2.5).")
        except KeyboardInterrupt:
            print("\n\n❌ Cancelled by user.")
            sys.exit(0)


def apply_fade_transition(
    img1: np.ndarray,
    img2: np.ndarray,
    progress: float
) -> np.ndarray:
    """
    Apply fade/crossfade transition between two images.
    
    Args:
        img1: First image
        img2: Second image
        progress: Transition progress (0.0 to 1.0)
        
    Returns:
        Blended image
    """
    progress = np.clip(progress, 0.0, 1.0)
    return cv2.addWeighted(img1, 1.0 - progress, img2, progress, 0)


def apply_slide_transition(
    img1: np.ndarray,
    img2: np.ndarray,
    progress: float,
    direction: str
) -> np.ndarray:
    """
    Apply slide transition between two images.
    
    Args:
        img1: First image
        img2: Second image
        progress: Transition progress (0.0 to 1.0)
        direction: 'left', 'right', 'up', 'down'
        
    Returns:
        Combined image with slide effect
    """
    progress = np.clip(progress, 0.0, 1.0)
    height, width = img1.shape[:2]
    result = img1.copy()
    
    if direction == 'left':
        slide_width = int(width * progress)
        result[:, :slide_width] = img2[:, :slide_width]
    elif direction == 'right':
        slide_width = int(width * progress)
        start = width - slide_width
        result[:, start:] = img2[:, start:]
    elif direction == 'up':
        slide_height = int(height * progress)
        result[:slide_height, :] = img2[:slide_height, :]
    elif direction == 'down':
        slide_height = int(height * progress)
        start = height - slide_height
        result[start:, :] = img2[start:, :]
    
    return result


def apply_zoom_transition(
    img1: np.ndarray,
    img2: np.ndarray,
    progress: float,
    zoom_type: str
) -> np.ndarray:
    """
    Apply zoom transition between two images.
    
    Args:
        img1: First image
        img2: Second image
        progress: Transition progress (0.0 to 1.0)
        zoom_type: 'in' or 'out'
        
    Returns:
        Zoomed and blended image
    """
    progress = np.clip(progress, 0.0, 1.0)
    height, width = img1.shape[:2]
    
    if zoom_type == 'in':
        # Zoom into img2
        scale = 1.0 + progress * 0.3  # Zoom up to 30%
        center_x, center_y = width // 2, height // 2
        
        # Create transformation matrix
        M = cv2.getRotationMatrix2D((center_x, center_y), 0, scale)
        zoomed = cv2.warpAffine(img2, M, (width, height))
        
        # Fade between img1 and zoomed img2
        return cv2.addWeighted(img1, 1.0 - progress, zoomed, progress, 0)
    else:  # zoom_out
        # Zoom out from img1
        scale = 1.3 - progress * 0.3  # Start at 130%, zoom to 100%
        center_x, center_y = width // 2, height // 2
        
        # Create transformation matrix
        M = cv2.getRotationMatrix2D((center_x, center_y), 0, scale)
        zoomed = cv2.warpAffine(img1, M, (width, height))
        
        # Fade between zoomed img1 and img2
        return cv2.addWeighted(zoomed, 1.0 - progress, img2, progress, 0)


def apply_wipe_transition(
    img1: np.ndarray,
    img2: np.ndarray,
    progress: float,
    direction: str
) -> np.ndarray:
    """
    Apply wipe transition between two images.
    
    Args:
        img1: First image
        img2: Second image
        progress: Transition progress (0.0 to 1.0)
        direction: 'left', 'right', 'up', 'down'
        
    Returns:
        Combined image with wipe effect
    """
    progress = np.clip(progress, 0.0, 1.0)
    height, width = img1.shape[:2]
    result = img1.copy()
    
    if direction == 'left':
        wipe_pos = int(width * progress)
        result[:, :wipe_pos] = img2[:, :wipe_pos]
    elif direction == 'right':
        wipe_pos = int(width * (1 - progress))
        result[:, wipe_pos:] = img2[:, wipe_pos:]
    elif direction == 'up':
        wipe_pos = int(height * progress)
        result[:wipe_pos, :] = img2[:wipe_pos, :]
    elif direction == 'down':
        wipe_pos = int(height * (1 - progress))
        result[wipe_pos:, :] = img2[wipe_pos:, :]
    
    return result


def apply_transition(
    img1: np.ndarray,
    img2: np.ndarray,
    progress: float,
    transition_type: str
) -> np.ndarray:
    """
    Apply the specified transition between two images.
    
    Args:
        img1: First image
        img2: Second image
        progress: Transition progress (0.0 to 1.0)
        transition_type: Type of transition to apply
        
    Returns:
        Transitioned image
    """
    if transition_type == 'fade':
        return apply_fade_transition(img1, img2, progress)
    elif transition_type == 'slide_left':
        return apply_slide_transition(img1, img2, progress, 'left')
    elif transition_type == 'slide_right':
        return apply_slide_transition(img1, img2, progress, 'right')
    elif transition_type == 'slide_up':
        return apply_slide_transition(img1, img2, progress, 'up')
    elif transition_type == 'slide_down':
        return apply_slide_transition(img1, img2, progress, 'down')
    elif transition_type == 'zoom_in':
        return apply_zoom_transition(img1, img2, progress, 'in')
    elif transition_type == 'zoom_out':
        return apply_zoom_transition(img1, img2, progress, 'out')
    elif transition_type == 'wipe_left':
        return apply_wipe_transition(img1, img2, progress, 'left')
    elif transition_type == 'wipe_right':
        return apply_wipe_transition(img1, img2, progress, 'right')
    elif transition_type == 'wipe_up':
        return apply_wipe_transition(img1, img2, progress, 'up')
    elif transition_type == 'wipe_down':
        return apply_wipe_transition(img1, img2, progress, 'down')
    elif transition_type == 'none':
        return img2 if progress >= 0.5 else img1
    else:  # random or unknown
        return apply_fade_transition(img1, img2, progress)


def resize_image_to_fit(image: np.ndarray, target_width: int, target_height: int) -> np.ndarray:
    """
    Resize image to fit within target dimensions while maintaining aspect ratio.
    
    Args:
        image: Input image as numpy array
        target_width: Target width
        target_height: Target height
        
    Returns:
        Resized image
    """
    height, width = image.shape[:2]
    
    # Calculate scaling factor
    scale = min(target_width / width, target_height / height)
    
    # Calculate new dimensions
    new_width = int(width * scale)
    new_height = int(height * scale)
    
    # Resize image
    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
    
    # Create black background
    result = np.zeros((target_height, target_width, 3), dtype=np.uint8)
    
    # Center the image
    y_offset = (target_height - new_height) // 2
    x_offset = (target_width - new_width) // 2
    result[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = resized
    
    return result


def create_video_from_images(
    image_paths: List[str],
    output_path: str,
    duration_seconds: float,
    fps: int = 30,
    target_width: int = 1920,
    target_height: int = 1080,
    transition_type: str = 'fade',
    transition_duration: float = 1.0
) -> bool:
    """
    Create a video from a list of images with smooth transitions.
    
    Args:
        image_paths: List of image file paths
        output_path: Output video file path
        duration_seconds: Total duration of video in seconds
        fps: Frames per second
        target_width: Target video width
        target_height: Target video height
        transition_type: Type of transition ('fade', 'slide_left', etc., or 'random')
        transition_duration: Duration of each transition in seconds
        
    Returns:
        True if successful, False otherwise
    """
    if not image_paths:
        print("❌ No images found to process.")
        return False
    
    print(f"\n📸 Found {len(image_paths)} image(s)")
    print(f"🎬 Creating video: {output_path}")
    print(f"   Resolution: {target_width}x{target_height}")
    print(f"   FPS: {fps}")
    print(f"   Duration: {duration_seconds:.2f} seconds")
    print(f"   Transition: {transition_type}")
    print(f"   Transition duration: {transition_duration:.2f} seconds")
    
    # Calculate timing
    total_frames = int(duration_seconds * fps)
    transition_frames = int(transition_duration * fps)
    
    # Calculate frames per image segment (excluding transitions)
    if len(image_paths) == 1:
        frames_per_image = total_frames
        transition_frames = 0
    else:
        # Total transition time
        total_transition_time = transition_duration * (len(image_paths) - 1)
        # Remaining time for displaying images
        image_display_time = duration_seconds - total_transition_time
        
        if image_display_time <= 0:
            print("⚠️  Warning: Transition duration too long for video duration.")
            print("   Reducing transition duration to fit video length.")
            # Adjust transition duration
            transition_duration = duration_seconds / (len(image_paths) * 2)
            transition_frames = int(transition_duration * fps)
            image_display_time = duration_seconds - (transition_duration * (len(image_paths) - 1))
        
        frames_per_image = max(1, int((image_display_time / len(image_paths)) * fps))
    
    print(f"   Frames per image: {frames_per_image}")
    print(f"   Transition frames: {transition_frames}")
    
    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (target_width, target_height))
    
    if not video_writer.isOpened():
        print(f"❌ Error: Could not open video writer for {output_path}")
        return False
    
    # Pre-load and resize all images
    print("\n   Loading and resizing images...")
    resized_images = []
    for idx, image_path in enumerate(image_paths, 1):
        image = cv2.imread(image_path)
        if image is None:
            print(f"      ⚠️  Warning: Could not read image: {image_path}")
            continue
        resized = resize_image_to_fit(image, target_width, target_height)
        resized_images.append(resized)
    
    if not resized_images:
        print("❌ No valid images to process.")
        video_writer.release()
        return False
    
    # Available transitions for random selection
    available_transitions = [
        'fade', 'slide_left', 'slide_right', 'slide_up', 'slide_down',
        'zoom_in', 'zoom_out', 'wipe_left', 'wipe_right', 'wipe_up', 'wipe_down'
    ]
    
    try:
        current_transition = transition_type
        frame_count = 0
        
        for idx in range(len(resized_images)):
            current_image = resized_images[idx]
            print(f"   Processing image {idx + 1}/{len(resized_images)}: {os.path.basename(image_paths[idx])}")
            
            # Determine transition type for this segment
            if transition_type == 'random' and idx > 0:
                current_transition = random.choice(available_transitions)
            
            # Write image display frames (before transition)
            if idx == 0 or transition_type == 'none':
                # First image or no transitions - just display
                for _ in range(frames_per_image):
                    video_writer.write(current_image)
                    frame_count += 1
            else:
                # Display part of current image before transition
                display_frames = frames_per_image // 2 if frames_per_image > 2 else 0
                for _ in range(display_frames):
                    video_writer.write(current_image)
                    frame_count += 1
                
                # Apply transition from previous to current image
                if transition_frames > 0 and idx > 0:
                    prev_image = resized_images[idx - 1]
                    for t in range(transition_frames):
                        progress = t / transition_frames
                        transitioned_frame = apply_transition(prev_image, current_image, progress, current_transition)
                        video_writer.write(transitioned_frame)
                        frame_count += 1
                
                # Display remaining part of current image after transition
                remaining_frames = frames_per_image - display_frames
                for _ in range(remaining_frames):
                    video_writer.write(current_image)
                    frame_count += 1
        
        # Fill remaining frames with last image if needed
        while frame_count < total_frames:
            video_writer.write(resized_images[-1])
            frame_count += 1
        
        video_writer.release()
        print(f"\n✅ Video created successfully: {output_path}")
        
        # Check if file was created and show size
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            file_size_mb = file_size / (1024 * 1024)
            print(f"   File size: {file_size_mb:.2f} MB")
            print(f"   Total frames: {frame_count}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating video: {e}")
        import traceback
        traceback.print_exc()
        video_writer.release()
        if os.path.exists(output_path):
            os.remove(output_path)
        return False


def main():
    """Main function to run the image to video converter."""
    parser = argparse.ArgumentParser(
        description='Convert multiple images into a video file.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode - will prompt for images and duration
  python imagetovideo.py
  
  # Provide images via command line
  python imagetovideo.py image1.jpg image2.png image3.jpg
  
  # Provide directory containing images
  python imagetovideo.py /path/to/images/
  
  # Mix of files and directories
  python imagetovideo.py image1.jpg /path/to/images/ image2.png
  
  # Specify output file
  python imagetovideo.py --output myvideo.mp4 image1.jpg image2.png
        """
    )
    
    parser.add_argument(
        'images',
        nargs='*',
        help='Image files or directories containing images'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Output video file path (default: video_YYYYMMDD_HHMMSS.mp4)'
    )
    
    parser.add_argument(
        '--fps',
        type=int,
        default=30,
        help='Frames per second (default: 30)'
    )
    
    parser.add_argument(
        '--width',
        type=int,
        default=1920,
        help='Video width in pixels (default: 1920)'
    )
    
    parser.add_argument(
        '--height',
        type=int,
        default=1080,
        help='Video height in pixels (default: 1080)'
    )
    
    parser.add_argument(
        '--transition', '-t',
        type=str,
        default=None,
        choices=['fade', 'slide_left', 'slide_right', 'slide_up', 'slide_down',
                 'zoom_in', 'zoom_out', 'wipe_left', 'wipe_right', 'wipe_up', 'wipe_down',
                 'random', 'none'],
        help='Transition type (default: interactive selection)'
    )
    
    parser.add_argument(
        '--transition-duration', '-td',
        type=float,
        default=None,
        help='Transition duration in seconds (default: interactive selection)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎬 Image to Video Converter")
    print("=" * 60)
    
    # Get image files
    image_files = []
    
    if args.images:
        # Use provided images
        image_files = get_image_files(args.images)
    else:
        # Interactive mode
        print("\n📁 Enter image file paths or directory paths (one per line).")
        print("   Press Enter twice when done, or Ctrl+C to cancel.")
        
        try:
            paths = []
            while True:
                path_input = input("   Image/Directory path: ").strip()
                
                if not path_input:
                    if paths:
                        break
                    else:
                        print("   ⚠️  Please enter at least one path.")
                        continue
                
                paths.append(path_input)
            
            image_files = get_image_files(paths)
            
        except KeyboardInterrupt:
            print("\n\n❌ Cancelled by user.")
            sys.exit(0)
    
    if not image_files:
        print("\n❌ No valid images found. Please check your paths.")
        sys.exit(1)
    
    # Get video duration
    duration_seconds = get_video_duration()
    
    # Get transition type
    if args.transition:
        transition_type = args.transition
        print(f"✅ Using transition: {transition_type}")
    else:
        transition_type = get_transition_type()
    
    # Get transition duration
    if args.transition_duration is not None:
        transition_duration = args.transition_duration
        if transition_duration < 0:
            print("❌ Transition duration cannot be negative. Using default 1.0s.")
            transition_duration = 1.0
        print(f"✅ Transition duration: {transition_duration:.2f} seconds")
    else:
        transition_duration = get_transition_duration()
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"video_{timestamp}.mp4"
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path) or '.'
    os.makedirs(output_dir, exist_ok=True)
    
    # Create video
    success = create_video_from_images(
        image_files,
        output_path,
        duration_seconds,
        fps=args.fps,
        target_width=args.width,
        target_height=args.height,
        transition_type=transition_type,
        transition_duration=transition_duration
    )
    
    if success:
        print(f"\n🎉 Done! Video saved to: {os.path.abspath(output_path)}")
        sys.exit(0)
    else:
        print("\n❌ Failed to create video.")
        sys.exit(1)


if __name__ == '__main__':
    main()

