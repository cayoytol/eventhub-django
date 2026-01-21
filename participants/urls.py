from django.urls import path
from . import views

urlpatterns = [
    path('', views.register_view, name='register'),
    path('success/<uuid:qr_token>/', views.success_view, name='success'),
    path('cancel/<uuid:qr_token>/', views.cancel_view, name='cancel_registration'),
    path('checkin/<uuid:qr_token>/', views.checkin_view, name='checkin'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('export/', views.export_participants, name='export_participants'),
]