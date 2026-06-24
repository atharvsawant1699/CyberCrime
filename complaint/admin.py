from django.contrib import admin
from .models import Officer, CaseType, Complaint, CaseAssignmentHistory

@admin.register(Officer)
class OfficerAdmin(admin.ModelAdmin):
    list_display = ('officer_id', 'full_name', 'rank', 'specialization', 'availability_status', 'created_date')
    list_filter = ('availability_status', 'specialization', 'rank', 'department')
    search_fields = ('officer_id', 'full_name', 'rank', 'department', 'contact_details')
    ordering = ('-created_date',)

@admin.register(CaseType)
class CaseTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'assigned_officer', 'priority_level', 'active_status')
    list_filter = ('priority_level', 'active_status')
    search_fields = ('name', 'description')

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('complaint_id', 'title', 'user', 'case_type', 'priority', 'status', 'assigned_officer', 'date_submitted')
    list_filter = ('status', 'priority', 'case_type', 'date_submitted')
    search_fields = ('complaint_id', 'title', 'description', 'name', 'email', 'phone', 'location')
    readonly_fields = ('complaint_id', 'date_submitted')
    ordering = ('-date_submitted',)

@admin.register(CaseAssignmentHistory)
class CaseAssignmentHistoryAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'previous_officer', 'new_officer', 'changed_by_admin', 'date', 'reason')
    list_filter = ('date', 'changed_by_admin')
    search_fields = ('complaint__complaint_id', 'reason', 'previous_officer__full_name', 'new_officer__full_name')
    readonly_fields = ('complaint', 'previous_officer', 'new_officer', 'changed_by_admin', 'date', 'reason')