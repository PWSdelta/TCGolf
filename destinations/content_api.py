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
    Returns destination data for content generation work
    Prioritizes destinations without any guides, then those missing language versions
    """
    
    def get(self, request):
        try:
            # Priority 1: Destinations with no guides at all
            destinations_without_guides = Destination.objects.filter(
                guides__isnull=True
            ).order_by('?')  # Random order
            
            if destinations_without_guides.exists():
                destination = destinations_without_guides.first()
                missing_languages = ['en'] + list(TARGET_LANGUAGES.keys())
                priority = 'no_guides'
            else:
                # Priority 2: Destinations missing language versions
                destinations_with_guides = Destination.objects.filter(
                    guides__isnull=False
                ).prefetch_related('guides').order_by('?')
                
                destination = None
                missing_languages = []
                
                for dest in destinations_with_guides:
                    existing_languages = set(dest.guides.values_list('language_code', flat=True))
                    all_languages = {'en'} | set(TARGET_LANGUAGES.keys())
                    missing = list(all_languages - existing_languages)
                    
                    if missing:
                        destination = dest
                        missing_languages = missing
                        priority = 'missing_languages'
                        break
                
                if not destination:
                    return JsonResponse({
                        'status': 'no_work',
                        'message': 'All destinations have complete content in all languages'
                    })
            
            # Get existing guides for context
            existing_guides = {}
            if destination.guides.exists():
                for guide in destination.guides.all():
                    existing_guides[guide.language_code] = {
                        'content': guide.content,
                        'created_at': guide.created_at.isoformat(),
                        'updated_at': guide.updated_at.isoformat()
                    }
            
            # Suggest primary language based on country
            primary_language = self.get_primary_language(destination.country)
            
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
                'missing_languages': missing_languages,
                'suggested_primary_language': primary_language,
                'existing_guides': existing_guides,
                'target_languages': TARGET_LANGUAGES,
                'work_requirements': {
                    'english_guide_min_words': 2500,
                    'translated_guide_min_words': 2000,
                    'include_local_insights': True,
                    'include_seasonal_info': True,
                    'include_course_recommendations': True
                }
            }
            
            logger.info(f"Fetched work for destination: {destination.city}, {destination.country}")
            return JsonResponse(work_data)
            
        except Exception as e:
            logger.error(f"Error fetching work: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error fetching work: {str(e)}'
            }, status=500)
    
    def get_primary_language(self, country):
        """Suggest primary language based on country"""
        country_language_map = {
            'Spain': 'es',
            'Mexico': 'es',
            'Argentina': 'es',
            'Chile': 'es',
            'Colombia': 'es',
            'Uruguay': 'es',
            'France': 'fr',
            'Germany': 'de',
            'Austria': 'de',
            'Switzerland': 'de',
            'Italy': 'it',
            'Portugal': 'pt',
            'Brazil': 'pt',
            'Netherlands': 'nl',
            'Japan': 'ja',
            'South Korea': 'ko',
            'China': 'zh',
            'Saudi Arabia': 'ar',
            'United Arab Emirates': 'ar',
            'Qatar': 'ar',
            'Oman': 'ar',
            'Bahrain': 'ar',
            'Kuwait': 'ar',
            'Jordan': 'ar',
            'Lebanon': 'ar',
        }
        return country_language_map.get(country, 'en')


@method_decorator(csrf_exempt, name='dispatch')
class SubmitWorkView(View):
    """
    Accepts completed content generation work
    Expects JSON with destination_id and guides in multiple languages
    """
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            destination_id = data.get('destination_id')
            guides = data.get('guides', {})
            worker_info = data.get('worker_info', {})
            
            if not destination_id or not guides:
                return JsonResponse({
                    'status': 'error',
                    'message': 'destination_id and guides are required'
                }, status=400)
            
            destination = Destination.objects.get(id=destination_id)
            
            created_guides = []
            updated_guides = []
            errors = []
            
            for language, guide_data in guides.items():
                try:
                    content = guide_data.get('content', '')
                    if not content or len(content.strip()) < 1000:
                        errors.append(f"Content for {language} is too short (minimum 1000 characters)")
                        continue
                    
                    # Create or update guide
                    guide, created = DestinationGuide.objects.update_or_create(
                        destination=destination,
                        language_code=language,
                        defaults={
                            'content': content,
                            'updated_at': datetime.now(timezone.utc)
                        }
                    )
                    
                    if created:
                        created_guides.append(language)
                    else:
                        updated_guides.append(language)
                        
                except Exception as e:
                    errors.append(f"Error processing {language}: {str(e)}")
            
            response_data = {
                'status': 'success',
                'destination': {
                    'id': destination.id,
                    'city': destination.city,
                    'country': destination.country
                },
                'results': {
                    'created_guides': created_guides,
                    'updated_guides': updated_guides,
                    'total_processed': len(created_guides) + len(updated_guides),
                    'errors': errors
                },
                'worker_info': worker_info
            }
            
            logger.info(f"Submitted work for {destination.city}, {destination.country}: "
                       f"{len(created_guides)} created, {len(updated_guides)} updated")
            
            return JsonResponse(response_data)
            
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
