from django.core.management.base import BaseCommand
from cyber_intelligence.services.gnews_service import GNewsService
from cyber_intelligence.services.scraper_service import ScraperService
from cyber_intelligence.services.nist_service import NISTService

class Command(BaseCommand):
    help = 'Fetches Cyber Threat Intelligence data (news, advisories, CVEs) from external APIs and scraping.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting CTI Update Process..."))

        # 1. Fetch from GNews
        self.stdout.write("Fetching cyber news from GNews API...")
        try:
            news_articles = GNewsService.fetch_latest_news()
            self.stdout.write(self.style.SUCCESS(f"Finished GNews API: Cached {len(news_articles)} items."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"GNews API failed: {e}"))

        # 2. Run fallback / additional web scraper
        self.stdout.write("Scraping CISA Cybersecurity Advisories page...")
        try:
            scraped_count = ScraperService.scrape_cyber_advisories()
            self.stdout.write(self.style.SUCCESS(f"Finished Scraper: Cached {scraped_count} new advisory items."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Scraper failed: {e}"))

        # 3. Fetch from NIST NVD API
        self.stdout.write("Fetching recent CVE vulnerabilities from NIST NVD...")
        try:
            cves_count = NISTService.fetch_recent_cves()
            self.stdout.write(self.style.SUCCESS(f"Finished NIST NVD: Cached {cves_count} new CVE items."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"NIST NVD failed: {e}"))

        self.stdout.write(self.style.SUCCESS("Cyber Threat Intelligence database update completed successfully!"))
