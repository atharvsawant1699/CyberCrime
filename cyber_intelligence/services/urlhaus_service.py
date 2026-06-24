import requests
import logging

logger = logging.getLogger(__name__)

class URLhausService:
    API_URL = "https://urlhaus-api.abuse.ch/v1/url/"

    @staticmethod
    def check_url(url):
        """
        Checks a URL against URLhaus database to detect malware-distributing websites.
        """
        data = {
            'url': url
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        try:
            logger.info(f"Checking URL against URLhaus: {url}")
            response = requests.post(URLhausService.API_URL, json=data, headers=headers, timeout=8)

            response.raise_for_status()
            
            result_data = response.json()
            query_status = result_data.get('query_status')
            
            if query_status == 'ok':
                url_status = result_data.get('url_status', 'offline')
                threat = result_data.get('threat', 'unknown')
                
                # Active malware urls are extremely high risk
                risk_score = 99 if url_status == 'online' else 70
                
                return {
                    'in_database': True,
                    'result': 'PHISHING' if threat == 'phishing' else 'SUSPICIOUS',
                    'risk_score': risk_score,
                    'source': f"URLhaus ({threat} - {url_status})"
                }
            
            return {
                'in_database': False,
                'result': 'SAFE',
                'risk_score': 0,
                'source': 'URLhaus Database'
            }
            
        except Exception as e:
            logger.error(f"URLhaus API lookup failed: {e}")
            return {
                'in_database': False,
                'result': 'UNKNOWN',
                'risk_score': 0,
                'source': 'URLhaus API Error'
            }
