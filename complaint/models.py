from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Officer(models.Model):
    SPECIALIZATION_CHOICES = [
        ('Online Fraud', 'Online Fraud'),
        ('Banking Fraud', 'Banking Fraud'),
        ('Phishing', 'Phishing'),
        ('Fake Website', 'Fake Website'),
        ('Identity Theft', 'Identity Theft'),
        ('Cyber Harassment', 'Cyber Harassment'),
        ('Social Media Crime', 'Social Media Crime'),
        ('Malware Attack', 'Malware Attack'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='officer_profile')
    officer_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=150, default='', blank=True)
    department = models.CharField(max_length=100, default='', blank=True)
    rank = models.CharField(max_length=100, default='', blank=True)
    specialization = models.CharField(max_length=100, choices=SPECIALIZATION_CHOICES, default='Phishing', blank=True)
    contact_details = models.TextField(blank=True, null=True, default='')
    availability_status = models.BooleanField(default=True)
    created_date = models.DateTimeField(default=timezone.now, blank=True)

    # Legacy fields kept for compatibility with existing tests/queries
    name = models.CharField(max_length=100, blank=True, null=True)
    badge_number = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    Station_code = models.CharField(max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Sync full_name and name
        if self.full_name and not self.name:
            self.name = self.full_name
        elif self.name and not self.full_name:
            self.full_name = self.name
            
        # Sync officer_id and badge_number
        if self.officer_id and not self.badge_number:
            self.badge_number = self.officer_id
        elif self.badge_number and not self.officer_id:
            self.officer_id = self.badge_number

        # Sync email
        if self.user and not self.email:
            self.email = self.user.email
        elif self.email and self.user and not self.user.email:
            self.user.email = self.email
            self.user.save(update_fields=['email'])
            
        # Sync contact_details and phone
        if self.phone and not self.contact_details:
            self.contact_details = self.phone
        elif self.contact_details and not self.phone:
            self.phone = self.contact_details[:15]
            
        if not self.Station_code:
            self.Station_code = "CYB-HQ"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name or self.name or 'Unnamed Officer'} ({self.rank or 'No Rank'} - {self.specialization})"


class CaseType(models.Model):
    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True, default='')
    assigned_officer = models.ForeignKey(Officer, on_delete=models.SET_NULL, null=True, blank=True, related_name='case_types')
    priority_level = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    active_status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Complaint(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Assigned', 'Assigned'),
        ('Under Investigation', 'Under Investigation'),
        ('Evidence Review', 'Evidence Review'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]

    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]

    complaint_id = models.CharField(max_length=50, unique=True, null=True, blank=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='complaints')
    case_type = models.ForeignKey(CaseType, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints')
    title = models.CharField(max_length=200)
    description = models.TextField()
    evidence = models.FileField(upload_to='evidence/', blank=True, null=True)
    location = models.CharField(max_length=255)
    date_submitted = models.DateTimeField(default=timezone.now, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    assigned_officer = models.ForeignKey(Officer, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_complaints')
    investigation_notes = models.TextField(blank=True, null=True, default='')
    investigation_report = models.FileField(upload_to='reports/', blank=True, null=True)

    # Legacy fields
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True) 
    phone = models.CharField(max_length=15, blank=True, null=True)
    incident_location = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True) # Kept for older templates and forms
    created_at = models.DateTimeField(auto_now_add=True) # Alias to date_submitted
    updated_at = models.DateTimeField(auto_now=True)

    # Allow accessing officer_assigned
    @property
    def officer_assigned(self):
        return self.assigned_officer
    
    @officer_assigned.setter
    def officer_assigned(self, value):
        self.assigned_officer = value

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        # Determine priority and assigned_officer from CaseType if not set
        if self.case_type:
            if not self.priority or self.priority == 'Medium':
                self.priority = self.case_type.priority_level
            if not self.category:
                self.category = self.case_type.name
            if is_new and not self.assigned_officer:
                # Automatic case allocation logic
                if self.case_type.assigned_officer and self.case_type.assigned_officer.availability_status:
                    self.assigned_officer = self.case_type.assigned_officer
                    self.status = 'Assigned'
                else:
                    # Fallback: find another officer with the same specialization who is available
                    available_officer = Officer.objects.filter(
                        specialization=self.case_type.name,
                        availability_status=True
                    ).first()
                    if available_officer:
                        self.assigned_officer = available_officer
                        self.status = 'Assigned'
                        
        if self.assigned_officer and self.status == 'Pending':
            self.status = 'Assigned'

        # Auto-fill user details into legacy fields if citizen logged in
        if self.user:
            if not self.name:
                self.name = f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
            if not self.email:
                self.email = self.user.email
            if not self.phone and hasattr(self.user, 'userprofile'):
                self.phone = self.user.userprofile.phone_number

        if not self.incident_location:
            self.incident_location = self.location

        super().save(*args, **kwargs)
        
        # Generate unique complaint_id
        if not self.complaint_id:
            self.complaint_id = f"CYB{10000 + self.id}"
            super().save(update_fields=['complaint_id'])
            
            # Send notification
            if self.assigned_officer:
                self.send_assignment_notification()

    def send_assignment_notification(self):
        from django.core.mail import send_mail
        subject = f"[CyberGuard ALERT] Case Assigned: {self.complaint_id}"
        message = (
            f"Dear Officer {self.assigned_officer.full_name or self.assigned_officer.name},\n\n"
            f"A new cybercrime complaint has been assigned to you.\n\n"
            f"Case ID: {self.complaint_id}\n"
            f"Title: {self.title}\n"
            f"Priority: {self.priority}\n"
            f"Location: {self.location}\n\n"
            f"Please login to the Officer Command Dashboard to begin investigation.\n\n"
            f"Regards,\n"
            f"CyberGuard Automated Allocation System"
        )
        recipient = self.assigned_officer.email or (self.assigned_officer.user.email if self.assigned_officer.user else None)
        if recipient:
            try:
                send_mail(
                    subject,
                    message,
                    'system@cyberguard.gov.in',
                    [recipient],
                    fail_silently=True
                )
            except Exception:
                pass

    def __str__(self):
        return f"{self.complaint_id or 'TEMP'} - {self.title}"


class CaseAssignmentHistory(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='assignment_histories')
    previous_officer = models.ForeignKey(Officer, on_delete=models.SET_NULL, null=True, blank=True, related_name='history_previous')
    new_officer = models.ForeignKey(Officer, on_delete=models.SET_NULL, null=True, blank=True, related_name='history_new')
    changed_by_admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Case Assignment Histories"

    def __str__(self):
        prev = self.previous_officer.full_name if self.previous_officer else "None"
        new = self.new_officer.full_name if self.new_officer else "None"
        return f"{self.complaint.complaint_id}: {prev} -> {new} by {self.changed_by_admin}"
