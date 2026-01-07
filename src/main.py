"""
AI Video Generator - Main Application
Orchestrates the news-to-video pipeline with both Pillow and Gemini support
"""

# ===== CRITICAL: Load .env FIRST before anything else =====
import os
import sys
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()
print("✓ Environment variables loaded")

# ===== NOW import other modules =====
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from news_scraper import NewsScraper
from script_generator import ScriptGenerator
from video_creator import VideoCreator
import config


class AIVideoGenerator:
    def __init__(self, use_gemini: bool = False):
        self.news_scraper = NewsScraper()
        self.script_generator = ScriptGenerator()
        self.video_creator = VideoCreator()
        self.gemini_video = None  # Initialize as None
        self.use_gemini = False
        
        if use_gemini:
            self._init_gemini()

    def _init_gemini(self) -> bool:
        """Lazily initialize Gemini so menu options can enable it on demand."""
        if self.gemini_video:
            return True
        try:
            import importlib
            gemini_mod = importlib.import_module('gemini_video_generator')

            # Some environments cache an old module without the class; reload defensively
            if not hasattr(gemini_mod, 'GeminiVideoGenerator'):
                gemini_mod = importlib.reload(gemini_mod)

            GeminiVideoGenerator = getattr(gemini_mod, 'GeminiVideoGenerator', None)
            if not GeminiVideoGenerator:
                raise ImportError("GeminiVideoGenerator class not found in gemini_video_generator")

            # Debug info to help when imports get shadowed
            print(f"Gemini module path: {getattr(gemini_mod, '__file__', 'unknown')}")
            print(f"GeminiVideoGenerator resolved: {GeminiVideoGenerator}")

            self.gemini_video = GeminiVideoGenerator()
            self.use_gemini = True
            print("✓ Gemini Video Generation enabled")
            return True
        except ImportError as e:
            print(f"⚠ Gemini module not found: {e}")
            print("  Make sure gemini_video_generator.py exists in src/")
        except ValueError as e:
            print(f"⚠ Gemini API key missing: {e}")
            print("  Add GEMINI_API_KEY to your .env file")
        except Exception as e:
            print(f"⚠ Gemini initialization error: {e}")
        self.use_gemini = False
        self.gemini_video = None
        return False
    
    def generate_video_from_article(self, article_index: int = 0, category: str = None, use_gemini: bool = None):
        """Generate a video from a specific news article"""
        
        # Allow override of gemini setting per call
        use_gemini_now = use_gemini if use_gemini is not None else self.use_gemini
        
        print("=" * 60)
        print("AI VIDEO GENERATOR - News to Video Pipeline")
        if use_gemini_now:
            print("[MODE: Gemini AI Video Generation]")
        else:
            print("[MODE: Pillow + MoviePy]")
        print("=" * 60)
        
        # Step 1: Fetch news article
        print("\n[1/4] Fetching trending news articles...")
        articles = self.news_scraper.get_trending_news(category=category)
        
        if not articles:
            print("Error: No articles found. Please check your NewsAPI key or internet connection.")
            return None
        
        if article_index >= len(articles):
            print(f"Error: Article index {article_index} out of range. Only {len(articles)} articles available.")
            return None
        
        article = articles[article_index]
        print(f"\nSelected Article:")
        print(f"  Title: {article['title']}")
        print(f"  Source: {article['source']}")
        
        # Step 2: Generate script
        print(f"\n[2/4] Generating video script...")
        script = self.script_generator.generate_script(article)
        
        if not script:
            print("Error: Failed to generate script")
            return None
        
        # Save script - use article title for consistent naming (no duplicates)
        safe_title = "".join(c for c in article['title'][:40] if c.isalnum() or c in (' ', '-', '_'))
        safe_title = safe_title.replace(' ', '_')
        script_filename = f"script_{safe_title}.json"
        self.script_generator.save_script(script, script_filename)
        
        print(f"\nGenerated Script Preview:")
        print(f"  Hook: {script.get('hook', 'N/A')[:80]}...")
        print(f"  Segments: {len(script.get('segments', []))}")
        print(f"  Script saved: output/scripts/{script_filename}")
        
        # Step 3: Create video
        print(f"\n[3/4] Creating video...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_filename = f"video_{timestamp}.mp4"
        
        try:
            if use_gemini_now and not self.gemini_video:
                use_gemini_now = self._init_gemini()

            if use_gemini_now and self.gemini_video:
                print("🎬 Using Google Gemini for video generation...")
                video_path = self.gemini_video.generate_video_from_script(
                    script,
                    output_path=os.path.join(config.OUTPUT_VIDEO_DIR, video_filename)
                )
            else:
                if use_gemini_now:
                    print("Error: Gemini not initialized. Falling back to Pillow mode...")
                print("🎬 Using Pillow + MoviePy for video generation...")
                video_path = self.video_creator.create_video(
                    article,
                    script,
                    video_filename
                )
            
            if not video_path:
                print("Error: Video generation failed")
                return None
            
            # Step 4: Done
            print(f"\n[4/4] Video generation complete!")
            print(f"\n{'=' * 60}")
            print("OUTPUT FILES:")
            print(f"  Video: {video_path}")
            print(f"  Script: {os.path.join(config.OUTPUT_SCRIPT_DIR, script_filename)}")
            print(f"{'=' * 60}")
            
            return video_path
            
        except Exception as e:
            print(f"\nError creating video: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_multiple_videos(self, count: int = 3, category: str = None, use_gemini: bool = None):
        """Generate multiple videos from trending articles"""
        use_gemini_now = use_gemini if use_gemini is not None else self.use_gemini
        
        print(f"\nGenerating {count} videos from trending news...")
        if use_gemini_now:
            print("⚠ Using Gemini - this may take longer due to API limits\n")
        
        videos = []
        for i in range(count):
            print(f"\n{'#' * 60}")
            print(f"Processing Article {i+1}/{count}")
            print(f"{'#' * 60}")
            
            video_path = self.generate_video_from_article(
                article_index=i, 
                category=category,
                use_gemini=use_gemini_now
            )
            
            if video_path:
                videos.append(video_path)
            else:
                print(f"Skipping article {i+1} due to errors")
        
        return videos
    
    def list_available_articles(self, category: str = None):
        """List available trending articles"""
        print("\nFetching trending articles...\n")
        articles = self.news_scraper.get_trending_news(category=category)
        
        if not articles:
            print("No articles found.")
            return
        
        print(f"Found {len(articles)} trending articles:\n")
        print("=" * 80)
        for i, article in enumerate(articles):
            print(f"\n[{i}] {article['title']}")
            print(f"  Source: {article['source']}")
            print(f"  URL: {article['url']}")
            if article['description']:
                print(f"  Description: {article['description'][:100]}...")
        print("\n" + "=" * 80)
    
    def print_modes(self):
        """Print available video generation modes"""
        print("\n" + "=" * 60)
        print("AVAILABLE VIDEO GENERATION MODES:")
        print("=" * 60)
        print("\n✓ Pillow + MoviePy Mode (DEFAULT)")
        print("  - Fast frame generation")
        print("  - Professional text overlays")
        print("  - No external API required")
        print("  - Best for: Quick generation, batch processing")
        
        print("\n✓ Google Gemini Mode (PREMIUM)")
        print("  - AI-generated videos")
        print("  - Photorealistic quality")
        print("  - Requires Google API key")
        print("  - Best for: High-quality, realistic videos")
        
        print("\n" + "=" * 60)


def print_usage():
    """Print usage instructions"""
    print("\nAI Video Generator - Usage")
    print("=" * 60)
    print("\nOptions:")
    print("  1. Generate a single video (Pillow mode)")
    print("  2. Generate a single video (Gemini mode)")
    print("  3. Generate multiple videos (Pillow mode)")
    print("  4. Generate multiple videos (Gemini mode)")
    print("  5. List available trending articles")
    print("  6. View available modes")
    print("  7. Exit")
    print("\n" + "=" * 60)


def main():
    """Main application entry point"""
    
    # Check if running from correct directory
    if not os.path.exists('config.py'):
        print("Error: Please run this script from the ai-video-generator directory")
        print("Current directory:", os.getcwd())
        return
    
    # Initialize without Gemini by default
    generator = AIVideoGenerator(use_gemini=False)
    
    # Interactive mode if no arguments
    if len(sys.argv) == 1:
        while True:
            print_usage()
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == '1':
                generator.generate_video_from_article(article_index=0, use_gemini=False)
                input("\nPress Enter to continue...")
                
            elif choice == '2':
                generator.generate_video_from_article(article_index=0, use_gemini=True)
                input("\nPress Enter to continue...")
                
            elif choice == '3':
                try:
                    count = int(input("How many videos to generate? (1-5): ").strip())
                    count = min(max(1, count), 5)
                    generator.generate_multiple_videos(count=count, use_gemini=False)
                except ValueError:
                    print("Invalid input. Please enter a number.")
                input("\nPress Enter to continue...")
                
            elif choice == '4':
                try:
                    count = int(input("How many videos to generate? (1-3): ").strip())
                    count = min(max(1, count), 3)
                    generator.generate_multiple_videos(count=count, use_gemini=True)
                except ValueError:
                    print("Invalid input. Please enter a number.")
                input("\nPress Enter to continue...")
                
            elif choice == '5':
                generator.list_available_articles()
                input("\nPress Enter to continue...")
                
            elif choice == '6':
                generator.print_modes()
                input("\nPress Enter to continue...")
                
            elif choice == '7':
                print("\nGoodbye!")
                break
                
            else:
                print("\nInvalid choice. Please try again.")
    
    else:
        # Command-line mode
        if sys.argv[1] == '--list':
            generator.list_available_articles()
        elif sys.argv[1] == '--generate':
            index = int(sys.argv[2]) if len(sys.argv) > 2 else 0
            use_gemini = '--gemini' in sys.argv
            generator.generate_video_from_article(article_index=index, use_gemini=use_gemini)
        elif sys.argv[1] == '--batch':
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 3
            use_gemini = '--gemini' in sys.argv
            generator.generate_multiple_videos(count=count, use_gemini=use_gemini)
        elif sys.argv[1] == '--modes':
            generator.print_modes()
        else:
            print("Commands:")
            print("  --list                          List available articles")
            print("  --generate [index]              Generate video from article")
            print("  --generate [index] --gemini     Generate with Gemini")
            print("  --batch [count]                 Generate multiple videos")
            print("  --batch [count] --gemini        Generate multiple with Gemini")
            print("  --modes                         Show available modes")


if __name__ == "__main__":
    main()
