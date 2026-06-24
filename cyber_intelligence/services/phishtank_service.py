import requests
import logging

logger = logging.getLogger(__name__)

class PhishTankService:
    API_URL = "https://checkurl.phishtank.com/checkurl/"

    @staticmethod
    def check_url(url):
        """
        Checks a URL against the PhishTank database via their checkurl API.
        """
        payload = {
            'url': url,
            'format': 'json'
        }
        
        headers = {
            'User-Agent': 'phishtank/smart_cyber_crime_reporting_system'
        }
        
        try:
            logger.info(f"Checking URL against PhishTank: {url}")
            # The public PhishTank checkurl endpoint takes a POST request
            response = requests.post(PhishTankService.API_URL, data=payload, headers=headers, timeout=8)

            
            # If rate-limited or API returns non-200, log it
            if response.status_code == 509:
                logger.warning("PhishTank API is rate-limited (509).")
                return {
                    'in_database': False,
                    'result': 'UNKNOWN',
                    'risk_score': 0,
                    'source': 'PhishTank (Rate Limited)'
                }
            
            response.raise_for_status()
            data = response.json()
            
            # PhishTank response is typically like:
            # {
            #   "meta": { ... },
            #   "results": {
            #     "url": "...",
            #     "in_database": true,
            #     "phish_id": "...",
            #     "phish_detail_page": "...",
            #     "verified": true,
            #     "verified_at": "...",
            #     "valid": true
            #   }
            # }
            results = data.get('results', {})
            in_database = results.get('in_database', False)
            valid = results.get('valid', False)
            verified = results.get('verified', False)

            if in_database and valid and verified:
                return {
                    'in_database': True,
                    'result': 'PHISHING',
                    'risk_score': 95,
                    'source': 'PhishTank Database'
                }
            elif in_database and not verified:
                return {
                    'in_database': True,
                    'result': 'SUSPICIOUS',
                    'risk_score': 50,
                    'source': 'PhishTank (Unverified)'
                }
            
            return {
                'in_database': False,
                'result': 'SAFE',
                'risk_score': 0,
                'source': 'PhishTank Database'
            }
            
        except Exception as e:
            logger.error(f"PhishTank API lookup failed: {e}")
            return {
                'in_database': False,
                'result': 'UNKNOWN',
                'risk_score': 0,
                'source': 'PhishTank API Error'
            }
