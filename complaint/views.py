from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from .models import Complaint, Officer, CaseType, CaseAssignmentHistory
from .forms import ComplaintForm

def superuser_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is a superuser.
    """
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_superuser:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapped_view

def officer_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is an officer.
    Superusers are redirected to the admin dashboard.
    """
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.is_superuser:
            return redirect('admin_dashboard')
            
        has_profile = Officer.objects.filter(user=request.user).exists()
        is_officer = has_profile or request.user.groups.filter(name='Officers').exists()
        if not is_officer:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapped_view

def home(request):
    from cyber_intelligence.models import CyberNews
    
    # Fetch latest CISA advisories to show as a quick alert feed
    cisa_alerts = CyberNews.objects.filter(source__icontains='CISA').order_by('-published_date')[:5]
    
    # Fetch general cyber news (excluding CISA) to show in a card deck
    news_queryset = CyberNews.objects.exclude(source='CISA Advisories').order_by('-published_date')
    if not news_queryset.exists():
        news_queryset = CyberNews.objects.all().order_by('-published_date')
        
    # Paginate Cyber News at 10 items per page
    paginator = Paginator(news_queryset, 10)
    page_number = request.GET.get('page')
    news_page = paginator.get_page(page_number)
    
    context = {
        'cisa_alerts': cisa_alerts,
        'news_page': news_page,
    }
    return render(request, 'complaints/home.html', context)

def ensure_default_case_types():
    if not CaseType.objects.exists():
        default_types = [
            ("Online Fraud", "Frauds related to online shopping, e-commerce, and services.", "High"),
            ("Banking Fraud", "Banking scams, credit card theft, OTP frauds, and banking phishing.", "High"),
            ("Phishing", "Phishing links, deceptive emails, and spoofed login forms.", "Medium"),
            ("Fake Website", "Websites designed to copy real organizations and steal credentials or money.", "Medium"),
            ("Identity Theft", "Stealing personal information, impersonating someone online, or account takeovers.", "High"),
            ("Cyber Harassment", "Cyber bullying, threats, and online harassment.", "Medium"),
            ("Social Media Crime", "Scams, impersonation, or offensive activities on social media.", "Medium"),
            ("Malware Attack", "Ransomware, viruses, spywares, and malicious softwares.", "High"),
        ]
        for name, desc, priority in default_types:
            CaseType.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'priority_level': priority,
                    'active_status': True
                }
            )

@login_required
def register_complaint(request):
    ensure_default_case_types()
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()
            messages.success(request, 'Incident reported successfully!')
            request.session['last_submission_id'] = complaint.complaint_id
            return redirect('submission_successful')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
    else:
        form = ComplaintForm()
    
    return render(request, 'complaints/register_complaint.html', {'form': form})

@login_required
def complaint_list(request):
    if request.user.is_superuser:
        complaints = Complaint.objects.all().order_by('-date_submitted')
    elif Officer.objects.filter(user=request.user).exists() or request.user.groups.filter(name='Officers').exists():
        officer_profile = Officer.objects.filter(user=request.user).first()
        if not officer_profile:
            officer_profile = Officer.objects.filter(email=request.user.email).first()
        complaints = Complaint.objects.filter(assigned_officer=officer_profile).order_by('-date_submitted')
    else:
        complaints = Complaint.objects.filter(user=request.user).order_by('-date_submitted')
        
    return render(request, 'complaints/complaint_list.html', {'complaints': complaints})

@login_required
def case_detail(request, complaint_id):
    try:
        complaint = Complaint.objects.get(complaint_id=complaint_id)
    except Complaint.DoesNotExist:
        messages.error(request, 'Case not found.')
        return redirect('home')
        
    # Access control: Owner, Assigned Officer, or Admin
    is_admin = request.user.is_superuser or request.user.is_staff
    is_assigned_officer = complaint.assigned_officer and complaint.assigned_officer.user == request.user
    is_owner = complaint.user == request.user
    
    if not (is_admin or is_assigned_officer or is_owner):
        messages.error(request, 'Access denied. You do not have permission to view this case.')
        return redirect('home')
        
    histories = complaint.assignment_histories.all().order_by('-date')
    
    context = {
        'complaint': complaint,
        'histories': histories,
        'is_admin': is_admin,
        'is_assigned_officer': is_assigned_officer,
        'is_owner': is_owner,
    }
    return render(request, 'complaints/case_detail.html', context)

