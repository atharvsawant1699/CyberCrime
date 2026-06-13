from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Complaint, Officer
from .forms import ComplaintForm

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

@login_required
def register_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            if not complaint.incident_location:
                complaint.incident_location = complaint.location
            complaint.save()
            messages.success(request, 'Incident reported successfully!')
            request.session['last_submission_id'] = f"CG-{complaint.id:04d}"
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
    # Retrieve complaints for the logged-in user
    complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'complaints/complaint_list.html', {'complaints': complaints})

@login_required
def officer_dashboard(request):
    # Scoping permission checks for officers
    if not (request.user.is_staff or request.user.groups.filter(name='Officers').exists()):
        messages.error(request, 'Access denied. You do not have permission to view the officer dashboard.')
        return redirect('home')
        
    if request.method == 'POST':
        case_id = request.POST.get('case_id', '').replace('#', '').replace('CG-', '').strip()
        status = request.POST.get('status')
        officer_id = request.POST.get('officer_id')
        
        try:
            complaint = Complaint.objects.get(id=int(case_id))
            if status:
                status_mapping = {
                    'under_review': 'Submitted',
                    'processing': 'Under Investigation',
                    'critical': 'Under Investigation',
                    'resolved': 'Resolved',
                    'dismissed': 'Rejected'
                }
                complaint.status = status_mapping.get(status, status)
            if officer_id:
                try:
                    officer = Officer.objects.get(id=officer_id)
                    complaint.officer_assigned = officer
                    complaint.assigned_officer = officer
                except Officer.DoesNotExist:
                    pass
            complaint.save()
            messages.success(request, f'Case #CG-{complaint.id:04d} updated successfully!')
        except (Complaint.DoesNotExist, ValueError):
            messages.error(request, f'Case #{case_id} not found or invalid format.')
            
        return redirect('officer')
        
    complaints = Complaint.objects.all().order_by('-created_at')
    officers = Officer.objects.all()
    
    total_cases = complaints.count()
    high_severity = complaints.filter(category='ransomware').count()
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
    }
    
    return render(request, 'complaints/officer_dashboard.html', context)

def submission_successful(request):
    complaint_id = request.session.get('last_submission_id', 'CG-UNKNOWN')
    return render(request, 'complaints/submission_successful.html', {'complaint_id': complaint_id})