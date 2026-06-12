from django.db import models

class Complaint(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Rejected', 'Rejected')
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField() 
    phone = models.CharField(max_length=15)
    title = models.CharField(max_length=200)
    description = models.TextField()

    evidence = models.FileField(
        upload_to='evidence/',
        blank=True,
        null=True
    )

    location = models.CharField(max_length=255)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    officer_assigned = models.ForeignKey('Officer', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

class Officer(models.Model):
    name = models.CharField(max_length=100)
    badge_number = models.CharField(max_length=50, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    department = models.CharField(max_length=100)
    Station_code = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.Station_code})"

