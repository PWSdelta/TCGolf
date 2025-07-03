import re
from django.conf import settings
from django.middleware.common import CommonMiddleware
from django.http import HttpResponsePermanentRedirect
from django.urls import is_valid_path


class NoTrailingSlashForFileExtensionsMiddleware(CommonMiddleware):
    """
    Middleware to prevent appending slashes to URLs with certain file extensions.
    This extends Django's CommonMiddleware to add exceptions for file extensions
    defined in settings.DISALLOW_SLASH_APPEND_EXTENSIONS.
    """

    def process_request(self, request):
        # Skip this middleware if APPEND_SLASH is disabled
        if not settings.APPEND_SLASH:
            return None
            
        # Get the extensions list from settings or use default
        extensions = getattr(settings, 'DISALLOW_SLASH_APPEND_EXTENSIONS', ['.xml', '.txt', '.json'])
        
        # Check if the URL ends with any of the disallowed extensions
        path = request.path
        
        # If the URL has an extension in our disallowed list, don't append a slash
        for ext in extensions:
            if path.endswith(ext):
                return None
        
        # Otherwise, use the default CommonMiddleware behavior
        return super().process_request(request)
