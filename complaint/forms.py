from django import forms
from .models import Complaint, CaseType
import os

class ComplaintForm(forms.ModelForm):
    case_type = forms.ModelChoiceField(
        queryset=CaseType.objects.filter(active_status=True),
        empty_label="Select Case Type / Category",
        widget=forms.Select(attrs={
            'class': 'w-full bg-surface border border-outline-variant rounded-lg px-4 py-3 focus:ring-4 focus:ring-primary/20 focus:border-primary transition-all outline-none text-on-surface appearance-none',
            'id': 'id_crime_category'
        })
    )

    class Meta:
        model = Complaint
        fields = ['name', 'email', 'phone', 'title', 'case_type', 'description', 'location', 'evidence']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full bg-surface border border-outline rounded-lg px-4 py-3 focus:ring-4 focus:ring-primary/20 focus:border-primary transition-all outline-none', 'placeholder': 'John Doe', 'id': 'id_full_name'}),
            'email': forms.EmailInput(attrs={'class': 'w-full bg-surface border border-outline rounded-lg px-4 py-3 focus:ring-4 focus:ring-primary/20 focus:border-primary transition-all outline-none', 'placeholder': 'john@example.com', 'id': 'id_email'}),
            'phone': forms.TextInput(attrs={'class': 'w-full bg-surface border border-outline rounded-lg px-4 py-3 focus:ring-4 focus:ring-primary/20 focus:border-primary transition-all outline-none', 'placeholder': '+1 (555) 000-0000', 'id': 'id_phone'}),
            'title': forms.TextInput(attrs={'class': 'w-full bg-surface border border-outline rounded-lg px-4 py-3 focus:ring-4 focus:ring-primary/20 focus:border-primary transition-all outline-none', 'placeholder': 'Short summary of the issue', 'id': 'id_complaint_title'}),
            'description': forms.Textarea(attrs={'class': 'w-full bg-surface border border-outline rounded-lg px-4 py-3 focus:ring-4 focus:ring-primary/20 focus:border-primary transition-all outline-none', 'placeholder': 'Describe what happened in detail...', 'rows': 4, 'id': 'id_description'}),
            'location': forms.TextInput(attrs={'class': 'w-full bg-surface border border-outline rounded-lg px-4 py-3 focus:ring-4 focus:ring-primary/20 focus:border-primary transition-all outline-none', 'placeholder': 'e.g. London, UK or https://suspicious-site.com', 'id': 'id_incident_location'}),
            'evidence': forms.FileInput(attrs={'class': 'hidden', 'id': 'id_evidence'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['case_type'].queryset = CaseType.objects.filter(active_status=True)

    def clean_evidence(self):
        evidence = self.cleaned_data.get('evidence')
        if evidence:
            # Check file size limit (10MB)
            if evidence.size > 10 * 1024 * 1024:
                raise forms.ValidationError("Evidence file size must not exceed 10MB.")
            # Validate allowed file types
            ext = os.path.splitext(evidence.name)[1].lower()
            valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx', '.txt', '.eml']
            if ext not in valid_extensions:
                raise forms.ValidationError("Unsupported file extension. Supported formats are: PDF, JPG, PNG, DOC, DOCX, TXT, EML.")
        return evidence