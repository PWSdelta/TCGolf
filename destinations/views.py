from django.http import JsonResponse
from .models import Destination, DestinationGuide

# API endpoint to export all Destinations as JSON
def export_destinations(request):
    data = list(Destination.objects.all().values())
    return JsonResponse(data, safe=False)

# API endpoint to export all DestinationGuides as JSON
def export_destination_guides(request):
    data = list(DestinationGuide.objects.all().values())
    return JsonResponse(data, safe=False)
from django.http import HttpResponse
from django.views.decorators.http import require_GET
# Dynamic sitemap.xml endpoint
@require_GET
def dynamic_sitemap_xml(request):
    """Dynamically generate sitemap.xml for search engines."""
    from .models import Destination
    import xml.etree.ElementTree as ET
    urlset = ET.Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    # Homepage
    url = ET.SubElement(urlset, 'url')
    ET.SubElement(url, 'loc').text = 'https://tcgplex.com/'
    ET.SubElement(url, 'changefreq').text = 'daily'
    ET.SubElement(url, 'priority').text = '1.0'

    for destination in Destination.objects.all():
        lang_set = set()
        if destination.article_content_multilang:
            lang_set.update(destination.article_content_multilang.keys())
        if not lang_set:
            lang_set = {'en'} if destination.article_content else set()
        for lang in lang_set:
            slug = destination.generate_slug(language=lang)
            if lang == 'en':
                loc = f'https://tcgplex.com/golf-courses/{slug}/'
            else:
                loc = f'https://tcgplex.com/{lang}/golf-courses/{slug}/'
            url = ET.SubElement(urlset, 'url')
            ET.SubElement(url, 'loc').text = loc
            ET.SubElement(url, 'changefreq').text = 'weekly'
            ET.SubElement(url, 'priority').text = '0.8'

    xml_str = ET.tostring(urlset, encoding='utf-8', method='xml')
    return HttpResponse(xml_str, content_type='application/xml')
from django.shortcuts import redirect
import re
# Redirect old /destination/{lang}-{slug} to new /destination/{lang}/{slug}
def redirect_old_destination_url(request, lang_slug):
    """Redirect /destination/{lang}-{slug} to /destination/{lang}/{slug}"""
    match = re.match(r'^(?P<lang>[a-z]{2,3})-(?P<slug>.+)$', lang_slug)
    if match:
        lang = match.group('lang')
        slug = match.group('slug')
        return redirect(f'/{lang}/golf-courses/{slug}/', permanent=True)
    # If not matching, 404
    raise Http404('Invalid destination URL')
