from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from urllib.parse import urlparse
import logging

from .models import CyberNews, Vulnerability, WebsiteScan
from .services.phishtank_service import PhishTankService
from .services.urlhaus_service import URLhausService
from .services.virustotal_service import VirusTotalService

logger = logging.getLogger(__name__)

@login_required
def cyber_dashboard_view(request):
    """
    Renders the CTI Dashboard displaying aggregated intelligence.
    """
    # Fetch cached news (excluding CISA Advisories to keep them in alerts)
    news_queryset = CyberNews.objects.exclude(source='CISA Advisories').order_by('-published_date')
    
    # Fallback to all news if no GNews matches
    if not news_queryset.exists():
        news_queryset = CyberNews.objects.all().order_by('-published_date')

    # Paginate Cyber News at 10 items per page
    paginator = Paginator(news_queryset, 10)
    page_number = request.GET.get('page')
    news_page = paginator.get_page(page_number)
    
    # Filter advisories specifically for CISA as Threat Alerts (displaying up to 10 dynamically)
    threat_alerts = CyberNews.objects.filter(source__icontains='CISA').order_by('-published_date')[:10]
    
    # Fetch vulnerabilities
    vulnerabilities = Vulnerability.objects.all().order_by('-published_date')[:10]
    
    # Fetch recent URL scans
    recent_scans = WebsiteScan.objects.all().order_by('-scanned_at')[:8]

    # Additional premium stats
    total_scans = WebsiteScan.objects.count()
    phishing_scans = WebsiteScan.objects.filter(result='PHISHING').count()
    suspicious_scans = WebsiteScan.objects.filter(result='SUSPICIOUS').count()
    safe_scans = WebsiteScan.objects.filter(result='SAFE').count()
    cisa_count = CyberNews.objects.filter(source__icontains='CISA').count()
    cve_count = Vulnerability.objects.count()

    context = {
        'news_page': news_page,
        'threat_alerts': threat_alerts,
        'vulnerabilities': vulnerabilities,
        'recent_scans': recent_scans,
        'stats': {
            'total_scans': total_scans,
            'phishing_scans': phishing_scans,
            'suspicious_scans': suspicious_scans,
            'safe_scans': safe_scans,
            'cisa_count': cisa_count,
            'cve_count': cve_count,
        }
    }
    
    return render(request, 'cyber_intelligence/cyber_dashboard.html', context)


@login_required
@require_POST
def url_scan_api(request):
    """
    Endpoint for performing live scans on a URL.
    Checks URL structure, PhishTank, URLhaus, and VirusTotal.
    """
    url = request.POST.get('url', '').strip()
    
    # Validate input URL
    if not url:
        return JsonResponse({'error': 'URL parameter is required.'}, status=400)
    
    # Clean URL input (prepend http if missing)
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url
        
    validator = URLValidator()
    try:
        validator(url)
    except ValidationError:
        return JsonResponse({'error': 'Invalid URL format.'}, status=400)
    
    # 1. URL Structure Heuristics Analysis
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()
    
    structure_risk = 0
    structure_reasons = []
    
    # Check for IP address in domain
    parts = domain.split('.')
    is_ip = all(part.isdigit() for part in parts) if len(parts) == 4 else False
    if is_ip:
        structure_risk += 40
        structure_reasons.append("IP Address as Hostname")
        
    # Check suspicious keywords in domain/path
    suspicious_keywords = ['login', 'secure', 'signin', 'bank', 'verify', 'update', 'account', 'paypal', 'support']
    for keyword in suspicious_keywords:
        if keyword in url.lower():
            structure_risk += 15
            structure_reasons.append(f"Suspicious word: '{keyword}'")
            
    # Check length
    if len(url) > 100:
        structure_risk += 10
        structure_reasons.append("Excessive URL length")

    # 2. Check external services
    # PhishTank
    pt_result = PhishTankService.check_url(url)
    
    # URLhaus
    uh_result = URLhausService.check_url(url)
    
    # VirusTotal
    vt_result = VirusTotalService.check_url(url)
    
    # Aggregate outcomes
    aggregated_risk = max(
        structure_risk,
        pt_result.get('risk_score', 0),
        uh_result.get('risk_score', 0),
        vt_result.get('risk_score', 0)
    )
    
    # Set final categorization
    if aggregated_risk >= 75:
        final_result = 'PHISHING'
    elif aggregated_risk >= 30:
        final_result = 'SUSPICIOUS'
    else:
        final_result = 'SAFE'
        
    # Combine sources for reporting
    sources = []
    if pt_result.get('in_database'):
        sources.append("PhishTank")
    if uh_result.get('in_database'):
        sources.append("URLhaus")
    if vt_result.get('in_database') and vt_result.get('risk_score', 0) > 0:
        sources.append("VirusTotal")
    if structure_reasons:
        sources.append("Structure Analysis")
        
    source_str = ", ".join(sources) if sources else "Heuristics & APIs"

    # Save to scan history
    scan = WebsiteScan.objects.create(
        url=url,
        result=final_result,
        risk_score=min(aggregated_risk, 100),
        source=source_str[:255]
    )

    return JsonResponse({
        'url': url,
        'result': final_result,
        'risk_score': scan.risk_score,
        'sources': source_str,
        'reasons': structure_reasons,
        'scanned_at': scan.scanned_at.strftime('%Y-%m-%d %H:%M:%S'),
        'details': {
            'phishtank': pt_result,
            'urlhaus': uh_result,
            'virustotal': vt_result
        }
    })
