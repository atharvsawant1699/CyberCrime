from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Officer, CaseType, Complaint, CaseAssignmentHistory

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class OfficerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Officer
        fields = [
            'id', 'officer_id', 'full_name', 'department', 'rank',
            'specialization', 'contact_details', 'availability_status',
            'created_date', 'user'
        ]

class CaseTypeSerializer(serializers.ModelSerializer):
    assigned_officer_name = serializers.ReadOnlyField(source='assigned_officer.full_name')
    class Meta:
        model = CaseType
        fields = ['id', 'name', 'description', 'assigned_officer', 'assigned_officer_name', 'priority_level', 'active_status']

class CaseAssignmentHistorySerializer(serializers.ModelSerializer):
    previous_officer_name = serializers.ReadOnlyField(source='previous_officer.full_name')
    new_officer_name = serializers.ReadOnlyField(source='new_officer.full_name')
    changed_by_name = serializers.ReadOnlyField(source='changed_by_admin.username')
    class Meta:
        model = CaseAssignmentHistory
        fields = [
            'id', 'complaint', 'previous_officer', 'previous_officer_name',
            'new_officer', 'new_officer_name', 'changed_by_admin', 'changed_by_name',
            'date', 'reason'
        ]

class ComplaintSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    case_type_name = serializers.ReadOnlyField(source='case_type.name')
    assigned_officer_detail = OfficerSerializer(source='assigned_officer', read_only=True)
    assignment_histories = CaseAssignmentHistorySerializer(many=True, read_only=True, source='assignment_histories_set') # using default related name

    class Meta:
        model = Complaint
        fields = [
            'id', 'complaint_id', 'user', 'case_type', 'case_type_name',
            'title', 'description', 'evidence', 'location', 'date_submitted',
            'priority', 'status', 'assigned_officer', 'assigned_officer_detail',
            'investigation_notes', 'investigation_report', 'assignment_histories'
        ]
        read_only_fields = ['complaint_id', 'date_submitted', 'status', 'assigned_officer']
