"""
Video Creator Module
Creates videos with text overlays and images using MoviePy
"""

from moviepy.editor import (
    TextClip, ImageClip, CompositeVideoClip, 
    concatenate_videoclips, ColorClip
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
        
    def create_background(self, color=(30, 30, 50)) -> str:
        """Create a gradient background image"""
        # Create gradient background
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
    
    def create_text_clip(self, text: str, duration: float, position='center') -> TextClip:
        """Create a text clip with styling"""
        try:
            # Try to create text clip with specified font
            text_clip = TextClip(
                text,
                fontsize=config.FONT_SIZE,
                color=config.FONT_COLOR,
                font='Arial-Bold',
                size=(self.width - 100, None),
                method='caption',
                align='center'
            ).set_duration(duration).set_position(position)
            
            return text_clip
        except Exception as e:
            print(f"Error creating text clip with custom font: {e}")
            # Fallback to default font
            text_clip = TextClip(
                text,
                fontsize=config.FONT_SIZE,
                color=config.FONT_COLOR,
                size=(self.width - 100, None),
                method='caption',
                align='center'
            ).set_duration(duration).set_position(position)
            
            return text_clip
    
    def create_title_clip(self, title: str, duration: float = 3) -> CompositeVideoClip:
        """Create an opening title clip"""
        # Background
        bg_path = self.create_background(color=(20, 20, 40))
        background = ImageClip(bg_path).set_duration(duration)
        
        # Title text
        title_text = self.create_text_clip(title, duration, position='center')
        
        # Subtitle
        subtitle = self.create_text_clip(
            "Trending News", 
            duration, 
            position=('center', self.height - 100)
        ).set_duration(duration)
        
        # Composite
        video = CompositeVideoClip([background, title_text, subtitle])
        return video
    
    def create_segment_clip(self, text: str, duration: float, bg_path: str = None) -> CompositeVideoClip:
        """Create a video segment with text overlay"""
        if bg_path and os.path.exists(bg_path):
            background = ImageClip(bg_path).set_duration(duration).resize((self.width, self.height))
        else:
            bg_temp = self.create_background()
            background = ImageClip(bg_temp).set_duration(duration)
        
        # Text overlay
        text_clip = self.create_text_clip(text, duration, position='center')
        
        # Add fade effects
        text_clip = text_clip.crossfadein(0.5).crossfadeout(0.5)
        
        video = CompositeVideoClip([background, text_clip])
        return video
    
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
        title_clip = self.create_title_clip(title, duration=3)
        clips.append(title_clip)
        
        # Create segment clips
        for i, segment in enumerate(script_segments):
            if not segment.strip():
                continue
                
            print(f"Processing segment {i+1}/{len(script_segments)}: {segment[:50]}...")
            segment_clip = self.create_segment_clip(
                segment, 
                self.text_duration,
                bg_path=background_image
            )
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
            threads=4
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
