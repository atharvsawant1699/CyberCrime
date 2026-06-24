from django.contrib import admin
from .models import CyberNews, WebsiteScan, Vulnerability

@admin.register(CyberNews)
class CyberNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'published_date', 'created_at')
    list_filter = ('source', 'published_date')
    search_fields = ('title', 'description', 'source')
    ordering = ('-published_date',)


@admin.register(WebsiteScan)
class WebsiteScanAdmin(admin.ModelAdmin):
    list_display = ('url', 'result', 'risk_score', 'source', 'scanned_at')
    list_filter = ('result', 'source', 'scanned_at')
    search_fields = ('url', 'source')
    readonly_fields = ('scanned_at',)
    ordering = ('-scanned_at',)


@admin.register(Vulnerability)
class VulnerabilityAdmin(admin.ModelAdmin):
    list_display = ('cve_id', 'severity', 'published_date')
    list_filter = ('severity', 'published_date')
    search_fields = ('cve_id', 'description')
    ordering = ('-published_date',)
