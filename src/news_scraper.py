"""
News Scraper Module
Fetches trending news articles from NewsAPI (API key required)
"""

import requests
from typing import List, Dict, Optional
import sys
from pathlib import Path
# ...existing code...
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import config
# ...existing code...


class NewsScraper:
    def __init__(self):
        self.newsapi_key = config.NEWSAPI_KEY
        self.newsapi_url = "https://newsapi.org/v2/top-headlines"
        
        # Validate API key
        if not self.newsapi_key:
            raise ValueError("NewsAPI key is required. Please set NEWSAPI_KEY in your .env file.")
        
    def fetch_newsapi_articles(self, category: str = None, country: str = None) -> List[Dict]:
        """Fetch articles from NewsAPI"""
        
        params = {
            'apiKey': self.newsapi_key,
            'language': config.NEWS_LANGUAGE,
            'category': category or config.NEWS_CATEGORY,
            'country': country or config.NEWS_COUNTRY,
            'pageSize': config.MAX_ARTICLES
        }
        
        try:
            response = requests.get(self.newsapi_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ok':
                articles = []
                for article in data.get('articles', [])[:config.MAX_ARTICLES]:
                    articles.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'url': article.get('url', ''),
                        'published_at': article.get('publishedAt', ''),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'image_url': article.get('urlToImage', '')
                    })
                return articles
            else:
                print(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return []
                
        except Exception as e:
            print(f"Error fetching from NewsAPI: {e}")
            return []
    
    
    def get_trending_news(self, category: str = None) -> List[Dict]:
        """Get trending news articles from NewsAPI"""
        print("Fetching trending news articles...")
        
        articles = self.fetch_newsapi_articles(category=category)
        
        if articles:
            print(f"Successfully fetched {len(articles)} articles")
        else:
            raise Exception("Failed to fetch articles from NewsAPI. Please check your API key and internet connection.")
            
        return articles
    
    def get_article_by_index(self, index: int = 0, category: str = None) -> Optional[Dict]:
        """Get a specific article by index"""
        articles = self.get_trending_news(category=category)
        
        if articles and 0 <= index < len(articles):
            return articles[index]
        
        return None


if __name__ == "__main__":
    # Test the scraper
    scraper = NewsScraper()
    articles = scraper.get_trending_news()
    
    if articles:
        print("\n=== Sample Articles ===")
        for i, article in enumerate(articles[:3], 1):
            print(f"\n{i}. {article['title']}")
            print(f"   Source: {article['source']}")
            print(f"   URL: {article['url']}")
