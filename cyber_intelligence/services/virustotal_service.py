import requests
import logging
import base64
from django.conf import settings

logger = logging.getLogger(__name__)

class VirusTotalService:
    @staticmethod
    def check_url(url):
        """
        Scans/retrieves reputation for a URL using the VirusTotal v3 API.
        """
        api_key = getattr(settings, 'VIRUSTOTAL_API_KEY', '')
        if not api_key:
            logger.warning("VirusTotal API key is not configured.")
            return {
                'in_database': False,
                'result': 'UNKNOWN',
                'risk_score': 0,
                'source': 'VirusTotal (API Key Missing)'
            }

        # URL identifier format: base64 encoded URL without padding
        try:
            url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
            endpoint = f"https://www.virustotal.com/api/v3/urls/{url_id}"
            headers = {
                "x-apikey": api_key,
                "Accept": "application/json"
            }
            
            logger.info(f"Checking URL on VirusTotal: {url} (ID: {url_id})")
            response = requests.get(endpoint, headers=headers, timeout=10)
            
            if response.status_code == 404:
                # URL is not in VirusTotal database, submit it for scanning
                logger.info(f"URL {url} not found in VirusTotal database. Requesting scan...")
                scan_url = "https://www.virustotal.com/api/v3/urls"
                scan_response = requests.post(scan_url, headers=headers, data={"url": url}, timeout=10)
                if scan_response.status_code == 200:
                    return {
                        'in_database': False,
                        'result': 'SAFE',
                        'risk_score': 10,
                        'source': 'VirusTotal (Scan Submitted)'
                    }
            
            response.raise_for_status()
            res_data = response.json()
            
            attributes = res_data.get('data', {}).get('attributes', {})
            stats = attributes.get('last_analysis_stats', {})
            
            malicious = stats.get('malicious', 0)
            suspicious = stats.get('suspicious', 0)
            harmless = stats.get('harmless', 0)
            undetected = stats.get('undetected', 0)
            
            total_engines = malicious + suspicious + harmless + undetected
            
            if total_engines == 0:
                return {
                    'in_database': True,
                    'result': 'SAFE',
                    'risk_score': 0,
                    'source': 'VirusTotal (No Analysis)'
                }
            
            # Risk score is percentage of engines flag it as malicious or suspicious
            detected_engines = malicious + suspicious
            risk_score = int((detected_engines / total_engines) * 100)
            
            if malicious >= 3:
                result = 'PHISHING'
            elif malicious > 0 or suspicious > 0:
                result = 'SUSPICIOUS'
            else:
                result = 'SAFE'
                
            return {
                'in_database': True,
                'result': result,
                'risk_score': risk_score,
                'source': f"VirusTotal ({malicious}/{total_engines} engines flagged)"
            }
            
        except Exception as e:
            logger.error(f"VirusTotal API lookup failed: {e}")
            return {
                'in_database': False,
                'result': 'UNKNOWN',
                'risk_score': 0,
                'source': 'VirusTotal API Error'
            }
