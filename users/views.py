from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import UserRegistrationForm, UserUpdateForm, UserProfileForm
from .models import UserProfile

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Create the associated UserProfile
            UserProfile.objects.create(
                user=user, 
                phone_number=form.cleaned_data.get('phone_number', '')
            )
            
            messages.success(request, f'Account created for {user.username}! You can now authorize access.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    next_url = request.POST.get('next') or request.GET.get('next')
    
    if request.method == 'POST':
        username_input = request.POST.get('username', '').strip()
        password_input = request.POST.get('password', '')
        
        # Authenticate by exact username
        user = authenticate(request, username=username_input, password=password_input)
        
        # Fallback: Search by email or case-insensitive username
        if user is None and username_input:
            from django.contrib.auth.models import User
            user_obj = User.objects.filter(email__iexact=username_input).exclude(email='').first()
            if not user_obj:
                user_obj = User.objects.filter(username__iexact=username_input).first()
                
            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password_input)
                
        if user is not None:
            login(request, user)
            display_name = user.first_name or user.username
            messages.success(request, f"Access authorized. Welcome back, {display_name}!")
            
            if next_url and next_url.startswith('/') and not next_url.startswith('//'):
                return redirect(next_url)
                
            from complaint.models import Officer
            has_profile = Officer.objects.filter(user=user).exists()
            if not has_profile and user.email:
                has_profile = Officer.objects.filter(email=user.email).exists()
                
            is_officer = has_profile or user.groups.filter(name='Officers').exists() or user.is_staff
            
            if user.is_superuser:
                return redirect('admin_dashboard')
            elif is_officer:
                return redirect('officer')
            else:
                return redirect('home')
        else:
            messages.error(request, "Invalid username/email or password. Please verify your credentials.")
            form = AuthenticationForm(request, data=request.POST)
    else:
        form = AuthenticationForm()
        
    return render(request, 'users/login.html', {'form': form, 'next': next_url})

@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have logged out successfully.')
        return redirect('login')
    return redirect('home')

@login_required
def profile_view(request):
    # Ensure profile exists
    if hasattr(request.user, 'userprofile'):
        profile = request.user.userprofile
    else:
        profile = UserProfile.objects.create(user=request.user)
        
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = UserProfileForm(instance=profile)
        
    # Query complaints counts for user dashboard metrics
    from complaint.models import Complaint
    user_complaints = Complaint.objects.filter(user=request.user)
    
    total_complaints = user_complaints.count()
    resolved_complaints = user_complaints.filter(status='Resolved').count()
    pending_complaints = user_complaints.exclude(status__in=['Resolved', 'Rejected']).count()
    
    pending_list = user_complaints.exclude(status__in=['Resolved', 'Rejected']).order_by('-created_at')[:5]
    resolved_list = user_complaints.filter(status='Resolved').order_by('-created_at')[:5]
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'profile': profile,
        'total_complaints': total_complaints,
        'resolved_complaints': resolved_complaints,
        'pending_complaints': pending_complaints,
        'pending_list': pending_list,
        'resolved_list': resolved_list
    }
    
    return render(request, 'users/profile.html', context)
