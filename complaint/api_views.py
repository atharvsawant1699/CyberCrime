from rest_framework import viewsets, permissions
from .models import Officer, CaseType, Complaint, CaseAssignmentHistory
from .serializers import OfficerSerializer, CaseTypeSerializer, ComplaintSerializer, CaseAssignmentHistorySerializer

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and (request.user.is_staff or request.user.is_superuser)

class OfficerViewSet(viewsets.ModelViewSet):
    queryset = Officer.objects.all()
    serializer_class = OfficerSerializer
    permission_classes = [IsAdminOrReadOnly]

class CaseTypeViewSet(viewsets.ModelViewSet):
    queryset = CaseType.objects.all()
    serializer_class = CaseTypeSerializer
    permission_classes = [IsAdminOrReadOnly]

class ComplaintViewSet(viewsets.ModelViewSet):
    serializer_class = ComplaintSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return Complaint.objects.all().order_by('-date_submitted')
        
        # Check if user is a registered officer
        officer = Officer.objects.filter(user=user).first()
        if officer:
            return Complaint.objects.filter(assigned_officer=officer).order_by('-date_submitted')
            
        return Complaint.objects.filter(user=user).order_by('-date_submitted')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
