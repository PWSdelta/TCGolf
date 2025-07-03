from django.shortcuts import render, get_object_or_404
from django.db import models
from .models import Destination
from django.utils.text import slugify
from django.http import Http404
from django.utils.translation import activate, get_language
from .realtime_service import RealTimeDestinationData
import markdown as md
import re

# Helper to improve content formatting while preserving structure
def improve_content_formatting(text):
    """
    Improve content formatting while preserving the existing structure.
    Handles bold headers and bullet points properly.
    """
    if not text:
        return ""
    
    lines = text.split('\n')
    result = []
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines but preserve spacing
        if not line:
            result.append('')
            continue
        
        # Handle bold numbered headers like **1. The Aberdeen Country Club**
        bold_header_match = re.match(r'^\*\*(\d+\.\s*.+?)\*\*$', line)
        if bold_header_match:
            header_text = bold_header_match.group(1).strip()
            result.append(f"### {header_text}")
            continue
            
        # Regular lines - keep as is
        result.append(line)
    
    # Join and clean up extra whitespace
    content = '\n'.join(result)
    
    # Remove excessive blank lines (more than 2 consecutive)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content

# Home view with search

def home(request, language='en'):
    """Home page with optional language support"""
    # Activate the requested language
    if language != 'en':
        activate(language)
    
    q = request.GET.get('q', '')
    destinations = Destination.objects.all().order_by('name')
    if q:
        destinations = destinations.filter(
            models.Q(name__icontains=q) |
            models.Q(city__icontains=q) |
            models.Q(region_or_state__icontains=q) |
            models.Q(country__icontains=q)
        )
    
    # Filter destinations that have content in the requested language
    if language != 'en':
        destinations = [d for d in destinations if d.has_content_in_language(language)]
    
    # Attach slug for each destination for SEO URLs
    for d in destinations:
        d.slug = d.generate_slug(language)
    
    # Prepare a serializable list for the map
    destinations_json = [
        {
            'id': d.id,
            'name': d.name,
            'city': d.city,
            'region_or_state': d.region_or_state,
            'country': d.country,
            'slug': d.slug,
            'latitude': d.latitude,
            'longitude': d.longitude,
            'absolute_url': d.get_absolute_url(language),
        } for d in destinations
    ]
    
    return render(request, 'destinations/home.html', {
        'destinations': destinations,
        'destinations_json': destinations_json,
        'current_language': language,
        'supported_languages': Destination.SUPPORTED_LANGUAGES,
    })

# Detail view with SEO-friendly slug

def destination_detail(request, slug, language='en'):
    """Detail view with multi-language support"""
    # Activate the requested language
    if language != 'en':
        activate(language)
    
    # Find by slug (recreate slug for each destination)
    for d in Destination.objects.all():
        expected_slug = d.generate_slug(language)
        if slug == expected_slug:
            # Get content in the requested language
            content = d.get_article_content(language)
            
            # If no content in requested language, check if we should redirect to English
            if not content.strip() and language != 'en':
                content = d.get_article_content('en')
                if not content.strip():
                    raise Http404('No content available for this destination')
            
            # Preprocess article_content with improved formatting
            content = improve_content_formatting(content)
            article_html = md.markdown(content, extensions=["tables"])
            # Add target="_blank" to all links
            article_html = re.sub(r'<a (?![^>]*target=)', '<a target="_blank" ', article_html)
            
            # Get related destinations for recommendations
            all_destinations = list(Destination.objects.exclude(id=d.id))
            
            # Filter to only show destinations with content in the current language
            if language != 'en':
                all_destinations = [dest for dest in all_destinations 
                                  if dest.has_content_in_language(language)]
            
            # Get destinations from same region/state (up to 3)
            nearby_destinations = [dest for dest in all_destinations 
                                 if dest.region_or_state == d.region_or_state and dest.country == d.country][:3]
            
            # Get destinations from same country (up to 3, excluding nearby ones)
            same_country = [dest for dest in all_destinations 
                          if dest.country == d.country and dest not in nearby_destinations][:3]
            
            # Get popular destinations (weighted random selection favoring different countries, up to 6)
            import random
            
            # Group by country for diverse selection
            destinations_by_country = {}
            for dest in all_destinations:
                country = dest.country
                if country not in destinations_by_country:
                    destinations_by_country[country] = []
                destinations_by_country[country].append(dest)
            
            # Select diverse popular destinations
            popular_destinations = []
            countries = list(destinations_by_country.keys())
            random.shuffle(countries)
            
            # Try to get at least one from each country, up to 6 total
            for country in countries[:6]:
                if len(popular_destinations) < 6 and destinations_by_country[country]:
                    popular_destinations.append(random.choice(destinations_by_country[country]))
            
            # Fill remaining slots if we have less than 6
            remaining_dests = [d for d in all_destinations if d not in popular_destinations]
            while len(popular_destinations) < 6 and remaining_dests:
                popular_destinations.append(remaining_dests.pop(random.randint(0, len(remaining_dests)-1)))
            
            # Add slugs to related destinations
            for dest in nearby_destinations + same_country + popular_destinations:
                dest.slug = dest.generate_slug(language)
            
            # Get real-time data for this destination
            realtime_service = RealTimeDestinationData()
            realtime_data = realtime_service.get_all_destination_data(d.city, d.country)
            
            return render(request, 'destinations/destination_detail.html', {
                'destination': d,
                'article_html': article_html,
                'nearby_destinations': nearby_destinations,
                'same_country_destinations': same_country,
                'popular_destinations': popular_destinations,
                'current_language': language,
                'supported_languages': Destination.SUPPORTED_LANGUAGES,
                'available_languages': d.get_available_languages(),
                'realtime_data': realtime_data,
            })
    raise Http404('Destination not found')
