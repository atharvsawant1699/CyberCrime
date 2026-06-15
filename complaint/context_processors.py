from .models import Officer

def officer_status(request):
    """
    Context processor to add 'is_officer' and 'is_admin' flags to all template contexts.
    """
    if not request.user.is_authenticated:
        return {'is_officer': False, 'is_admin': False}
    
    # An officer is someone who has an Officer profile, belongs to the 'Officers' group, or is staff/superuser
    has_profile = Officer.objects.filter(user=request.user).exists() or Officer.objects.filter(email=request.user.email).exists()
    is_officer = (
        request.user.is_staff or 
        request.user.is_superuser or
        request.user.groups.filter(name='Officers').exists() or 
        has_profile
    )
    is_admin = request.user.is_superuser or request.user.is_staff
    
    return {
        'is_officer': is_officer,
        'is_admin': is_admin
    }
