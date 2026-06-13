from django.db import models

class CyberNews(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True, max_length=1000)
    source = models.CharField(max_length=100)
    article_url = models.URLField(unique=True, max_length=1000)
    published_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Cyber News"
        ordering = ['-published_date']

    def __str__(self):
        return self.title

    @property
    def formatted_published_date(self):
        return self._format_datetime(self.published_date)

    @property
    def formatted_created_at(self):
        return self._format_datetime(self.created_at)

    def _format_datetime(self, dt):
        if not dt:
            return ""
        from django.utils import timezone
        local_dt = timezone.localtime(dt)
        date_str = local_dt.strftime("%B %d, %Y")
        
        if local_dt.hour == 12 and local_dt.minute == 0:
            time_str = "noon"
        elif local_dt.hour == 0 and local_dt.minute == 0:
            time_str = "midnight"
        else:
            hour = local_dt.hour
            minute = local_dt.minute
            am_pm = "a.m." if hour < 12 else "p.m."
            hour_12 = hour % 12
            if hour_12 == 0:
                hour_12 = 12
            time_str = f"{hour_12}:{minute:02d} {am_pm}"
            
        return f"{date_str}, {time_str}"



class WebsiteScan(models.Model):
    RESULT_CHOICES = [
        ('SAFE', 'SAFE'),
        ('SUSPICIOUS', 'SUSPICIOUS'),
        ('PHISHING', 'PHISHING'),
    ]

    url = models.URLField(max_length=2048)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, default='SAFE')
    risk_score = models.IntegerField(default=0)  # 0 to 100
    source = models.CharField(max_length=255)  # PhishTank, URLhaus, Structure Analysis, etc.
    scanned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scanned_at']

    def __str__(self):
        return f"{self.url} - {self.result} ({self.risk_score}%)"


class Vulnerability(models.Model):
    cve_id = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    severity = models.CharField(max_length=20, blank=True, null=True)  # Low, Medium, High, Critical
    published_date = models.DateTimeField()
    reference_url = models.URLField(max_length=1000, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Vulnerabilities"
        ordering = ['-published_date']

    def __str__(self):
        return f"{self.cve_id} - {self.severity}"
