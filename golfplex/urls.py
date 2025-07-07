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
from django.urls import path, include, re_path
from django.http import HttpResponse
from django.conf import settings
import os
import os

def static_sitemap_xml(request):
    sitemap_path = os.path.join(settings.BASE_DIR, 'sitemap.xml')
    try:
        with open(sitemap_path, 'r') as f:
            content = f.read()
        return HttpResponse(content, content_type='application/xml')
    except Exception:
        return HttpResponse('', content_type='application/xml', status=404)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Keep ads.txt static serving
    re_path(r'^ads\.txt$', lambda request: HttpResponse(open(os.path.join(settings.BASE_DIR, 'ads.txt')).read() if os.path.exists(os.path.join(settings.BASE_DIR, 'ads.txt')) else '', content_type='text/plain'), name='ads_txt'),
    # Serve static sitemap.xml
    re_path(r'^sitemap\.xml/?$', static_sitemap_xml, name='sitemap_xml'),
    path('sitemap.xml/', static_sitemap_xml),
    path('', include('destinations.urls')),
]
