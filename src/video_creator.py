"""
Video Creator Module
Creates videos with text overlays and images using MoviePy and Pillow
"""
from moviepy.editor import (
    ImageClip, CompositeVideoClip, concatenate_videoclips
)
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
        
    def get_font(self, size: int):
        """Get font with fallback support"""
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
            "/System/Library/Fonts/Arial.ttf",  # macOS
            "C:\\Windows\\Fonts\\arial.ttf",  # Windows
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except:
                    pass
        
        # Fallback to default font
        return ImageFont.load_default()
    
    def create_gradient_background(self, color=(30, 30, 50)) -> str:
        """Create a gradient background image using Pillow"""
        img = Image.new('RGB', (self.width, self.height), color)
        draw = ImageDraw.Draw(img)
        
        # Add gradient effect
        for i in range(self.height):
            alpha = i / self.height
            r = int(color[0] * (1 - alpha * 0.3))
            g = int(color[1] * (1 - alpha * 0.3))
            b = int(color[2] + (100 * alpha * 0.5))
            draw.line([(0, i), (self.width, i)], fill=(r, g, b))
        
        # Save temporary background
        os.makedirs(config.ASSETS_DIR, exist_ok=True)
        bg_path = os.path.join(config.ASSETS_DIR, 'temp_background.png')
        img.save(bg_path)
        
        return bg_path
    
    def create_text_image(self, text: str, width: int = None, max_lines: int = 4) -> Image.Image:
        """Create an image with text using Pillow"""
        if width is None:
            width = self.width - 100
        
        font_size = config.FONT_SIZE
        font = self.get_font(font_size)
        
        # Split text into lines
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            line_text = " ".join(current_line)
            bbox = draw.textbbox((0, 0), line_text, font=font)
            line_width = bbox[2] - bbox[0]
            
            if line_width > width and len(current_line) > 1:
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(" ".join(current_line))
        
        # Limit lines
        lines = lines[:max_lines]
        
        # Create image for text
        temp_img = Image.new('RGBA', (width, 500), (0, 0, 0, 0))
        draw = ImageDraw.Draw(temp_img)
        
        y_offset = 0
        for line in lines:
            draw.text((0, y_offset), line, font=font, fill=config.FONT_COLOR)
            bbox = draw.textbbox((0, y_offset), line, font=font)
            y_offset += bbox[3] - bbox[1] + 10
        
        # Crop to content
        bbox = temp_img.getbbox()
        if bbox:
            text_img = temp_img.crop(bbox)
        else:
            text_img = temp_img
        
        return text_img
    
    def create_text_overlay(self, text: str, bg_width: int = None, bg_height: int = None) -> Image.Image:
        """Create a complete text overlay with background"""
        if bg_width is None:
            bg_width = self.width
        if bg_height is None:
            bg_height = self.height
        
        # Create background
        overlay = Image.new('RGBA', (bg_width, bg_height), (0, 0, 0, 0))
        
        # Create text image
        text_img = self.create_text_image(text, width=bg_width - 100)
        
        # Center text vertically and horizontally
        text_x = (bg_width - text_img.width) // 2
        text_y = (bg_height - text_img.height) // 2
        
        overlay.paste(text_img, (text_x, text_y), text_img)
        
        return overlay
    
    def create_title_image(self, title: str, subtitle: str = "Trending News") -> str:
        """Create title image using Pillow"""
        img = Image.new('RGB', (self.width, self.height), (20, 20, 40))
        draw = ImageDraw.Draw(img)
        
        # Add gradient
        for i in range(self.height):
            alpha = i / self.height
            r = int(20 * (1 - alpha * 0.3))
            g = int(20 * (1 - alpha * 0.3))
            b = int(40 + (100 * alpha * 0.5))
            draw.line([(0, i), (self.width, i)], fill=(r, g, b))
        
        # Draw title
        title_font = self.get_font(int(config.FONT_SIZE * 1.5))
        subtitle_font = self.get_font(config.FONT_SIZE)
        
        # Center title
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_x = (self.width - (title_bbox[2] - title_bbox[0])) // 2
        title_y = (self.height // 2) - 50
        
        draw.text((title_x, title_y), title, font=title_font, fill=config.FONT_COLOR)
        
        # Center subtitle
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        subtitle_x = (self.width - (subtitle_bbox[2] - subtitle_bbox[0])) // 2
        subtitle_y = title_y + 80
        
        draw.text((subtitle_x, subtitle_y), subtitle, font=subtitle_font, fill=(200, 200, 200))
        
        # Save
        os.makedirs(config.ASSETS_DIR, exist_ok=True)
        title_path = os.path.join(config.ASSETS_DIR, 'title_image.png')
        img.save(title_path)
        
        return title_path
    
    def create_segment_image(self, text: str, bg_path: str = None) -> str:
        """Create segment image with text overlay"""
        if bg_path and os.path.exists(bg_path):
            img = Image.open(bg_path).convert('RGB')
            img.thumbnail((self.width, self.height), Image.Resampling.LANCZOS)
            
            # Resize to exact dimensions
            if img.size != (self.width, self.height):
                img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
        else:
            img = Image.new('RGB', (self.width, self.height), (30, 30, 50))
            draw = ImageDraw.Draw(img)
            
            # Add gradient
            for i in range(self.height):
                alpha = i / self.height
                r = int(30 * (1 - alpha * 0.3))
                g = int(30 * (1 - alpha * 0.3))
                b = int(50 + (100 * alpha * 0.5))
                draw.line([(0, i), (self.width, i)], fill=(r, g, b))
        
        # Add semi-transparent overlay for text readability
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 80))
        img = img.convert('RGBA')
        img = Image.alpha_composite(img, overlay)
        
        # Add text
        draw = ImageDraw.Draw(img)
        font = self.get_font(config.FONT_SIZE)
        
        # Word wrap text
        words = text.split()
        lines = []
        current_line = []
        max_width = self.width - 100
        
        for word in words:
            current_line.append(word)
            line_text = " ".join(current_line)
            bbox = draw.textbbox((0, 0), line_text, font=font)
            
            if (bbox[2] - bbox[0]) > max_width:
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(" ".join(current_line))
        
        # Calculate starting y position for centered text
        total_height = len(lines) * 40
        start_y = (self.height - total_height) // 2
        
        # Draw text with shadow effect
        for i, line in enumerate(lines):
            y = start_y + (i * 40)
            x = 50
            
            # Shadow
            draw.text((x + 2, y + 2), line, font=font, fill=(0, 0, 0, 150))
            # Text
            draw.text((x, y), line, font=font, fill=config.FONT_COLOR)
        
        # Save
        os.makedirs(config.ASSETS_DIR, exist_ok=True)
        segment_path = os.path.join(config.ASSETS_DIR, f'segment_{hash(text)}.png')
        img = img.convert('RGB')
        img.save(segment_path)
        
        return segment_path
    
    def create_video_from_script(
        self, 
        script_segments: List[str], 
        title: str,
        output_filename: str,
        background_image: str = None
    ) -> str:
        """Create a complete video from script segments"""
        print(f"Creating video with {len(script_segments)} segments...")
        
        clips = []
        
        # Create title clip
        title_path = self.create_title_image(title)
        title_clip = ImageClip(title_path).set_duration(3)
        clips.append(title_clip)
        
        # Create segment clips
        for i, segment in enumerate(script_segments):
            if not segment.strip():
                continue
            
            print(f"Processing segment {i+1}/{len(script_segments)}: {segment[:50]}...")
            segment_path = self.create_segment_image(segment, bg_path=background_image)
            segment_clip = ImageClip(segment_path).set_duration(self.text_duration)
            clips.append(segment_clip)
        
        # Concatenate all clips
        print("Concatenating clips...")
        final_video = concatenate_videoclips(clips, method="compose")
        
        # Ensure output directory exists
        os.makedirs(config.OUTPUT_VIDEO_DIR, exist_ok=True)
        output_path = os.path.join(config.OUTPUT_VIDEO_DIR, output_filename)
        
        # Export video
        print(f"Exporting video to {output_path}...")
        final_video.write_videofile(
            output_path,
            fps=self.fps,
            codec='libx264',
            audio=False,
            preset='medium',
            threads=4,
            verbose=False,
            logger=None
        )
        
        # Cleanup
        final_video.close()
        for clip in clips:
            clip.close()
        
        print(f"Video created successfully: {output_path}")
        return output_path
    
    def create_video(
        self, 
        article: Dict, 
        script: Dict, 
        output_filename: str = None
    ) -> str:
        """Create video from article and script"""
        if not output_filename:
            # Generate filename from article title
            safe_title = "".join(c for c in article['title'][:30] if c.isalnum() or c in (' ', '-', '_'))
            safe_title = safe_title.replace(' ', '_')
            output_filename = f"{safe_title}.mp4"
        
        # Get script segments
        segments = []
        segments.append(script.get('hook', ''))
        segments.extend(script.get('segments', []))
        segments.append(script.get('conclusion', ''))
        
        # Filter empty segments
        segments = [s for s in segments if s.strip()]
        
        # Create video
        return self.create_video_from_script(
            segments,
            article['title'],
            output_filename,
            background_image=article.get('image_url')
        )

if __name__ == "__main__":
    # Test video creator
    test_article = {
        'title': 'AI Technology News',
        'description': 'Breaking developments in artificial intelligence',
        'source': 'Tech News',
        'url': 'https://example.com',
        'image_url': ''
    }
    
    test_script = {
        'hook': 'Big news in AI technology!',
        'segments': [
            'Revolutionary changes are coming',
            'This will transform everything',
            'What does it mean for you?'
        ],
        'conclusion': 'Stay tuned for updates!'
    }
    
    creator = VideoCreator()
    creator.create_video(test_article, test_script, "test_video.mp4")
