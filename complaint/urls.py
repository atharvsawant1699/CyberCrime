from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_complaint, name='register_complaint'),
    path('complaints/', views.complaint_list, name='complaint_list'),
    path('submission_successful', views.complaint_list ,name='submission_successful'),
]   