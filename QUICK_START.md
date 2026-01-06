# QUICK START GUIDE

## AI Video Generator - Get Started in 5 Minutes

### Prerequisites
- Python 3.8 or higher installed
- Internet connection

### Option 1: Automated Setup (Windows)

1. Open the project folder
2. Double-click `setup.bat`
3. Follow the prompts
4. Edit `.env` file with your API keys (optional - can use RSS feeds)
5. Run the application

### Option 2: Manual Setup

```bash
# 1. Navigate to project
cd ai-video-generator

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
copy .env.example .env

# 4. (Optional) Edit .env with your API keys
notepad .env

# 5. Run the application
cd src
python main.py
```

### First Run (No API Keys)

The tool works WITHOUT API keys using:
- RSS feeds for news (instead of NewsAPI)
- Fallback scripts (instead of AI-generated scripts)

```bash
cd src
python main.py --list
```

This will fetch and display trending news from RSS feeds.

### Generate Your First Video (Without API Keys)

```bash
cd src
python main.py --generate
```

The tool will:
1. Fetch news from RSS feeds
2. Create a basic script (no AI needed)
3. Generate a video with text overlays
4. Save to `output/videos/`

### With API Keys (Recommended)

For AI-generated scripts, add to `.env`:

```
# Get free key at: https://newsapi.org
NEWSAPI_KEY=your_key_here

# Choose ONE of these:
OPENAI_API_KEY=your_key_here
# OR
GEMINI_API_KEY=your_key_here

# Set provider
AI_PROVIDER=openai
```

Then run:
```bash
cd src
python main.py --generate
```

### Interactive Menu

For an interactive experience:
```bash
cd src
python main.py
```

Menu options:
1. Generate single video
2. Batch generate videos
3. List articles
4. Select specific article
5. Exit

### Sample Commands

```bash
# List trending articles
python main.py --list

# Generate 1 video from first article
python main.py --generate

# Generate video from 3rd article
python main.py --generate 2

# Batch generate 3 videos
python main.py --batch 3
```

### Output Location

- **Videos**: `ai-video-generator/output/videos/video_TIMESTAMP.mp4`
- **Scripts**: `ai-video-generator/output/scripts/script_TIMESTAMP.json`

### Customization

Edit `config.py` to change:
- Video resolution (default: 1280x720)
- Text duration (default: 3 seconds per segment)
- News category (technology, business, sports, etc.)
- Font size and color

### Troubleshooting

**"No module named 'moviepy'"**
```bash
pip install -r requirements.txt
```

**"No articles found"**
- Check internet connection
- RSS feeds are automatically used as fallback

**"Error generating script"**
- Either add API keys to `.env`
- Or use fallback mode (automatic, no configuration needed)

### Video Specifications

- **Format**: MP4 (H.264)
- **Resolution**: 1280x720 (720p)
- **Frame Rate**: 24 fps
- **Duration**: 30-60 seconds
- **Audio**: None (text-based)
- **File Size**: 1-3 MB per video

### Need Help?

1. Check `README.md` for detailed documentation
2. Check `IMPLEMENTATION_REPORT.md` for technical details
3. Verify Python version: `python --version`
4. Verify dependencies: `pip list`

### Quick Demo

Want to test immediately? Run this:

```bash
cd ai-video-generator
pip install -r requirements.txt
cd src
python news_scraper.py
```

This will test the news scraper and show you available articles.

---

**That's it! You're ready to generate AI videos from trending news!** ???
