"""
AI Video Generator - Main Application
Orchestrates the news-to-video pipeline
"""

import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from news_scraper import NewsScraper
from script_generator import ScriptGenerator
from video_creator import VideoCreator
import config


class AIVideoGenerator:
    def __init__(self):
        self.news_scraper = NewsScraper()
        self.script_generator = ScriptGenerator()
        self.video_creator = VideoCreator()
    
    def generate_video_from_article(self, article_index: int = 0, category: str = None):
        """Generate a video from a specific news article"""
        print("=" * 60)
        print("AI VIDEO GENERATOR - News to Video Pipeline")
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
        
        # Save script
        # Save script - use article title for consistent naming (no duplicates)
        safe_title = "".join(c for c in article['title'][:40] if c.isalnum() or c in (' ', '-', '_'))
        safe_title = safe_title.replace(' ', '_')
        script_filename = f"script_{safe_title}.json"
        self.script_generator.save_script(script, script_filename)

        
        print(f"\nGenerated Script Preview:")
        print(f"  Hook: {script.get('hook', 'N/A')[:80]}...")
        print(f"  Segments: {len(script.get('segments', []))}")
        
        # Step 3: Create video
        print(f"\n[3/4] Creating video...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_filename = f"video_{timestamp}.mp4"
        
        try:
            video_path = self.video_creator.create_video(
                article, 
                script, 
                video_filename
            )
            
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
    
    def generate_multiple_videos(self, count: int = 3, category: str = None):
        """Generate multiple videos from trending articles"""
        print(f"\nGenerating {count} videos from trending news...\n")
        
        videos = []
        for i in range(count):
            print(f"\n{'#' * 60}")
            print(f"Processing Article {i+1}/{count}")
            print(f"{'#' * 60}")
            
            video_path = self.generate_video_from_article(article_index=i, category=category)
            
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
            print(f"    Source: {article['source']}")
            print(f"    URL: {article['url']}")
            if article['description']:
                print(f"    Description: {article['description'][:100]}...")
        
        print("\n" + "=" * 80)


def print_usage():
    """Print usage instructions"""
    print("\nAI Video Generator - Usage")
    print("=" * 60)
    print("\nOptions:")
    print("  1. Generate a single video from the first trending article")
    print("  2. Generate multiple videos (specify count)")
    print("  3. List available trending articles")
    print("  4. Generate video from specific article index")
    print("  5. Exit")
    print("\n" + "=" * 60)


def main():
    """Main application entry point"""
    # Check if running from correct directory
    if not os.path.exists('config.py'):
        print("Error: Please run this script from the ai-video-generator directory")
        print("Current directory:", os.getcwd())
        return
    
    generator = AIVideoGenerator()
    
    # Interactive mode if no arguments
    if len(sys.argv) == 1:
        while True:
            print_usage()
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                generator.generate_video_from_article(article_index=0)
                input("\nPress Enter to continue...")
                
            elif choice == '2':
                try:
                    count = int(input("How many videos to generate? (1-5): ").strip())
                    count = min(max(1, count), 5)
                    generator.generate_multiple_videos(count=count)
                    input("\nPress Enter to continue...")
                except ValueError:
                    print("Invalid input. Please enter a number.")
                    
            elif choice == '3':
                generator.list_available_articles()
                input("\nPress Enter to continue...")
                
            elif choice == '4':
                try:
                    index = int(input("Enter article index: ").strip())
                    generator.generate_video_from_article(article_index=index)
                    input("\nPress Enter to continue...")
                except ValueError:
                    print("Invalid input. Please enter a number.")
                    
            elif choice == '5':
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
            generator.generate_video_from_article(article_index=index)
        elif sys.argv[1] == '--batch':
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 3
            generator.generate_multiple_videos(count=count)
        else:
            print("Unknown command. Use --list, --generate [index], or --batch [count]")


if __name__ == "__main__":
    main()
