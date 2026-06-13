from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_complaint, name='register'),
    path('complaints/', views.complaint_list, name='complaints'),
    path('officer/', views.officer_dashboard, name='officer'),
    path('submission_successful/', views.submission_successful, name='submission_successful'),
]