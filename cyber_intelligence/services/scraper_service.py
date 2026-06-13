import requests
from bs4 import BeautifulSoup
import logging
import time
from datetime import datetime
from django.utils.timezone import make_aware
from ..models import CyberNews

logger = logging.getLogger(__name__)

class ScraperService:
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }

    @staticmethod
    def scrape_cyber_advisories():
        """
        Scrapes threat advisories from CISA Cybersecurity Advisories page.
        """
        url = "https://www.cisa.gov/news-events/cybersecurity-advisories"
        
        try:
            logger.info(f"Starting scraper for: {url}")
            response = requests.get(url, headers=ScraperService.HEADERS, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # The structure of CISA news page:
            # Advisories are typically in view-content list, each having a heading, date, description.
            advisory_items = soup.find_all('div', class_='c-view-teaser') or soup.find_all('article')
            
            saved_count = 0
            
            for item in advisory_items[:10]:  # Scrape top 10 items
                title_el = item.find('h3') or item.find('h2') or item.find('a')
                if not title_el:
                    continue
                
                title = title_el.get_text(strip=True)
                link_el = title_el.find('a') if hasattr(title_el, 'find') else None
                if not link_el:
                    link_el = item.find('a')
                    
                if not link_el or not link_el.get('href'):
                    continue
                    
                article_url = link_el.get('href')
                if not article_url.startswith('http'):
                    article_url = "https://www.cisa.gov" + article_url
                
                # Extract description
                desc_el = item.find('div', class_='c-view-teaser__summary') or item.find('p')
                description = desc_el.get_text(strip=True) if desc_el else "No summary available."
                
                # Extract date or use current date
                date_el = item.find('time') or item.find('span', class_='c-view-teaser__date')
                published_date = datetime.now()
                if date_el and date_el.get('datetime'):
                    try:
                        published_date = datetime.fromisoformat(date_el.get('datetime').replace('Z', '+00:00'))
                    except Exception:
                        pass
                
                # Save to db
                news_item, created = CyberNews.objects.update_or_create(
                    article_url=article_url,
                    defaults={
                        'title': title[:255],
                        'description': description,
                        'source': 'CISA Advisories'[:100],
                        'published_date': make_aware(published_date) if not published_date.tzinfo else published_date,
                        'image_url': ''
                    }
                )
                if created:
                    saved_count += 1
                
                # Polite scraping rate limit (sleep 0.5s per item processed)
                time.sleep(0.5)
                
            logger.info(f"CISA Scraper finished. Saved {saved_count} new advisories.")
            return saved_count
        except Exception as e:
            logger.error(f"Scraper error: {e}")
            return 0
