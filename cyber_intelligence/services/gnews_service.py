import requests
import logging
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_aware, make_aware
from datetime import datetime
from ..models import CyberNews

logger = logging.getLogger(__name__)

class GNewsService:
    @staticmethod
    def fetch_latest_news():
        api_key = getattr(settings, 'GNEWS_API_KEY', '')
        if not api_key:
            logger.warning("GNews API Key is missing. Skipping API fetch.")
            return []

        # Combining keywords using OR operator for a single efficient API call
        query = '"cyber attack" OR "phishing" OR "ransomware" OR "online fraud" OR "data breach"'
        url = "https://gnews.io/api/v4/search"
        params = {
            'q': query,
            'lang': 'en',
            'token': api_key,
            'max': 10,  # Max articles to fetch
            'sortby': 'publishedAt'
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            articles = data.get('articles', [])
            
            saved_count = 0
            for art in articles:
                # Parse datetime
                pub_date_str = art.get('publishedAt')
                pub_date = parse_datetime(pub_date_str) if pub_date_str else datetime.now()
                if pub_date and not is_aware(pub_date):
                    pub_date = make_aware(pub_date)

                # Check for duplicates using the article URL
                news_item, created = CyberNews.objects.update_or_create(
                    article_url=art.get('url'),
                    defaults={
                        'title': art.get('title')[:255],
                        'description': art.get('description', ''),
                        'image_url': art.get('image', ''),
                        'source': art.get('source', {}).get('name', 'GNews')[:100],
                        'published_date': pub_date
                    }
                )
                if created:
                    saved_count += 1
            
            logger.info(f"GNews: Fetched and saved {saved_count} new articles.")
            return articles
        except Exception as e:
            logger.error(f"GNews API request failed: {e}")
            return []
