import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

# Video Configuration
VIDEO_WIDTH = 1280
VIDEO_HEIGHT = 720
VIDEO_FPS = 24
VIDEO_DURATION = 45  # Target duration in seconds
TEXT_DISPLAY_TIME = 3  # Seconds per text segment

# Font Configuration
FONT_SIZE = 60
FONT_COLOR = 'white'
FONT_FAMILY = 'Arial'

# Output Paths
OUTPUT_VIDEO_DIR = 'output/videos'
OUTPUT_SCRIPT_DIR = 'output/scripts'
ASSETS_DIR = 'assets'

# News Configuration
NEWS_LANGUAGE = 'en'
NEWS_COUNTRY = 'us'
NEWS_CATEGORY = 'technology'  # technology, business, entertainment, general, health, science, sports
MAX_ARTICLES = 5

# AI Model Selection
AI_PROVIDER = os.getenv('AI_PROVIDER', 'openai')  # 'openai' or 'gemini'
