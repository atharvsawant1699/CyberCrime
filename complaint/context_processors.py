from .models import Officer

def officer_status(request):
    """
    Context processor to add 'is_officer' and 'is_admin' flags to all template contexts.
    """
    if not request.user.is_authenticated:
        return {'is_officer': False, 'is_admin': False}
    
    # Superusers are strictly administrators, NOT officers
    is_admin = request.user.is_superuser
    
    has_profile = Officer.objects.filter(user=request.user).exists()
    is_officer = (not is_admin) and (has_profile or request.user.groups.filter(name='Officers').exists())
    
    return {
        'is_officer': is_officer,
        'is_admin': is_admin
    }

def branding_metadata(request):
    """
    Context processor to add global software branding variables to all template contexts.
    """
    from django.conf import settings
    return {
        'SOFTWARE_NAME': getattr(settings, 'SOFTWARE_NAME', 'CyberGuard'),
        'SOFTWARE_VERSION': getattr(settings, 'SOFTWARE_VERSION', 'v1.0.0'),
        'BUILD_NUMBER': getattr(settings, 'BUILD_NUMBER', '2026.001'),
        'RELEASE_DATE': getattr(settings, 'RELEASE_DATE', 'June 2026'),
        'COMPANY_NAME': getattr(settings, 'COMPANY_NAME', 'AIsync Software Solutions'),
        'DEVELOPER_NAME': getattr(settings, 'DEVELOPER_NAME', 'Indranil Sawant'),
        'COPYRIGHT_YEAR': getattr(settings, 'COPYRIGHT_YEAR', '2026'),
    }
