import requests
import logging
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_aware, make_aware
from datetime import datetime
from ..models import Vulnerability

logger = logging.getLogger(__name__)

class NISTService:
    API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"

    @staticmethod
    def fetch_recent_cves():
        """
        Fetches the latest CVEs from the NIST NVD database.
        """
        headers = {}
        api_key = getattr(settings, 'NVD_API_KEY', '')
        if api_key:
            headers['apiKey'] = api_key

        # Fetch top 15 most recent CVEs
        params = {
            'resultsPerPage': 15,
            # We sort by publish date in descending order to get latest CVEs
            # Wait, NVD API v2 does not support direct 'sort' parameter. Instead, it returns latest by default,
            # or we can query with pubStartDate/pubEndDate.
            # But the default order is chronological or modification based. Usually default parameters return latest.
        }

        try:
            logger.info("Fetching CVEs from NIST NVD API...")
            response = requests.get(NISTService.API_URL, headers=headers, params=params, timeout=12)
            response.raise_for_status()
            
            data = response.json()
            vulns = data.get('vulnerabilities', [])
            
            saved_count = 0
            for item in vulns:
                cve = item.get('cve', {})
                cve_id = cve.get('id')
                if not cve_id:
                    continue
                
                # Extract description
                descriptions = cve.get('descriptions', [])
                description = ""
                for desc in descriptions:
                    if desc.get('lang') == 'en':
                        description = desc.get('value')
                        break
                if not description and descriptions:
                    description = descriptions[0].get('value', '')
                
                # Extract severity (look for CVSS v3.1, v3.0, then v2 metrics)
                severity = 'UNKNOWN'
                metrics = cve.get('metrics', {})
                cvss_metrics = metrics.get('cvssMetricV31') or metrics.get('cvssMetricV30')
                if cvss_metrics:
                    severity = cvss_metrics[0].get('cvssData', {}).get('baseSeverity', 'UNKNOWN')
                else:
                    cvss_v2 = metrics.get('cvssMetricV2')
                    if cvss_v2:
                        severity = cvss_v2[0].get('baseSeverity', 'UNKNOWN')
                
                # Extract published date
                published_str = cve.get('published')
                published_date = parse_datetime(published_str) if published_str else datetime.now()
                if published_date and not is_aware(published_date):
                    published_date = make_aware(published_date)
                
                # Extract reference url
                references = cve.get('references', [])
                ref_url = f"https://nvd.nist.gov/vuln/detail/{cve_id}"
                if references:
                    ref_url = references[0].get('url', ref_url)
                
                # Save to database
                vuln, created = Vulnerability.objects.update_or_create(
                    cve_id=cve_id,
                    defaults={
                        'description': description,
                        'severity': severity.upper(),
                        'published_date': published_date,
                        'reference_url': ref_url
                    }
                )
                if created:
                    saved_count += 1
            
            logger.info(f"NIST NVD: Fetched and saved {saved_count} new CVEs.")
            return saved_count
        except Exception as e:
            logger.error(f"NIST NVD API fetch failed: {e}")
            return 0
