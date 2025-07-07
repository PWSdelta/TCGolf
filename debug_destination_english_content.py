import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'golfplex.settings')
django.setup()

from destinations.models import Destination, DestinationGuide

def debug_english_content():
    for dest in Destination.objects.all():
        has_guide = DestinationGuide.objects.filter(destination=dest, language_code='en').exists()
        acm = dest.article_content_multilang if hasattr(dest, 'article_content_multilang') else None
        ac = dest.article_content if hasattr(dest, 'article_content') else None
        acm_en = acm.get('en') if acm and isinstance(acm, dict) else None
        print(f"ID: {dest.id} | Name: {dest.name}")
        print(f"  Has DestinationGuide (en): {has_guide}")
        print(f"  article_content_multilang['en']: {repr(acm_en)[:100]}")
        print(f"  article_content: {repr(ac)[:100]}")
        print('-' * 60)

if __name__ == "__main__":
    debug_english_content()