from django.shortcuts import render, get_object_or_404
from django.db import models
from django.db.models import Count
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
    Handles bold headers, bullet points, and markdown tables properly.
    """
    if not text:
        return ""
    
    # Remove template instructions and clean up markers
    text = re.sub(r'---.*\(Continue with.*\).*---', '', text, flags=re.DOTALL)
    text = re.sub(r'\n*---.*---\n*', '\n\n', text)
    text = re.sub(r'\*\*\s*$', '', text)
    text = re.sub(r'\n\s*\*\*\s*\n', '\n\n', text)
    
    # Fix markdown table formatting
    lines = text.split('\n')
    result = []
    table_started = False
    needs_header = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Skip empty lines and lines with just pipes
        if not line or line.strip('| ') == '':
            if not table_started:
                result.append('')
            continue
        
        # Check for table content
        if '|' in line:
            cells = [cell.strip() for cell in line.split('|')]
            if len(cells) < 3:  # Need at least one real column
                continue
                
            # Clean and standardize the row
            cleaned_row = '|' + '|'.join(f' {cell.strip()} ' for cell in cells[1:-1]) + '|'
            
            # Handle start of table
            if not table_started:
                table_started = True
                if 'Month' in line or 'Month'.upper() in line or any(c.isupper() for c in line):
                    # This is a header row
                    result.append(cleaned_row)
                    # Add separator row
                    cols = len(cells) - 2  # subtract first/last empty cells
                    result.append('|' + '|'.join([' --- ' for _ in range(cols)]) + '|')
                else:
                    # Missing header - add it based on context
                    if "Month" in text[:1000]:  # Check if this is a monthly table
                        result.append('| Month | Avg. High (°C) | Avg. Low (°C) | Rainfall (mm) | Playing Conditions |')
                        result.append('| --- | --- | --- | --- | --- |')
                    needs_header = True
                continue
            
            # Skip separator rows if we already added one
            if '---' in line:
                continue
                
            # Add content row
            result.append(cleaned_row)
            continue
        
        # Not a table row
        if table_started:
            table_started = False
            result.append('')  # Add space after table
        
        # Handle regular content
        if line.startswith('#'):
            result.append(line)
        elif re.match(r'^\*\*(\d+\.\s*.+?)\*\*$', line):
            header_text = re.match(r'^\*\*(\d+\.\s*.+?)\*\*$', line).group(1).strip()
            result.append(f"### {header_text}")
        elif line not in ['**', '***', '____', '---']:
            result.append(line)
    
    # Join and clean up
    content = '\n'.join(result)
    content = re.sub(r'\n{3,}', '\n\n', content)  # Remove excessive blank lines
    
    # If content appears truncated, append a note
    if re.search(r'\*\*\s*$', content):
        content += "\n\n---\n\n**Note:** This guide appears to be incomplete. Please check back later for the full content."
    
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
    
    # Only show destinations that have 8 or more languages
    destinations_with_8_plus_languages = destinations.annotate(
        language_count=Count('guides__language_code', distinct=True)
    ).filter(language_count__gte=8)
    
    # Use the filtered destinations
    destinations = destinations_with_8_plus_languages
    
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
        article_html = md.markdown(content, extensions=["tables", "fenced_code", "nl2br"])
        # Add target="_blank" to all links
        article_html = re.sub(r'<a (?![^>]*target=)', '<a target="_blank" ', article_html)
        
        # Add a warning if content seems truncated
        if len(guide.content) < 1000 or guide.content.strip().endswith('**'):
            article_html += '<div class="alert alert-warning mt-4" role="alert"><strong>Note:</strong> This guide appears to be incomplete. Please check back later for the full content.</div>'
        
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


# ============================================
# CITY GUIDE VIEWS
# ============================================

from .models import CityGuide

def city_guide_home(request):
    """City guide listing page (English)"""
    return city_guide_home_lang(request, 'en')

def city_guide_home_lang(request, language='en'):
    """City guide listing page for specific language"""
    city_guides = CityGuide.objects.filter(
        language_code=language,
        is_published=True
    ).select_related('destination').order_by('-is_featured', '-updated_at')
    
    context = {
        'city_guides': city_guides,
        'current_language': language,
        'total_guides': city_guides.count(),
    }
    
    return render(request, 'destinations/city_guide_home.html', context)

def city_guide_detail(request, slug):
    """City guide detail page (English)"""
    return city_guide_detail_lang(request, slug, 'en')

def city_guide_detail_lang(request, slug, language='en'):
    """City guide detail page for specific language"""
    try:
        # Get the city guide
        city_guide = get_object_or_404(
            CityGuide.objects.select_related('destination'),
            slug=slug,
            language_code=language,
            is_published=True
        )
        
        # Get available languages for this destination's city guides
        available_languages = list(
            CityGuide.objects.filter(
                destination=city_guide.destination,
                is_published=True
            ).values_list('language_code', flat=True).distinct()
        )
        
        # Get related golf guide if it exists
        golf_guide = None
        try:
            golf_guide = DestinationGuide.objects.get(
                destination=city_guide.destination,
                language_code=language
            )
        except DestinationGuide.DoesNotExist:
            pass
        
        # Get nearby city guides (same country, different cities)
        nearby_guides = CityGuide.objects.filter(
            destination__country=city_guide.destination.country,
            language_code=language,
            is_published=True
        ).exclude(id=city_guide.id).select_related('destination')[:6]
        
        # Get real-time data for this city with error handling
        realtime_data = {}
        try:
            realtime_service = RealTimeDestinationData()
            realtime_data = realtime_service.get_all_destination_data(
                city_guide.destination.city, 
                city_guide.destination.country
            )
        except Exception as e:
            # Log the error but continue without the realtime data
            import logging
            logging.error(f"Error fetching realtime data for city guide: {e}")
        
        context = {
            'city_guide': city_guide,
            'destination': city_guide.destination,
            'golf_guide': golf_guide,
            'current_language': language,
            'available_languages': available_languages,
            'nearby_guides': nearby_guides,
            'sections_summary': city_guide.get_sections_summary(),
            'reading_time': city_guide.get_reading_time(),
            'realtime_data': realtime_data,
        }
        
        return render(request, 'destinations/city_guide_detail.html', context)
        
    except Exception as e:
        import logging
        logging.error(f"Error in city_guide_detail view: {e}")
        raise Http404('City guide not found')
