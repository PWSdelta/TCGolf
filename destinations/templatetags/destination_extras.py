from django import template
from django.urls import reverse
import random
import hashlib

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """
    Template filter to look up a value in a dictionary by key.
    Usage: {{ mydict|lookup:mykey }}
    """
    if dictionary and key in dictionary:
        return dictionary[key]
    return None

@register.simple_tag
def language_url(destination, language_code):
    """
    Generate URL for destination in specific language
    """
    try:
        if language_code == 'en':
            return destination.get_absolute_url()
        else:
            slug = destination.generate_slug(language_code)
            return reverse('destination_detail_lang', kwargs={
                'language': language_code, 
                'slug': slug
            })
    except:
        # Fallback if URL reverse fails
        if language_code == 'en':
            return f"/golf-courses/{destination.generate_slug()}/"
        else:
            return f"/{language_code}/golf-courses/{destination.generate_slug(language_code)}/"

@register.filter  
def language_name(language_code):
    """
    Get native language name for language code
    """
    names = {
        'en': 'Read in English',
        'de': 'Auf Deutsch lesen',
        'es': 'Leer en español', 
        'fr': 'Lire en français',
        'it': 'Leggi in italiano',
        'pt': 'Ler em português',
        'ja': '日本語で読む',
        'ko': '한국어로 읽기',
        'zh': '中文阅读'
    }
    return names.get(language_code, f'Read in {language_code.upper()}')

@register.filter
def personalized_hero_text(destination):
    """
    Generate personalized hero text for each destination
    """
    
    # Use destination info to create a consistent seed
    seed = f"{destination.city}{destination.country}".lower()
    hash_object = hashlib.md5(seed.encode())
    random.seed(int(hash_object.hexdigest()[:8], 16))
    
    country = destination.country
    city = destination.city
    
    # Different text patterns for variety
    patterns = [
        f"Discover world-class golf courses in {country} and plan your perfect getaway",
        f"Traveling to {country}? Don't miss these incredible golf destinations",
        f"Experience the finest golf courses {city} has to offer",
        f"Explore premium golf experiences in {country}",
        f"Your guide to exceptional golf in {city}, {country}",
        f"Uncover hidden golf gems in {country}",
        f"Plan your ultimate golf adventure in {city}",
        f"Golf enthusiasts: {country} awaits your next round",
        f"From local favorites to championship courses in {country}",
        f"Tee off in paradise: {city}'s best golf destinations"
    ]
    
    # Select pattern based on consistent hash
    return random.choice(patterns)
