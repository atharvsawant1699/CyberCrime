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
