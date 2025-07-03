"""
URL configuration for golfplex project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
import os

def ads_txt(request):
    """Serve ads.txt file for Google AdSense verification"""
    ads_txt_path = os.path.join(settings.BASE_DIR, 'ads.txt')
    try:
        with open(ads_txt_path, 'r') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/plain')
    except FileNotFoundError:
        return HttpResponse('', content_type='text/plain', status=404)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ads.txt', ads_txt, name='ads_txt'),
    path('', include('destinations.urls')),
]
