"""
Video Creator - Fast Frame Generation with Pillow
Creates high-quality videos with professional text overlays
"""
from moviepy.editor import ImageSequenceClip
from PIL import Image, ImageDraw, ImageFont
import os
from typing import List, Dict
import config

class VideoCreator:
    def __init__(self):
        self.width = config.VIDEO_WIDTH
        self.height = config.VIDEO_HEIGHT
        self.fps = config.VIDEO_FPS
        self.text_duration = config.TEXT_DISPLAY_TIME
        self.frames_per_segment = int(self.text_duration * self.fps)
        
        self.frames_dir = os.path.join(config.ASSETS_DIR, 'frames')
        self.frame_counter = 0
        
        # Clean old frames
        if os.path.exists(self.frames_dir):
            for f in os.listdir(self.frames_dir):
                try:
                    os.remove(os.path.join(self.frames_dir, f))
                except:
                    pass
        
        os.makedirs(self.frames_dir, exist_ok=True)
    
    def get_next_frame_path(self):
        """Get next frame path"""
        path = os.path.join(self.frames_dir, f'{self.frame_counter:06d}.png')
        self.frame_counter += 1
        return path
    
    def get_font(self, size: int):
        """Get available font with fallback"""
        font_paths = [
            "C:\\Windows\\Fonts\\arial.ttf",  # Windows
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
            "/Library/Fonts/Arial.ttf",  # macOS
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except:
                    pass
        
        return ImageFont.load_default()
    
    def create_frame_with_text(self, output_path: str, text: str, font_size: int = 48, 
                              bg_color: tuple = (30, 30, 50), text_opacity: float = 1.0):
        """Create frame with text using Pillow"""
        # Create image
        img = Image.new('RGB', (self.width, self.height), bg_color)
        draw = ImageDraw.Draw(img, 'RGBA')
        
        font = self.get_font(font_size)
        
        # Word wrap text
        words = text.split()
        lines = []
        current_line = []
        max_width = self.width - 100
        
        for word in words:
            current_line.append(word)
            line_text = " ".join(current_line)
            bbox = draw.textbbox((0, 0), line_text, font=font)
            line_width = bbox[2] - bbox[0]
            
            if line_width > max_width and len(current_line) > 1:
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(" ".join(current_line))
        
        # Calculate y position
        line_height = int(font_size * 1.3)
        total_height = len(lines) * line_height
        start_y = (self.height - total_height) // 2
        
        # Draw text with shadow
        alpha = int(255 * text_opacity)
        
        for i, line in enumerate(lines):
            y = start_y + i * line_height
            x = self.width // 2
            
            # Get text bbox for centering
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            centered_x = x - text_width // 2
            
            # Draw shadow (dark, offset)
            shadow_color = (0, 0, 0, int(alpha * 0.7))
            draw.text((centered_x + 3, y + 3), line, font=font, fill=shadow_color)
            
            # Draw main text (white)
            text_color = (255, 255, 255, alpha)
            draw.text((centered_x, y), line, font=font, fill=text_color)
        
        img.save(output_path)
    
    def create_title_frames(self, title: str) -> List[str]:
        """Create animated title frames"""
        frame_paths = []
        num_frames = int(3 * self.fps)
        
        print(f"  Creating {num_frames} title frames...")
        
        for frame_num in range(num_frames):
            frame_path = self.get_next_frame_path()
            
            # Fade in effect
            progress = frame_num / num_frames
            opacity = min(1.0, progress * 3)
            
            self.create_frame_with_text(
                frame_path, 
                title, 
                font_size=72, 
                bg_color=(20, 20, 40),
                text_opacity=opacity
            )
            
            frame_paths.append(frame_path)
        
        return frame_paths
    
    def create_segment_frames(self, text: str, bg_image: str = None) -> List[str]:
        """Create segment frames with fade in/out"""
        frame_paths = []
        
        for frame_num in range(self.frames_per_segment):
            frame_path = self.get_next_frame_path()
            
            # Handle background image
            if bg_image and os.path.exists(bg_image):
                try:
                    bg = Image.open(bg_image).convert('RGB')
                    bg.thumbnail((self.width, self.height), Image.Resampling.LANCZOS)
                    
                    if bg.size != (self.width, self.height):
                        # Pad to correct size
                        bg_new = Image.new('RGB', (self.width, self.height), (30, 30, 50))
                        x_offset = (self.width - bg.width) // 2
                        y_offset = (self.height - bg.height) // 2
                        bg_new.paste(bg, (x_offset, y_offset))
                        bg = bg_new
                    
                    bg.save(frame_path, 'PNG')
                    
                    # Add overlay
                    overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 128))
                    bg_rgba = Image.open(frame_path).convert('RGBA')
                    bg_rgba = Image.alpha_composite(bg_rgba, overlay)
                    bg_rgba.convert('RGB').save(frame_path, 'PNG')
                except:
                    self.create_frame_with_text(frame_path, text, font_size=48)
                    continue
            else:
                self.create_frame_with_text(frame_path, text, font_size=48)
                continue
            
            # Add text to the frame
            frame_img = Image.open(frame_path).convert('RGBA')
            draw = ImageDraw.Draw(frame_img)
            
            # Fade in/out
            progress = frame_num / self.frames_per_segment
            if progress < 0.2:
                opacity = progress / 0.2
            elif progress > 0.8:
                opacity = (1 - progress) / 0.2
            else:
                opacity = 1.0
            
            # Word wrap
            words = text.split()
            lines = []
            current_line = []
            font = self.get_font(48)
            max_width = self.width - 100
            
            for word in words:
                current_line.append(word)
                line_text = " ".join(current_line)
                bbox = draw.textbbox((0, 0), line_text, font=font)
                if (bbox[2] - bbox[0]) > max_width and len(current_line) > 1:
                    current_line.pop()
                    lines.append(" ".join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(" ".join(current_line))
            
            # Draw text
            line_height = int(48 * 1.3)
            total_height = len(lines) * line_height
            start_y = (self.height - total_height) // 2
            
            alpha = int(255 * opacity)
            
            for i, line in enumerate(lines):
                y = start_y + i * line_height
                x = self.width // 2
                
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                centered_x = x - text_width // 2
                
                # Shadow
                draw.text((centered_x + 3, y + 3), line, font=font, fill=(0, 0, 0, int(alpha * 0.7)))
                # Text
                draw.text((centered_x, y), line, font=font, fill=(255, 255, 255, alpha))
            
            frame_img.save(frame_path, 'PNG')
            frame_paths.append(frame_path)
        
        return frame_paths
    
    def create_video_from_frames(self, output_filename: str) -> str:
        """Convert frames to video using MoviePy"""
        frame_files = sorted([f for f in os.listdir(self.frames_dir) if f.endswith('.png')])
        frame_paths = [os.path.join(self.frames_dir, f) for f in frame_files]
        
        if not frame_paths:
            print("ERROR: No frames generated!")
            return None
        
        print(f"Converting {len(frame_paths)} frames to video (this takes a minute)...")
        
        try:
            clip = ImageSequenceClip(frame_paths, fps=self.fps)
            
            os.makedirs(config.OUTPUT_VIDEO_DIR, exist_ok=True)
            output_path = os.path.join(config.OUTPUT_VIDEO_DIR, output_filename)
            
            clip.write_videofile(
                output_path,
                fps=self.fps,
                codec='libx264',
                audio=False,
                preset='fast',
                bitrate='5000k',
                verbose=False,
                logger=None
            )
            
            clip.close()
            
            # Cleanup
            for fp in frame_paths:
                try:
                    os.remove(fp)
                except:
                    pass
            
            print(f"✓ Video saved: {output_path}")
            return output_path
        
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def create_video(self, article: Dict, script: Dict, output_filename: str = None) -> str:
        """Create video"""
        if not output_filename:
            safe_title = "".join(c for c in article['title'][:30] if c.isalnum() or c in (' ', '-', '_'))
            output_filename = f"{safe_title.replace(' ', '_')}.mp4"
        
        print(f"\n🎬 Creating: {article['title']}")
        
        self.frame_counter = 0
        
        # Title
        print("📝 Creating title...")
        self.create_title_frames(article['title'])
        
        # Segments
        segments = [s for s in [
            script.get('hook', ''),
            *script.get('segments', []),
            script.get('conclusion', '')
        ] if s.strip()]
        
        print(f"📝 Creating {len(segments)} segments...")
        
        for i, segment in enumerate(segments):
            if i % 5 == 0:
                print(f"  → {i+1}/{len(segments)}")
            
            self.create_segment_frames(segment, article.get('image_url'))
        
        print("🎥 Rendering video...")
        return self.create_video_from_frames(output_filename)
