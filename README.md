# AI Video Generator - Trending News to Video

An AI-powered application that automatically scrapes trending news articles, generates engaging video scripts, and creates 30-60 second social media videos with text overlays.

## ?? Features

- **Automated News Scraping**: Fetches trending news from NewsAPI or RSS feeds
- **AI Script Generation**: Uses OpenAI GPT or Google Gemini to create engaging video scripts
- **Video Creation**: Generates professional videos with text overlays and fade effects
- **Multiple News Categories**: Technology, Business, Entertainment, Health, Science, Sports
- **Batch Processing**: Generate multiple videos at once
- **Customizable**: Configure video resolution, duration, fonts, and colors

## ?? Requirements

- Python 3.8 or higher
- API Keys (at least one):
  - NewsAPI (optional, has RSS fallback)
  - OpenAI API OR Google Gemini API

## ?? Installation

### 1. Clone or Download the Project

```bash
cd ai-video-generator
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Copy the example environment file:

```bash
copy .env.example .env
```

Edit `.env` and add your API keys:

```
NEWSAPI_KEY=your_newsapi_key_here
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
AI_PROVIDER=openai
```

#### Getting API Keys:

- **NewsAPI**: Sign up at [newsapi.org](https://newsapi.org/) (Free tier: 100 requests/day)
- **OpenAI**: Get your key at [platform.openai.com](https://platform.openai.com/api-keys)
- **Google Gemini**: Get your key at [makersuite.google.com](https://makersuite.google.com/app/apikey)

**Note**: The tool can work without NewsAPI (uses RSS feeds as fallback), but you need either OpenAI or Gemini for script generation.

## ?? Usage

### Interactive Mode

Run the application without arguments for interactive menu:

```bash
cd src
python main.py
```

Menu options:
1. Generate a single video from the first trending article
2. Generate multiple videos (batch mode)
3. List available trending articles
4. Generate video from specific article index
5. Exit

### Command-Line Mode

**List trending articles:**
```bash
python src/main.py --list
```

**Generate video from first article:**
```bash
python src/main.py --generate
```

**Generate video from specific article (by index):**
```bash
python src/main.py --generate 2
```

**Generate multiple videos (batch):**
```bash
python src/main.py --batch 3
```

## ?? Project Structure

```
ai-video-generator/
+-- src/
¦   +-- main.py              # Main application
¦   +-- news_scraper.py      # News fetching module
¦   +-- script_generator.py  # AI script generation
¦   +-- video_creator.py     # Video creation module
+-- output/
¦   +-- videos/              # Generated videos (.mp4)
¦   +-- scripts/             # Generated scripts (.json)
+-- assets/
¦   +-- background.jpg       # Default background image
+-- config.py                # Configuration settings
+-- requirements.txt         # Python dependencies
+-- .env.example            # Environment variables template
+-- README.md               # This file
```

## ?? Configuration

Edit `config.py` to customize:

### Video Settings
- `VIDEO_WIDTH`: Default 1280
- `VIDEO_HEIGHT`: Default 720
- `VIDEO_FPS`: Default 24
- `VIDEO_DURATION`: Target duration (45 seconds)
- `TEXT_DISPLAY_TIME`: Seconds per segment (3 seconds)

### News Settings
- `NEWS_CATEGORY`: technology, business, entertainment, general, health, science, sports
- `NEWS_COUNTRY`: 'us' (2-letter country code)
- `NEWS_LANGUAGE`: 'en'
- `MAX_ARTICLES`: Number of articles to fetch (5)

### Font Settings
- `FONT_SIZE`: Default 60
- `FONT_COLOR`: 'white'
- `FONT_FAMILY`: 'Arial'

## ?? Output

The application generates:

1. **Video Files** (`output/videos/`): MP4 videos (720p, 24fps)
   - Title screen with article headline
   - Multiple text segments with fade effects
   - 30-60 second duration

2. **Script Files** (`output/scripts/`): JSON files containing:
   - Hook (attention-grabbing opening)
   - Segments (main content)
   - Conclusion (call-to-action)

## ?? Troubleshooting

### "No articles found"
- Check your NewsAPI key in `.env`
- Verify internet connection
- The tool will automatically fall back to RSS feeds

### "Error generating script"
- Verify OpenAI or Gemini API key in `.env`
- Check API credit balance
- Ensure `AI_PROVIDER` in `.env` matches your API key

### "MoviePy errors"
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- On Windows, you may need to install ImageMagick separately
- Try running: `pip install --upgrade moviepy`

### Font errors
- The tool will automatically fall back to default fonts
- On Windows, Arial is usually available
- You can specify different fonts in `config.py`

## ?? Examples

### Example 1: Quick Single Video
```bash
cd src
python main.py --generate
```

### Example 2: Batch Generate 3 Videos
```bash
python src/main.py --batch 3
```

### Example 3: Interactive Selection
```bash
python src/main.py
# Choose option 3 to list articles
# Choose option 4 to select specific article
```

## ?? Pipeline Overview

1. **News Scraping**: Fetch trending articles from NewsAPI or RSS feeds
2. **Script Generation**: AI generates engaging 30-60 second script
3. **Video Creation**: Assemble video with text overlays and effects
4. **Output**: Save video (MP4) and script (JSON)

## ?? API Limits

- **NewsAPI Free**: 100 requests/day
- **OpenAI**: Pay-per-use (typically $0.002 per request for GPT-3.5)
- **Google Gemini**: Free tier available with rate limits

## ?? Contributing

Feel free to fork, modify, and improve this project!

## ?? License

This project is provided as-is for educational purposes.

## ?? Credits

- NewsAPI for news data
- OpenAI/Google Gemini for AI capabilities
- MoviePy for video processing
- Pillow for image processing

## ?? Support

For issues or questions:
1. Check the Troubleshooting section above
2. Verify all API keys are configured correctly
3. Ensure all dependencies are installed
4. Check that Python 3.8+ is installed

---

**Note**: This tool is designed for educational purposes. Ensure you have the right to use and distribute any news content in your videos.
