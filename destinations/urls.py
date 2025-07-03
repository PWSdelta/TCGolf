from django.urls import path
from . import views

urlpatterns = [
    # English (default) routes
    path('', views.home, name='home'),
    path('golf-courses/<slug:slug>/', views.destination_detail, name='destination_detail'),
    
    # Multi-language routes
    path('<str:language>/', views.home, name='home_lang'),
    path('<str:language>/golf-courses/<slug:slug>/', views.destination_detail, name='destination_detail_lang'),
]
