from django.shortcuts import render, redirect
from .models import Complaint
from .forms import ComplaintForm

def home(request):
    return render(request, 'complaints/home.html')


def register_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('submission_successful  ')

    else:
        form = ComplaintForm()

    return render(
        request,
        'complaints/register_complaint.html',
        {'form': form}
    )



def complaint_list(request):

    complaints = Complaint.objects.all().order_by('-created_at')

    return render(  
        request,
        'complaints/complaint_list.html',
        {'complaints': complaints}
    )