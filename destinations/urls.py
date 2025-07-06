from django.urls import path
from . import views
from .content_api import FetchWorkView, SubmitWorkView, work_status, typeahead_search

app_name = 'destinations'

urlpatterns = [
    # Content Generation API Endpoints (before catch-all patterns)
    path('api/fetch-work/', FetchWorkView.as_view(), name='fetch_work'),
    path('api/submit-work/', SubmitWorkView.as_view(), name='submit_work'),
    path('api/work-status/', work_status, name='work_status'),
    path('api/typeahead-search/', typeahead_search, name='typeahead_search'),
    
    # English (default) routes
    path('', views.home, name='home'),
    path('golf-courses/<slug:slug>/', views.destination_detail, name='destination_detail'),
    
    # Multi-language routes
    path('<str:language>/', views.home, name='home_lang'),
    path('<str:language>/golf-courses/<slug:slug>/', views.destination_detail, name='destination_detail_lang'),

    # Redirect old /destination/{lang}-{slug} to new /destination/{lang}/{slug}
    path('destination/<str:lang_slug>/', views.redirect_old_destination_url, name='redirect_old_destination_url'),
]
