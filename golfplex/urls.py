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
from django.views.decorators.http import require_GET
import os

@require_GET
def ads_txt(request):
    """Serve ads.txt file for Google AdSense verification"""
    ads_txt_path = os.path.join(settings.BASE_DIR, 'ads.txt')
    try:
        with open(ads_txt_path, 'r') as f:
            content = f.read()
        response = HttpResponse(content, content_type='text/plain')
        # Prevent caching to ensure the latest content is always served
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    except FileNotFoundError:
        return HttpResponse('', content_type='text/plain', status=404)

@require_GET
def sitemap_xml(request):
    """Serve sitemap.xml file for search engine indexing"""
    sitemap_path = os.path.join(settings.BASE_DIR, 'sitemap.xml')
    try:
        with open(sitemap_path, 'r') as f:
            content = f.read()
        response = HttpResponse(content, content_type='application/xml')
        # Prevent caching to ensure the latest content is always served
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        # Prevent adding trailing slashes to XML files
        response['X-Robots-Tag'] = 'noindex'
        return response
    except FileNotFoundError:
        return HttpResponse('', content_type='application/xml', status=404)

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^ads\.txt$', ads_txt, name='ads_txt'),
    # Use a more specific regex pattern for sitemap.xml
    re_path(r'^sitemap\.xml/?$', sitemap_xml, name='sitemap_xml'),
    path('sitemap.xml/', sitemap_xml),  # Also handle with trailing slash explicitly
    path('', include('destinations.urls')),
]