@officer_required
def officer_dashboard(request):
    officer_profile = Officer.objects.filter(user=request.user).first()
    if not officer_profile:
        officer_profile = Officer.objects.filter(email=request.user.email).first()
        
    if request.method == 'POST':
        complaint_id = request.POST.get('case_id', '').replace('#', '').strip()
        status = request.POST.get('status')
        notes = request.POST.get('notes', '').strip()
        report = request.FILES.get('report')
        
        try:
            complaint = Complaint.objects.get(complaint_id=complaint_id, assigned_officer=officer_profile)
                
            if status:
                status_mapping = {
                    'under_review': 'Pending',
                    'processing': 'Under Investigation',
                    'critical': 'Under Investigation',
                    'resolved': 'Resolved',
                    'dismissed': 'Closed'
                }
                complaint.status = status_mapping.get(status, status)
                
            if notes:
                timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
                officer_name = officer_profile.full_name if officer_profile else request.user.username
                new_entry = f"[{timestamp}] Officer {officer_name}:\n{notes}\n\n"
                complaint.investigation_notes = new_entry + (complaint.investigation_notes or '')
                
            if report:
                complaint.investigation_report = report
                
            complaint.save()
            messages.success(request, f'Case {complaint.complaint_id} updated successfully!')
        except (Complaint.DoesNotExist, ValueError):
            messages.error(request, f'Case {complaint_id} not found or permission denied.')
            
        return redirect('officer')
        
    complaints = Complaint.objects.filter(assigned_officer=officer_profile).order_by('-date_submitted')
    officers = Officer.objects.all()
    
    total_cases = complaints.count()
    high_severity = complaints.filter(priority='High').count()
    resolved_count = complaints.filter(status='Resolved').count()
    resolution_rate = round((resolved_count / total_cases * 100), 1) if total_cases > 0 else 0.0
    
    stats = {
        'total_cases': total_cases,
        'high_severity': high_severity,
        'resolved_count': resolved_count,
        'resolution_rate': resolution_rate,
    }
    
    context = {
        'complaints': complaints,
        'officers': officers,
        'stats': stats,
        'officer_profile': officer_profile,
    }
    
    return render(request, 'complaints/officer_dashboard.html', context)

@superuser_required
def admin_dashboard(request):
        
    ensure_default_case_types()
    complaints = Complaint.objects.all().order_by('-date_submitted')
    officers = Officer.objects.all().order_by('full_name')
    case_types = CaseType.objects.all().order_by('name')
    
    total_cases = complaints.count()
    pending_cases = complaints.filter(status='Pending').count()
    assigned_cases = complaints.filter(status='Assigned').count()
    investigating_cases = complaints.filter(status__in=['Under Investigation', 'Evidence Review']).count()
    resolved_cases = complaints.filter(status='Resolved').count()
    closed_cases = complaints.filter(status='Closed').count()
    
    available_officers = officers.filter(availability_status=True).count()
    
    stats = {
        'total_cases': total_cases,
        'pending_cases': pending_cases,
        'assigned_cases': assigned_cases,
        'investigating_cases': investigating_cases,
        'resolved_cases': resolved_cases,
        'closed_cases': closed_cases,
        'available_officers': available_officers,
    }
    
    context = {
        'complaints': complaints,
        'officers': officers,
        'case_types': case_types,
        'stats': stats,
        'specialization_choices': Officer.SPECIALIZATION_CHOICES,
    }
    
    return render(request, 'complaints/admin_dashboard.html', context)

@superuser_required
def reassign_case(request):
        
    if request.method == 'POST':
        complaint_id = request.POST.get('complaint_id')
        officer_id = request.POST.get('officer_id')
        reason = request.POST.get('reason', '').strip() or 'Workload Distribution'
        
        try:
            complaint = Complaint.objects.get(complaint_id=complaint_id)
            previous_officer = complaint.assigned_officer
            new_officer = None
            
            if officer_id:
                new_officer = Officer.objects.get(id=officer_id)
                
            complaint.assigned_officer = new_officer
            if new_officer:
                complaint.status = 'Assigned'
            else:
                complaint.status = 'Pending'
            complaint.save()
            
            # Log assignment history
            CaseAssignmentHistory.objects.create(
                complaint=complaint,
                previous_officer=previous_officer,
                new_officer=new_officer,
                changed_by_admin=request.user,
                reason=reason
            )
            
            # Notify new officer
            if new_officer:
                complaint.send_assignment_notification()
                
            messages.success(request, f'Case {complaint.complaint_id} reassigned successfully.')
        except (Complaint.DoesNotExist, Officer.DoesNotExist):
            messages.error(request, 'Error executing reassignment. Invalid case or officer.')
            
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))

@superuser_required
def toggle_officer_availability(request, officer_id):
        
    try:
        officer = Officer.objects.get(id=officer_id)
        officer.availability_status = not officer.availability_status
        officer.save()
        status_str = "Available" if officer.availability_status else "Unavailable"
        messages.success(request, f'Officer {officer.full_name} status updated to {status_str}.')
    except Officer.DoesNotExist:
        messages.error(request, 'Officer not found.')
        
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))

@superuser_required
def update_officer_specialization(request, officer_id):
        
    if request.method == 'POST':
        specialization = request.POST.get('specialization')
        try:
            officer = Officer.objects.get(id=officer_id)
            officer.specialization = specialization
            officer.save()
            messages.success(request, f'Officer {officer.full_name} specialization updated to {specialization}.')
        except Officer.DoesNotExist:
            messages.error(request, 'Officer not found.')
            
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))

def submission_successful(request):
    complaint_id = request.session.get('last_submission_id', 'CG-UNKNOWN')
    return render(request, 'complaints/submission_successful.html', {'complaint_id': complaint_id})