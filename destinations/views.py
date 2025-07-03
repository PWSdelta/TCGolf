from django.shortcuts import render, get_object_or_404
from django.db import models
from .models import Destination, DestinationGuide
from django.utils.text import slugify
from django.http import Http404
from django.utils.translation import activate, get_language
from .realtime_service import RealTimeDestinationData
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
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
    in_numbered_list = False
    current_list_content = []
    
    for line in lines:
        original_line = line
        line = line.strip()
        
        # Skip empty lines but preserve spacing
        if not line:
            # If we were in a numbered list, close it first
            if in_numbered_list and current_list_content:
                # Join the content and add as one list item
                list_item_content = ' '.join(current_list_content)
                result.append(list_item_content)
                current_list_content = []
                in_numbered_list = False
            result.append('')
            continue
        
        # Handle bold numbered headers like **1. The Aberdeen Country Club**
        bold_header_match = re.match(r'^\*\*(\d+\.\s*.+?)\*\*$', line)
        if bold_header_match:
            # Close any pending numbered list
            if in_numbered_list and current_list_content:
                list_item_content = ' '.join(current_list_content)
                result.append(list_item_content)
                current_list_content = []
                in_numbered_list = False
            
            header_text = bold_header_match.group(1).strip()
            result.append(f"### {header_text}")
            continue
        
        # Check if we're starting a numbered list item
        numbered_item_match = re.match(r'^(\d+\.)\s*(.+)', line)
        if numbered_item_match:
            # Close previous list item if we were in one
            if in_numbered_list and current_list_content:
                list_item_content = ' '.join(current_list_content)
                result.append(list_item_content)
                current_list_content = []
            
            # Start new list item
            in_numbered_list = True
            number = numbered_item_match.group(1)
            content = numbered_item_match.group(2)
            current_list_content = [f"{number} {content}"]
            continue
        
        # Handle content that belongs to a numbered list item
        if in_numbered_list:
            # If it's a bullet point, convert it to plain text
            if line.startswith('*'):
                bullet_content = line[1:].strip()  # Remove the * and trim
                current_list_content.append(bullet_content)
            else:
                # Regular content belonging to the list item
                current_list_content.append(line)
            continue
        
        # Regular lines - keep as is
        result.append(original_line)
    
    # Handle any remaining numbered list content
    if in_numbered_list and current_list_content:
        list_item_content = ' '.join(current_list_content)
        result.append(list_item_content)
    
    # Join and clean up extra whitespace
    content = '\n'.join(result)
    
    # Remove excessive blank lines (more than 2 consecutive)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content

# Home view with search
@cache_page(60 * 15)  # Cache for 15 minutes
@vary_on_headers('Accept-Language')  # Vary cache by language headers
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
        destinations = destinations.filter(guides__language_code=language).distinct()
    else:
        # For English, show all destinations with any guides
        destinations = destinations.filter(guides__isnull=False).distinct()
    
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
    
    # Get available languages across all destinations
    available_languages = list(DestinationGuide.objects.values_list('language_code', flat=True).distinct())
    
    return render(request, 'destinations/home.html', {
        'destinations': destinations,
        'destinations_json': destinations_json,
        'current_language': language,
        'available_languages': available_languages,
    })

# Detail view with SEO-friendly slug

def destination_detail(request, slug, language='en'):
    """Detail view with multi-language support using DestinationGuide model"""
    # Activate the requested language
    if language != 'en':
        activate(language)
    
    # Find destination by matching slug pattern
    destination = None
    guide = None
    
    try:
        # Try to find guide by exact slug match first
        try:
            guide = DestinationGuide.objects.select_related('destination').get(
                slug=slug, 
                language_code=language
            )
            destination = guide.destination
        except DestinationGuide.DoesNotExist:
            # If no exact match, try to find by destination and language
            for d in Destination.objects.prefetch_related('guides'):
                expected_slug = d.generate_slug(language)
                if slug == expected_slug:
                    destination = d
                    try:
                        guide = d.guides.get(language_code=language)
                    except DestinationGuide.DoesNotExist:
                        # Try English as fallback
                        if language != 'en':
                            try:
                                guide = d.guides.get(language_code='en')
                            except DestinationGuide.DoesNotExist:
                                pass
                    break
        
        if not destination:
            raise Http404('Destination not found')
        
        if not guide:
            raise Http404('No content available for this destination in the requested language')
        
        # Process the content
        content = improve_content_formatting(guide.content)
        article_html = md.markdown(content, extensions=["tables"])
        # Add target="_blank" to all links
        article_html = re.sub(r'<a (?![^>]*target=)', '<a target="_blank" ', article_html)
        
        # Get available languages for this destination
        available_languages = list(
            destination.guides.values_list('language_code', flat=True).distinct()
        )
        
        # Get related destinations for recommendations
        all_destinations = list(
            Destination.objects.filter(guides__language_code=language)
            .exclude(id=destination.id)
            .distinct()
        )
        
        # Get destinations from same region/state (up to 3)
        nearby_destinations = [dest for dest in all_destinations 
                             if dest.region_or_state == destination.region_or_state 
                             and dest.country == destination.country][:3]
        
        # Get destinations from same country (up to 3, excluding nearby ones)
        same_country = [dest for dest in all_destinations 
                      if dest.country == destination.country 
                      and dest not in nearby_destinations][:3]
        
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
        
        # Get real-time data for this destination with error handling
        realtime_data = {}
        try:
            realtime_service = RealTimeDestinationData()
            realtime_data = realtime_service.get_all_destination_data(destination.city, destination.country)
        except Exception as e:
            # Log the error but continue without the realtime data
            import logging
            logging.error(f"Error fetching realtime data: {e}")
        
        return render(request, 'destinations/destination_detail.html', {
            'destination': destination,
            'guide': guide,
            'article_html': article_html,
            'nearby_destinations': nearby_destinations,
            'same_country_destinations': same_country,
            'popular_destinations': popular_destinations,
            'current_language': language,
            'available_languages': available_languages,
            'realtime_data': realtime_data,
        })
    except Exception as e:
        # Log any unexpected errors but handle them gracefully
        import logging
        logging.error(f"Error in destination_detail view: {e}")
        raise Http404('Unable to load destination details')
