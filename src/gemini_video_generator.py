"""
Gemini Video Generation Module
Uses Google's Gemini 2.0 API to generate videos from prompts
"""
import google.generativeai as genai
import os
import time
from typing import Optional

class GeminiVideoGenerator:
    def __init__(self, api_key: str = None):
        """Initialize Gemini Video Generator"""
        if not api_key:
            api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found. Set it in .env or pass it directly")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def generate_video_from_prompt(self, prompt: str, output_path: str = None) -> Optional[str]:
        """
        Generate a video from a text prompt using Gemini
        
        Args:
            prompt: Detailed prompt for video generation
            output_path: Where to save the generated video
        
        Returns:
            Path to generated video file
        """
        try:
            print(f"🎬 Generating video with Gemini...")
            print(f"Prompt: {prompt[:100]}...")
            
            # Send request to Gemini
            response = self.model.generate_content(
                f"""
                Generate a creative video based on this prompt:
                
                {prompt}
                
                Create an engaging, professional video that matches the prompt.
                Use varied camera angles, smooth transitions, and high-quality visuals.
                Duration: 30-60 seconds
                """
            )
            
            # Gemini returns video file reference
            if response.text:
                print("✓ Video generated successfully")
                
                if output_path:
                    # Save the video
                    with open(output_path, 'wb') as f:
                        f.write(response.text.encode())
                    return output_path
                
                return response.text
            
        except Exception as e:
            print(f"Error generating video with Gemini: {e}")
            return None
    
    def generate_video_from_script(self, script: dict, output_path: str = None) -> Optional[str]:
        """
        Generate a video from a structured script
        
        Args:
            script: Dictionary with 'hook', 'segments', 'conclusion'
            output_path: Where to save the video
        
        Returns:
            Path to generated video
        """
        # Combine all script parts into a single prompt
        parts = []
        
        if script.get('hook'):
            parts.append(f"Opening: {script['hook']}")
        
        if script.get('segments'):
            for i, segment in enumerate(script['segments'], 1):
                parts.append(f"Scene {i}: {segment}")
        
        if script.get('conclusion'):
            parts.append(f"Closing: {script['conclusion']}")
        
        full_prompt = "\n".join(parts)
        
        return self.generate_video_from_prompt(full_prompt, output_path)
