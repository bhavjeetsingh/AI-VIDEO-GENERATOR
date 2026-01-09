"""
Gemini Video Generation Module
Uses Google's Gemini 2.0 API to generate videos from prompts
"""

import google.generativeai as genai
import os
from typing import Optional, List

class GeminiVideoGenerator:
    def __init__(self, api_key: str = None):
        """Initialize Gemini Video Generator"""
        if not api_key:
            api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found. Set it in .env or pass it directly")
        
        # Configure client (library defaults to current API)
        genai.configure(api_key=api_key)

        # Start with discovered models if list_models is available, then fall back to defaults
        discovered = self._discover_available_models()
        fallback_models = [
            'gemini-1.5-pro',
            'gemini-1.5-flash',
            'gemini-pro-vision',
            'gemini-1.0-pro-latest',
            'gemini-1.0-pro',
            'gemini-1.5-flash-latest',
            'gemini-pro',
            'models/gemini-1.5-pro',
            'models/gemini-1.5-flash',
            'models/gemini-pro',
        ]
        self.model_names: List[str] = discovered + [m for m in fallback_models if m not in discovered]
        self.model = self._first_available_model()

    def _discover_available_models(self) -> List[str]:
        names: List[str] = []
        try:
            models = genai.list_models()
            for m in models:
                methods = getattr(m, 'supported_generation_methods', []) or []
                if 'generateContent' in methods or 'generate_content' in methods:
                    names.append(m.name)
        except Exception as e:
            print(f"Warning: Unable to list Gemini models automatically: {e}")
        return names

    def _first_available_model(self):
        for name in self.model_names:
            try:
                return genai.GenerativeModel(name)
            except Exception:
                continue
        print("No Gemini models available from the configured account")
        return None
    
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
            if not self.model:
                print("Gemini model unavailable; aborting Gemini generation")
                return None

            response = self.model.generate_content(
                f"Create a professional video based on this prompt:\n\n{prompt}\n\n"
                "Duration: 30-60 seconds. High quality visuals."
            )
            
            # Gemini returns video file reference
            if response and response.text:
                print("✓ Video generated successfully")
                
                if output_path:
                    # Ensure output directory exists before writing
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    return output_path
                
                return response.text
            
        except Exception as e:
            print(f"Error generating video with Gemini: {e}")

            # Try alternate models if the current one fails (e.g., 404)
            for name in self.model_names:
                try:
                    alt_model = genai.GenerativeModel(name)
                    response = alt_model.generate_content(
                        f"Create a professional video based on this prompt:\n\n{prompt}\n\n"
                        "Duration: 30-60 seconds. High quality visuals."
                    )
                    if response and response.text:
                        print(f"✓ Video generated successfully with model {name}")
                        self.model = alt_model
                        if output_path:
                            with open(output_path, 'w', encoding='utf-8') as f:
                                f.write(response.text)
                            return output_path
                        return response.text
                except Exception as e_alt:
                    print(f"Gemini model '{name}' failed: {e_alt}")
                    continue
            print("All Gemini models failed; returning None")
            return None
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
