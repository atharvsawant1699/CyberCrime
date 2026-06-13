from django.db import models
from django.contrib.auth.models import User

class Officer(models.Model):
    name = models.CharField(max_length=100)
    badge_number = models.CharField(max_length=50, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    department = models.CharField(max_length=100)
    Station_code = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.Station_code})"

class Complaint(models.Model):
    STATUS_CHOICES = [
        ('Submitted', 'Submitted'),
        ('Under Investigation', 'Under Investigation'),
        ('Resolved', 'Resolved'),
        ('Rejected', 'Rejected')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField() 
    phone = models.CharField(max_length=15)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()

    evidence = models.FileField(
        upload_to='evidence/',
        blank=True,
        null=True
    )

    location = models.CharField(max_length=255)
    incident_location = models.CharField(max_length=255, blank=True, null=True)

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='Submitted'
    )

    officer_assigned = models.ForeignKey(Officer, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints_assigned')
    assigned_officer = models.ForeignKey(Officer, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints_assigned_officer')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
