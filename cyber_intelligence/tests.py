from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import CyberNews, Vulnerability, WebsiteScan

class CyberIntelligenceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        
        # Create dummy news
        self.news = CyberNews.objects.create(
            title="Test Attack",
            description="Test description",
            source="Test Source",
            article_url="http://testattack.local",
            published_date="2026-06-13T10:00:00Z"
        )
        
        # Create dummy vulnerability
        self.vuln = Vulnerability.objects.create(
            cve_id="CVE-2026-99999",
            description="Test vuln",
            severity="HIGH",
            published_date="2026-06-13T10:00:00Z",
            reference_url="http://cve.local"
        )

    def test_dashboard_redirects_for_anonymous(self):
        """
        Dashboard should redirect to login page for anonymous users.
        """
        response = self.client.get(reverse('cyber_intelligence:cyber_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_dashboard_accessible_for_authenticated(self):
        """
        Dashboard should load successfully for logged-in users.
        """
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('cyber_intelligence:cyber_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cyber_intelligence/cyber_dashboard.html')
        self.assertContains(response, "Test Attack")
        self.assertContains(response, "CVE-2026-99999")

    def test_url_scan_api_rejects_anonymous(self):
        """
        URL Scan API endpoint should redirect or reject anonymous POST requests.
        """
        response = self.client.post(reverse('cyber_intelligence:url_scan_api'), {'url': 'http://google.com'})
        self.assertEqual(response.status_code, 302)

    def test_url_scan_api_handles_safe_url(self):
        """
        Scan endpoint should analyze a valid URL and return scan results.
        """
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('cyber_intelligence:url_scan_api'), {'url': 'http://safe-site.com'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['url'], 'http://safe-site.com')
        self.assertIn('result', data)
        self.assertIn('risk_score', data)
        
        # Verify it stored in DB
        self.assertTrue(WebsiteScan.objects.filter(url='http://safe-site.com').exists())

    def test_url_scan_api_handles_malicious_heuristics(self):
        """
        Scan endpoint should flag URLs containing suspicious keywords as Suspicious.
        """
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('cyber_intelligence:url_scan_api'), {'url': 'http://secure-login-paypal.com'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['result'], 'SUSPICIOUS')
        self.assertGreater(data['risk_score'], 0)
        self.assertIn("Suspicious word: 'login'", data['reasons'])

    def test_custom_date_formatting(self):
        """
        Verify that CyberNews formatted_published_date formats dates as requested:
        - 12:00 UTC should output 'noon'
        - 00:00 UTC should output 'midnight'
        - 09:48 UTC should output '9:48 a.m.'
        - 15:30 UTC should output '3:30 p.m.'
        """
        from datetime import datetime, timezone
        
        # Test case for noon
        news_noon = CyberNews(
            title="Noon test",
            article_url="http://noon.local",
            published_date=datetime(2026, 6, 12, 12, 0, 0, tzinfo=timezone.utc)
        )
        self.assertEqual(news_noon.formatted_published_date, "June 12, 2026, noon")

        # Test case for midnight
        news_midnight = CyberNews(
            title="Midnight test",
            article_url="http://midnight.local",
            published_date=datetime(2026, 6, 12, 0, 0, 0, tzinfo=timezone.utc)
        )
        self.assertEqual(news_midnight.formatted_published_date, "June 12, 2026, midnight")

        # Test case for 9:48 a.m.
        news_am = CyberNews(
            title="AM test",
            article_url="http://am.local",
            published_date=datetime(2026, 6, 13, 9, 48, 0, tzinfo=timezone.utc)
        )
        self.assertEqual(news_am.formatted_published_date, "June 13, 2026, 9:48 a.m.")

        # Test case for 3:30 p.m.
        news_pm = CyberNews(
            title="PM test",
            article_url="http://pm.local",
            published_date=datetime(2026, 6, 13, 15, 30, 0, tzinfo=timezone.utc)
        )
        self.assertEqual(news_pm.formatted_published_date, "June 13, 2026, 3:30 p.m.")

