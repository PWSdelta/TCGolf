"""
Content Generation API Views for GolfPlex

Endpoints for distributed content generation:
1. /api/fetch-work/ - Get next destination to process
2. /api/submit-work/ - Submit completed content in multiple languages
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.db import models
import json
import logging
from datetime import datetime, timezone
from .models import Destination, DestinationGuide

logger = logging.getLogger(__name__)

# Country code to flag emoji mapping for UI enhancement
COUNTRY_FLAGS = {
    'United States': '🇺🇸',
    'USA': '🇺🇸',  # Alternative name
    'US': '🇺🇸',   # Alternative name
    'Canada': '🇨🇦',
    'United Kingdom': '🇬🇧',
    'UK': '🇬🇧',   # Alternative name
    'Ireland': '🇮🇪',
    'Scotland': '🏴',
    'Spain': '🇪🇸',
    'France': '🇫🇷',
    'Germany': '🇩🇪',
    'Italy': '🇮🇹',
    'Portugal': '🇵🇹',
    'Netherlands': '🇳🇱',
    'Switzerland': '🇨🇭',
    'Austria': '🇦🇹',
    'Denmark': '🇩🇰',
    'Sweden': '🇸🇪',
    'Norway': '🇳🇴',
    'Japan': '🇯🇵',
    'South Korea': '🇰🇷',
    'China': '🇨🇳',
    'Australia': '🇦🇺',
    'New Zealand': '🇳🇿',
    'South Africa': '🇿🇦',
    'UAE': '🇦🇪',
    'United Arab Emirates': '🇦🇪',  # Alternative name
    'Thailand': '🇹🇭',
    'Malaysia': '🇲🇾',
    'Singapore': '🇸🇬',
    'Mexico': '🇲🇽',
    'Brazil': '🇧🇷',
    'Argentina': '🇦🇷',
    'Chile': '🇨🇱',
    'Turkey': '🇹🇷',
    'Morocco': '🇲🇦',
    'Egypt': '🇪🇬',
    'India': '🇮🇳',
    'Saudi Arabia': '🇸🇦',
    'Ghana': '🇬🇭',
    'Côte d\'Ivoire': '🇨🇮',
}

# Target languages for content generation
TARGET_LANGUAGES = {
    'es': 'Spanish',      # Huge international golf markets
    'fr': 'French',       # Europe + parts of Africa  
    'de': 'German',       # Big traveling golfer market
    'it': 'Italian',      # Domestic golf, inbound travelers
    'pt': 'Portuguese',   # Portugal, Brazil
    'nl': 'Dutch',        # Niche but high-value travelers
    'ja': 'Japanese',     # Premium golf tourists
    'ko': 'Korean',       # Very active international golfers
    'zh': 'Chinese',      # Both mainland + Taiwan markets
    'ar': 'Arabic',       # Middle East golf destinations
}

@method_decorator(csrf_exempt, name='dispatch')
class FetchWorkView(View):
    """
    Returns a single (destination, language) work unit for content generation
    Prioritizes destinations without any guides, then those missing language versions
    """
    
    def get(self, request):
        try:
            # Find the next (destination, language) pair to work on
            destination = None
            target_language = None
            priority = None
            
            # Priority 1: Destinations with no guides at all (start with English)
            destinations_without_guides = Destination.objects.filter(
                guides__isnull=True
            ).order_by('?')  # Random order
            
            if destinations_without_guides.exists():
                destination = destinations_without_guides.first()
                target_language = 'en'  # Always start with English
                priority = 'no_guides'
            else:
                # Priority 2: Destinations missing language versions
                destinations_with_guides = Destination.objects.filter(
                    guides__isnull=False
                ).prefetch_related('guides').order_by('?')
                
                for dest in destinations_with_guides:
                    existing_languages = set(dest.guides.values_list('language_code', flat=True))
                    all_languages = {'en'} | set(TARGET_LANGUAGES.keys())
                    missing = list(all_languages - existing_languages)
                    
                    if missing:
                        destination = dest
                        # Prioritize English if missing, otherwise pick first missing language
                        target_language = 'en' if 'en' in missing else missing[0]
                        priority = 'missing_languages'
                        break
                
                if not destination:
                    return JsonResponse({
                        'status': 'no_work',
                        'message': 'All destinations have complete content in all languages'
                    })
            
            # Get existing guides for context (for translation or reference)
            existing_guides = {}
            if destination.guides.exists():
                for guide in destination.guides.all():
                    existing_guides[guide.language_code] = {
                        'content': guide.content,
                        'created_at': guide.created_at.isoformat(),
                        'updated_at': guide.updated_at.isoformat()
                    }
            
            # Prepare the single work unit
            work_data = {
                'status': 'work_available',
                'priority': priority,
                'destination': {
                    'id': destination.id,
                    'name': destination.name,
                    'city': destination.city,
                    'region_or_state': destination.region_or_state,
                    'country': destination.country,
                    'description': destination.description,
                    'latitude': float(destination.latitude),
                    'longitude': float(destination.longitude),
                    'slug': destination.generate_slug(),
                },
                'target_language': target_language,
                'language_name': TARGET_LANGUAGES.get(target_language, 'English'),
                'existing_guides': existing_guides,
                'is_translation': target_language != 'en' and 'en' in existing_guides,
                'work_requirements': {
                    'min_words': 2500 if target_language == 'en' else 2000,
                    'include_local_insights': True,
                    'include_seasonal_info': True,
                    'include_course_recommendations': True
                }
            }
            
            logger.info(f"Fetched work unit: {destination.city}, {destination.country} ({target_language})")
            return JsonResponse(work_data)
            
        except Exception as e:
            logger.error(f"Error fetching work: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error fetching work: {str(e)}'
            }, status=500)
    

@method_decorator(csrf_exempt, name='dispatch')
class SubmitWorkView(View):
    """
    Accepts completed content generation work in two formats:
    1. Atomic: single (destination, language) pair
       {destination_id, language_code, content}
    2. Legacy: bulk format with multiple guides
       {destination_id, guides: {lang: {content}}}
    """
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            destination_id = data.get('destination_id')
            if not destination_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'destination_id is required'
                }, status=400)
                
            # Try atomic format first
            language_code = data.get('language_code')
            content = data.get('content', '')
            worker_info = data.get('worker_info', {})
            
            # If no language_code, try legacy format
            if not language_code:
                guides = data.get('guides', {})
                if not guides:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Either language_code+content or guides is required'
                    }, status=400)
                    
                results = {
                    'created_guides': [],
                    'updated_guides': [],
                    'errors': []
                }
                
                # Process each guide in legacy format
                for lang, guide_data in guides.items():
                    try:
                        guide_content = guide_data.get('content', '')
                        if len(guide_content.strip()) < 1000:
                            results['errors'].append(f'Content too short for {lang}')
                            continue
                            
                        guide, created = DestinationGuide.objects.update_or_create(
                            destination_id=destination_id,
                            language_code=lang,
                            defaults={
                                'content': guide_content,
                                'updated_at': datetime.now(timezone.utc)
                            }
                        )
                        
                        if created:
                            results['created_guides'].append(lang)
                        else:
                            results['updated_guides'].append(lang)
                            
                    except Exception as e:
                        results['errors'].append(f'Error processing {lang}: {str(e)}')
                
                return JsonResponse({
                    'status': 'success',
                    'results': results,
                    'worker_info': worker_info
                })
            
            # Handle atomic format (single language)
            if language_code and content:
                if len(content.strip()) < 1000:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Content is too short (minimum 1000 characters, got {len(content.strip())})'
                    }, status=400)
                
                try:
                    destination = Destination.objects.get(id=destination_id)
                    
                    # Create or update guide
                    guide, created = DestinationGuide.objects.update_or_create(
                        destination=destination,
                        language_code=language_code,
                        defaults={
                            'content': content,
                            'updated_at': datetime.now(timezone.utc)
                        }
                    )
                    
                    action = 'created' if created else 'updated'
                    language_name = TARGET_LANGUAGES.get(language_code, 'English')
                    
                    response_data = {
                        'status': 'success',
                        'destination': {
                            'id': destination.id,
                            'city': destination.city,
                            'country': destination.country
                        },
                        'guide': {
                            'language_code': language_code,
                            'language_name': language_name,
                            'action': action,
                            'content_length': len(content),
                            'created_at': guide.created_at.isoformat(),
                            'updated_at': guide.updated_at.isoformat()
                        },
                        'worker_info': worker_info
                    }
                    
                    logger.info(f"Submitted work for {destination.city}, {destination.country} ({language_code}): {action}")
                    return JsonResponse(response_data)
                    
                except Destination.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Destination {destination_id} not found'
                    }, status=404)
            
        except Destination.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Destination not found'
            }, status=404)
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Error submitting work: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error submitting work: {str(e)}'
            }, status=500)


@require_http_methods(["GET"])
def work_status(request):
    """
    Returns overall status of content generation work
    """
    try:
        total_destinations = Destination.objects.count()
        destinations_with_guides = Destination.objects.filter(
            guides__isnull=False
        ).distinct().count()
        destinations_without_guides = total_destinations - destinations_with_guides
        
        # Count guides by language
        language_stats = {}
        for lang_code, lang_name in [('en', 'English')] + list(TARGET_LANGUAGES.items()):
            count = DestinationGuide.objects.filter(language_code=lang_code).count()
            language_stats[lang_code] = {
                'name': lang_name,
                'count': count,
                'percentage': round((count / total_destinations) * 100, 1) if total_destinations > 0 else 0
            }
        
        # Calculate completion percentage
        total_possible_guides = total_destinations * (len(TARGET_LANGUAGES) + 1)  # +1 for English
        total_existing_guides = DestinationGuide.objects.count()
        completion_percentage = round((total_existing_guides / total_possible_guides) * 100, 1) if total_possible_guides > 0 else 0
        
        status_data = {
            'overview': {
                'total_destinations': total_destinations,
                'destinations_with_guides': destinations_with_guides,
                'destinations_without_guides': destinations_without_guides,
                'total_guides': total_existing_guides,
                'completion_percentage': completion_percentage
            },
            'language_stats': language_stats,
            'target_languages': TARGET_LANGUAGES,
            'next_priorities': {
                'no_guides': destinations_without_guides,
                'missing_translations': destinations_with_guides  # Simplified
            }
        }
        
        return JsonResponse(status_data)
        
    except Exception as e:
        logger.error(f"Error getting work status: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error getting work status: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def typeahead_search(request):
    """
    Typeahead search API for autocomplete functionality
    Returns destinations matching search query with country flags
    """
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return JsonResponse({
            'results': [],
            'message': 'Please enter at least 2 characters'
        })
    
    # Search destinations by name, city, region, or country
    destinations = Destination.objects.filter(
        models.Q(name__icontains=query) |
        models.Q(city__icontains=query) |
        models.Q(region_or_state__icontains=query) |
        models.Q(country__icontains=query)
    ).filter(guides__isnull=False).distinct().order_by('name')[:10]  # Limit to 10 results
    
    results = []
    for dest in destinations:
        # Get country flag emoji
        flag = COUNTRY_FLAGS.get(dest.country, '🌍')  # Default globe emoji
        
        results.append({
            'id': dest.id,
            'name': dest.name,
            'city': dest.city,
            'region_or_state': dest.region_or_state,
            'country': dest.country,
            'country_flag': flag,
            'display_text': f"{dest.name}, {dest.city}",
            'location_text': f"{dest.city}, {dest.region_or_state}, {dest.country}",
            'url': dest.get_absolute_url(),
        })
    
    return JsonResponse({
        'results': results,
        'count': len(results)
    })
