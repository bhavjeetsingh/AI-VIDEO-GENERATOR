"""
Script Generator Module
Generates video scripts from news articles using OpenAI or Google Gemini
"""

from typing import Dict, List
import config
import json
import os


class ScriptGenerator:
    def __init__(self):
        self.ai_provider = (config.AI_PROVIDER or '').lower()
        self.client = None
        self._gemini_models = self._discover_gemini_models()

        if self.ai_provider == 'openai':
            self._init_openai_client()
            if not self.client and config.GEMINI_API_KEY:
                # Gracefully fall back to Gemini if OpenAI initialization fails
                print("OpenAI unavailable, falling back to Gemini")
                self.ai_provider = 'gemini'
                self._init_gemini_client()
        elif self.ai_provider == 'gemini':
            self._init_gemini_client()
        else:
            self.client = None
            print("Invalid AI provider specified")

    def _init_openai_client(self):
        """Initialize OpenAI client, handling common proxy/version issues."""
        if not config.OPENAI_API_KEY:
            print("OpenAI API key missing; skipping OpenAI initialization")
            return
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        except TypeError as e:
            # Some older OpenAI client versions do not accept proxy arguments
            if 'proxies' in str(e):
                print("OpenAI client error: installed version does not support proxy arguments. "
                      "Upgrade 'openai' to >=1.0 or remove OPENAI_PROXY/HTTPS_PROXY settings.")
            else:
                print(f"Error initializing OpenAI: {e}")
            self.client = None
        except Exception as e:
            print(f"Error initializing OpenAI: {e}")
            self.client = None

    def _init_gemini_client(self):
        """Initialize Gemini client if a key is present."""
        if not config.GEMINI_API_KEY:
            print("Gemini API key missing; skipping Gemini initialization")
            return
        try:
            import google.generativeai as genai
            # Use default API settings; model name must be available to your account
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.client = self._first_available_gemini_model(genai)
        except Exception as e:
            print(f"Error initializing Gemini: {e}")
            self.client = None

    def _discover_gemini_models(self) -> List[str]:
        """Attempt to fetch available Gemini models and merge with fallbacks."""
        preferred = [
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

        names: List[str] = []
        try:
            import google.generativeai as genai
            models = genai.list_models()
            for m in models:
                methods = getattr(m, 'supported_generation_methods', []) or []
                if 'generateContent' in methods or 'generate_content' in methods:
                    names.append(m.name)
        except Exception as e:
            print(f"Warning: Unable to list Gemini models automatically: {e}")

        # Merge discovered with preferred fallbacks
        return names + [m for m in preferred if m not in names]

    def _first_available_gemini_model(self, genai):
        """Pick the first Gemini model that can be constructed."""
        for name in self._gemini_models:
            try:
                return genai.GenerativeModel(name)
            except Exception:
                continue
        print("No Gemini models available from the configured account")
        return None
    
    def generate_script_openai(self, article: Dict) -> Dict:
        """Generate script using OpenAI GPT"""
        prompt = f"""Create an engaging 30-60 second video script for this news article.
        
Title: {article['title']}
Description: {article['description']}
Source: {article['source']}

Requirements:
1. Break the script into 4-6 short, punchy segments
2. Each segment should be 1-2 sentences (8-12 words max)
3. Make it engaging and suitable for social media
4. Start with a hook to grab attention
5. End with a call-to-action or thought-provoking statement

Format the response as JSON with this structure:
{{
    "hook": "attention-grabbing opening",
    "segments": ["segment 1", "segment 2", "segment 3", "segment 4"],
    "conclusion": "closing statement or CTA"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a creative social media content writer specializing in short-form video scripts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            script_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                # Remove markdown code blocks if present
                if script_text.startswith("```"):
                    script_text = script_text.split("```")[1]
                    if script_text.startswith("json"):
                        script_text = script_text[4:]
                script_text = script_text.strip()
                
                script_data = json.loads(script_text)
                return script_data
            except json.JSONDecodeError:
                # Fallback: create manual structure
                return self._fallback_script(article)
                
        except Exception as e:
            print(f"Error generating script with OpenAI: {e}")
            return self._fallback_script(article)
    
    def generate_script_gemini(self, article: Dict) -> Dict:
        """Generate script using Google Gemini"""
        prompt = f"""Create an engaging 30-60 second video script for this news article.
        
Title: {article['title']}
Description: {article['description']}
Source: {article['source']}

Requirements:
1. Break the script into 4-6 short, punchy segments
2. Each segment should be 1-2 sentences (8-12 words max)
3. Make it engaging and suitable for social media
4. Start with a hook to grab attention
5. End with a call-to-action or thought-provoking statement

Format the response as JSON with this structure:
{{
    "hook": "attention-grabbing opening",
    "segments": ["segment 1", "segment 2", "segment 3", "segment 4"],
    "conclusion": "closing statement or CTA"
}}
"""
        
        if not self.client:
            print("Gemini client not initialized; using fallback script")
            return self._fallback_script(article)

        # Try each configured model until one works
        try_models = [getattr(self.client, 'model_name', None)] + self._gemini_models
        seen = set()

        for model_name in filter(None, try_models):
            if model_name in seen:
                continue
            seen.add(model_name)
            try:
                import google.generativeai as genai
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                script_text = response.text.strip()

                # Try to parse JSON response
                try:
                    if script_text.startswith("```"):
                        script_text = script_text.split("```")[1]
                        if script_text.startswith("json"):
                            script_text = script_text[4:]
                    script_text = script_text.strip()
                    script_data = json.loads(script_text)
                    self.client = model
                    return script_data
                except json.JSONDecodeError:
                    return self._fallback_script(article)
            except Exception as e:
                print(f"Gemini model '{model_name}' failed: {e}")
                continue

        print("All Gemini models failed; using fallback script")
        return self._fallback_script(article)
    
    def _fallback_script(self, article: Dict) -> Dict:
        """Create a simple fallback script structure"""
        title = article['title']
        description = article['description'] or "Breaking news story"
        
        return {
            "hook": title[:80],
            "segments": [
                description[:100],
                f"This story from {article['source']}",
                "What are your thoughts?",
                "Follow for more updates!"
            ],
            "conclusion": "Stay informed!"
        }
    
    def generate_script(self, article: Dict) -> Dict:
        """Generate a video script from an article"""
        if not self.client:
            print("No AI provider configured, using fallback script")
            return self._fallback_script(article)
        
        print(f"Generating script using {self.ai_provider}...")
        
        if self.ai_provider == 'openai':
            return self.generate_script_openai(article)
        elif self.ai_provider == 'gemini':
            return self.generate_script_gemini(article)
        else:
            return self._fallback_script(article)
    
    def get_script_segments(self, script: Dict) -> List[str]:
        """Get all script segments in order"""
        segments = []
        segments.append(script.get('hook', ''))
        segments.extend(script.get('segments', []))
        segments.append(script.get('conclusion', ''))
        return [s for s in segments if s]  # Filter out empty segments
    
    def save_script(self, script: Dict, filename: str):
        """Save script to JSON file"""
        os.makedirs(config.OUTPUT_SCRIPT_DIR, exist_ok=True)
        filepath = os.path.join(config.OUTPUT_SCRIPT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(script, f, indent=2, ensure_ascii=False)
        
        print(f"Script saved to {filepath}")


if __name__ == "__main__":
    # Test the script generator
    test_article = {
        'title': 'New AI Technology Revolutionizes Video Creation',
        'description': 'Researchers have developed a groundbreaking AI system that can automatically generate professional videos from text descriptions.',
        'source': 'Tech News',
        'url': 'https://example.com',
        'published_at': '2024-01-01',
        'image_url': ''
    }
    
    generator = ScriptGenerator()
    script = generator.generate_script(test_article)
    
    print("\n=== Generated Script ===")
    print(json.dumps(script, indent=2))
