import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'golfplex.settings')
django.setup()

from destinations.models import Destination, DestinationGuide
from django.db import transaction

created = 0
skipped = 0
missing = []

def create_missing_english_guides():
    global created, skipped
    for dest in Destination.objects.all():
        has_guide = DestinationGuide.objects.filter(destination=dest, language_code='en').exists()
        if has_guide:
            skipped += 1
            continue
        # Try to get English content
        en_content = None
        if dest.article_content_multilang and isinstance(dest.article_content_multilang, dict):
            en_content = dest.article_content_multilang.get('en')
        if not en_content and dest.article_content:
            en_content = dest.article_content
        if en_content and en_content.strip():
            DestinationGuide.objects.create(
                destination=dest,
                language_code='en',
                content=en_content,
                title=dest.name,
                slug='',  # Will be auto-generated
            )
            created += 1
            print(f"[CREATE] English guide for destination id={dest.id} ({dest.name})")
        else:
            missing.append(dest.id)
            print(f"[MISSING] No English content for destination id={dest.id} ({dest.name})")

if __name__ == "__main__":
    with transaction.atomic():
        create_missing_english_guides()
    print(f"\nDone. Created: {created}, Skipped (already exists): {skipped}, Missing content: {len(missing)}")
