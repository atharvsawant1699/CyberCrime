from django.urls import path
from . import views

app_name = 'cyber_intelligence'

urlpatterns = [
    path('', views.cyber_dashboard_view, name='cyber_dashboard'),
    path('scan/', views.url_scan_api, name='url_scan_api'),
]
