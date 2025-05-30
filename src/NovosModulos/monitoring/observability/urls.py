from django.urls import path
from . import views

app_name = 'observabilidade'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/observabilidade/dashboard', views.dashboard_data, name='dashboard_data'),
] 