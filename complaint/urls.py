from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

router = DefaultRouter()
router.register(r'officers', api_views.OfficerViewSet, basename='api_officers')
router.register(r'case-types', api_views.CaseTypeViewSet, basename='api_case_types')
router.register(r'complaints', api_views.ComplaintViewSet, basename='api_complaints')

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_complaint, name='register'),
    path('complaints/', views.complaint_list, name='complaints'),
    path('complaints/<str:complaint_id>/', views.case_detail, name='case_detail'),
    path('officer/', views.officer_dashboard, name='officer'),
    path('submission_successful/', views.submission_successful, name='submission_successful'),
    
    # Admin front-end views
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/reassign/', views.reassign_case, name='reassign_case'),
    path('admin-dashboard/toggle-availability/<int:officer_id>/', views.toggle_officer_availability, name='toggle_officer_availability'),
    path('admin-dashboard/officer-specialization/<int:officer_id>/', views.update_officer_specialization, name='update_officer_specialization'),
    
    # API endpoints
    path('api/', include(router.urls)),
]